import { Hono } from 'hono';
import { getCookie, setCookie } from 'hono/cookie';
import type { Context } from 'hono';
import { initialState, snapshot, addCrew, assignWatch, scenario, acknowledge, addSite, type State } from './domain';

export interface Bindings { DB:D1Database; ASSETS:Fetcher; EXACLIM_MODE:string }
type User={id:string;email:string;name:string;site_ids:string[]};
type Env={Bindings:Bindings};
const app=new Hono<Env>();
const COOKIE='exaclim_supervisor', ROUNDS=100000;
class APIError extends Error { constructor(public status:number,public code:string,message:string){super(message);} }
const fail=(status:number,code:string,message:string):never=>{throw new APIError(status,code,message);};
const hex=(bytes:ArrayBuffer|Uint8Array)=>Array.from(new Uint8Array(bytes instanceof Uint8Array?bytes.buffer as ArrayBuffer:bytes),x=>x.toString(16).padStart(2,'0')).join('');
const random=()=>hex(crypto.getRandomValues(new Uint8Array(32)));
const digest=async(value:string)=>hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)));
async function passwordHash(password:string,salt:string,rounds=ROUNDS) {
  const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(password),'PBKDF2',false,['deriveBits']);
  return hex(await crypto.subtle.deriveBits({name:'PBKDF2',hash:'SHA-256',salt:new TextEncoder().encode(salt),iterations:rounds},key,256));
}
const schema=[
 'CREATE TABLE IF NOT EXISTS dashboard_state (id INTEGER PRIMARY KEY CHECK(id=1), document TEXT NOT NULL CHECK(json_valid(document)), revision INTEGER NOT NULL DEFAULT 0)',
 'CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY,email TEXT NOT NULL UNIQUE,name TEXT NOT NULL,salt TEXT NOT NULL,password_hash TEXT NOT NULL,password_rounds INTEGER NOT NULL)',
 'CREATE TABLE IF NOT EXISTS user_sites (user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,site_id TEXT NOT NULL,PRIMARY KEY(user_id,site_id))',
 'CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,created_at TEXT NOT NULL,expires_at TEXT NOT NULL)',
 'CREATE INDEX IF NOT EXISTS session_expiry ON sessions(expires_at)',
 'CREATE TABLE IF NOT EXISTS login_attempts (key_hash TEXT PRIMARY KEY,count INTEGER NOT NULL,expires_at TEXT NOT NULL)',
];
const bootstraps=new WeakMap<D1Database,Promise<void>>();
async function bootstrap(db:D1Database) {
 let pending=bootstraps.get(db);
 if(!pending){pending=(async()=>{
  await db.batch(schema.map(sql=>db.prepare(sql)));
  const exists=await db.prepare('SELECT id FROM users WHERE id=?').bind('demo-supervisor').first();
  if(!exists){const salt=random(),hash=await passwordHash('Exaclim2026!',salt);await db.prepare('INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?)').bind('demo-supervisor','demo@exaclim.test','Demo supervisor',salt,hash,ROUNDS).run();}
  await db.batch([
   db.prepare('INSERT OR IGNORE INTO dashboard_state(id,document,revision) VALUES(1,?,0)').bind(JSON.stringify(initialState())),
   ...['accra','tema'].map(id=>db.prepare('INSERT OR IGNORE INTO user_sites VALUES(?,?)').bind('demo-supervisor',id)),
  ]);
 })();bootstraps.set(db,pending);}
 try{await pending;}catch(error){bootstraps.delete(db);throw error;}
}
async function load(db:D1Database){const row=await db.prepare('SELECT document,revision FROM dashboard_state WHERE id=1').first<{document:string;revision:number}>();if(!row)throw new Error('State unavailable');return {state:JSON.parse(row.document) as State,revision:row.revision};}
async function update<T>(db:D1Database,mutate:(state:State)=>T):Promise<T>{
 for(let attempt=0;attempt<12;attempt++){const {state,revision}=await load(db),result=mutate(state);const saved=await db.prepare('UPDATE dashboard_state SET document=?,revision=revision+1 WHERE id=1 AND revision=?').bind(JSON.stringify(state),revision).run();if(saved.meta.changes===1)return result;}
 return fail(409,'state_busy','Another change is being saved. Try again.');
}
async function user(c:Context<Env>,siteId?:string):Promise<User>{
 const token=getCookie(c,COOKIE);if(!token||token.length>512)return fail(401,'unauthenticated','Sign in to the synthetic supervisor demo.');
 const row=await c.env.DB.prepare('SELECT u.id,u.email,u.name FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?').bind(await digest(token),new Date().toISOString()).first<{id:string;email:string;name:string}>();
 if(!row)return fail(401,'unauthenticated','Sign in to the synthetic supervisor demo.');
 const sites=await c.env.DB.prepare('SELECT site_id FROM user_sites WHERE user_id=? ORDER BY site_id').bind(row.id).all<{site_id:string}>();
 const result={...row,site_ids:sites.results.map(s=>s.site_id)};
 if(siteId&&!result.site_ids.includes(siteId))return fail(403,'site_forbidden','This supervisor cannot access the requested site.');
 return result;
}
async function body(c:Context<Env>,allowed:string[]):Promise<Record<string,unknown>>{
 if(c.req.header('Content-Type')?.split(';')[0]!=='application/json')return fail(415,'content_type','Use application/json.');
 const reader=c.req.raw.body?.getReader();if(!reader)return fail(400,'invalid_json','Provide a bounded JSON object with finite values.');
 const chunks:Uint8Array[]=[];let length=0;
 while(true){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;if(length>16384){await reader.cancel();return fail(400,'invalid_json','Provide a bounded JSON object with finite values.');}chunks.push(value);}
 const data=new Uint8Array(length);let offset=0;for(const chunk of chunks){data.set(chunk,offset);offset+=chunk.byteLength;}
 let parsed:unknown;try{parsed=JSON.parse(new TextDecoder('utf-8',{fatal:true,ignoreBOM:false}).decode(data));}catch{return fail(400,'invalid_json','Provide a bounded JSON object with finite values.');}
 if(!parsed||typeof parsed!=='object'||Array.isArray(parsed))return fail(400,'invalid_json','Provide a JSON object.');
 if(Object.keys(parsed).some(k=>!allowed.includes(k)))return fail(422,'unsupported_fields','Unsupported fields; personal watch profiles are not accepted.');
 return parsed as Record<string,unknown>;
}
function site(state:State,id:string){return state.sites[id]??fail(404,'site_not_found','Site not found.');}
const summary=(s:State['sites'][string])=>({id:s.id,name:s.name,latitude:s.latitude,longitude:s.longitude,timezone:s.timezone});
function dashboard(state:State,id:string,u:User){
 const raw=snapshot(state,id);
 // Public adapter matches the existing browser/Python API; no routine individual data.
 const forecast={...raw.forecast,status:'synthetic',fetched_at:raw.forecast.generated_at,days:raw.forecast.days.map(day=>({...day,windows:day.windows.map(w=>({...w,level:'red',label:'High-risk scenario window'})),hours:day.hours.map(h=>({...h,time:h.start,hour:h.local_time,level:raw.forecast.stale?'amber':h.risk,quality:h.data_quality}))}))};
 return {...raw,mode:'synthetic-demo',source:'Synthetic watches, shared-phone gateway and weather scenario',updated_at:raw.generated_at,sites:Object.values(state.sites).filter(s=>u.site_ids.includes(s.id)).map(summary),forecast,groups:raw.groups.map(g=>({...g,suggestion:raw.suggestions.find(s=>s.group_id===g.id),counts:g.counts?{...g.counts,unknown:g.unknown_contributors}:null})),emergencies:raw.emergencies.map(e=>({...e,acknowledged:!!e.acknowledged_at}))};
}
app.use('*',async(c,next)=>{
 c.header('X-Content-Type-Options','nosniff');c.header('Referrer-Policy','no-referrer');
 if(c.req.path.startsWith('/api/'))c.header('Cache-Control','private, no-store');
 if(c.env.EXACLIM_MODE!=='demo')return c.json({error:'This build only supports synthetic demo mode.',code:'demo_only'},503);
 if(!['GET','HEAD','OPTIONS'].includes(c.req.method)){
  const origin=c.req.header('Origin');if(origin&&origin!==new URL(c.req.url).origin)return fail(403,'cross_origin','Cross-origin changes are not permitted.');
  if(c.req.header('Sec-Fetch-Site')==='cross-site')return fail(403,'cross_site','Cross-site changes are not permitted.');
 }
 if(c.req.path.startsWith('/api/')&&c.req.path!=='/api/health')await bootstrap(c.env.DB);
 await next();
});
app.onError((err,c)=>{const known=err instanceof APIError;const status=known?err.status:err instanceof TypeError?422:500;return c.json({error:known?err.message:status===422?err.message:'The request could not be completed. Try again.',code:known?err.code:status===422?'validation':'internal_error',request_id:random().slice(0,12)},status as 400);});
app.get('/api/health',c=>c.json({status:'ok',mode:'synthetic-demo',product:'Exaclim'}));
app.post('/api/v1/auth/login',async c=>{
 const data=await body(c,['email','password']);if(typeof data.email!=='string'||typeof data.password!=='string'||data.email.length>320||data.password.length>1024)return fail(422,'credentials','Provide the synthetic demo email and password.');
 const db=c.env.DB,key=await digest(c.req.header('CF-Connecting-IP')??'local'),now=new Date().toISOString();
 const attempts=await db.prepare('SELECT count FROM login_attempts WHERE key_hash=? AND expires_at>?').bind(key,now).first<{count:number}>();if((attempts?.count??0)>=10)return fail(429,'rate_limited','Too many attempts. Wait a minute and try again.');
 const account=await db.prepare('SELECT * FROM users WHERE email=?').bind(data.email.trim().toLowerCase()).first<{id:string;salt:string;password_hash:string;password_rounds:number}>();
 const hash=await passwordHash(data.password,account?.salt??'synthetic-unknown-account',account?.password_rounds??ROUNDS);
 let difference=0;const expected=account?.password_hash??'0'.repeat(64);for(let i=0;i<64;i++)difference|=hash.charCodeAt(i)^expected.charCodeAt(i);
 if(!account||difference!==0){await db.prepare('INSERT INTO login_attempts VALUES(?,1,?) ON CONFLICT(key_hash) DO UPDATE SET count=CASE WHEN expires_at<=? THEN 1 ELSE count+1 END,expires_at=CASE WHEN expires_at<=? THEN excluded.expires_at ELSE expires_at END').bind(key,new Date(Date.now()+60000).toISOString(),now,now).run();return fail(401,'invalid_credentials','Email or password does not match the demo account.');}
 const token=random()+random(),expires=new Date(Date.now()+43200000).toISOString();await db.batch([db.prepare('DELETE FROM login_attempts WHERE key_hash=?').bind(key),db.prepare('DELETE FROM sessions WHERE expires_at<=?').bind(now),db.prepare('INSERT INTO sessions VALUES(?,?,?,?)').bind(await digest(token),account.id,now,expires)]);
 setCookie(c,COOKIE,token,{path:'/',httpOnly:true,sameSite:'Strict',secure:new URL(c.req.url).protocol==='https:',maxAge:43200});
 const sites=await db.prepare('SELECT site_id FROM user_sites WHERE user_id=? ORDER BY site_id').bind(account.id).all<{site_id:string}>();
 return c.json({user:{id:account.id,email:'demo@exaclim.test',name:'Demo supervisor',site_ids:sites.results.map(s=>s.site_id)},mode:'synthetic-demo'});
});
app.get('/api/v1/auth/me',async c=>c.json({user:await user(c),mode:'synthetic-demo'}));
app.post('/api/v1/auth/logout',async c=>{await body(c,[]);const token=getCookie(c,COOKIE);if(token)await c.env.DB.prepare('DELETE FROM sessions WHERE token_hash=?').bind(await digest(token)).run();setCookie(c,COOKIE,'',{path:'/',httpOnly:true,sameSite:'Strict',secure:new URL(c.req.url).protocol==='https:',maxAge:0});return c.json({ok:true});});
app.get('/api/v1/sites/:id/:operation',async c=>{
 const id=c.req.param('id'),op=c.req.param('operation');if(!['dashboard','setup'].includes(op))return fail(404,'not_found','Endpoint not found.');const u=await user(c,id),{state}=await load(c.env.DB),s=site(state,id);
 return c.json(op==='dashboard'?dashboard(state,id,u):{site:summary(s),crews:s.crews.map(({id,name,count})=>({id,name,count})),assignments:s.assignments,mode:'synthetic-demo'});
});
function validated<T>(fn:()=>T):T {try{return fn();}catch(e){if(e instanceof APIError)throw e;return fail(422,'validation',e instanceof Error?e.message.slice(0,180):'Invalid value.');}}
app.patch('/api/v1/sites/:id',async c=>{
 const id=c.req.param('id');await user(c,id);const data=await body(c,['name','latitude','longitude','timezone']);
 const result=await update(c.env.DB,state=>{const current=site(state,id),changed={...summary(current),...data};validated(()=>{const temporary:State={schema_version:1,sites:{}};addSite(temporary,changed.name as string,changed.latitude as number,changed.longitude as number,changed.timezone as string);});Object.assign(current,{name:(changed.name as string).trim(),latitude:changed.latitude,longitude:changed.longitude,timezone:changed.timezone});return summary(current);});return c.json({site:result,ok:true});
});
app.post('/api/v1/sites/:id/:operation',async c=>{
 const id=c.req.param('id'),op=c.req.param('operation');if(!['crews','assignments','simulate'].includes(op))return fail(404,'not_found','Endpoint not found.');const u=await user(c,id);
 if(op==='crews'){const d=await body(c,['name','count']);const crew=await update(c.env.DB,s=>{site(s,id);return validated(()=>addCrew(s,id,d.name as string,d.count as number));});return c.json({crew,...crew},201);}
 if(op==='assignments'){const d=await body(c,['crew_id','worker_name','watch_id']);const assignment=await update(c.env.DB,s=>{site(s,id);return validated(()=>assignWatch(s,id,d.crew_id as string,d.worker_name as string,d.watch_id as string));});return c.json({assignment,...assignment},201);}
 const d=await body(c,['scenario']);if(typeof d.scenario!=='string')return fail(422,'scenario','Choose a named synthetic scenario.');if(!['normal','rising-heat','connection-lost','reconnect','help','delayed-help','resolve-help'].includes(d.scenario))return fail(422,'validation','Unknown scenario');
 const result=await update(c.env.DB,s=>{site(s,id);validated(()=>scenario(s,id,d.scenario as string));return dashboard(s,id,u);});return c.json({ok:true,scenario:d.scenario,dashboard:result});
});
app.post('/api/v1/emergencies/:id/ack',async c=>{
 const u=await user(c);await body(c,[]);const id=c.req.param('id');const event=await update(c.env.DB,s=>{const owner=Object.values(s.sites).find(site=>site.events.some(e=>e.id===id));if(!owner)return fail(404,'event_not_found','Help event not found.');if(!u.site_ids.includes(owner.id))return fail(403,'site_forbidden','This supervisor cannot access the requested site.');return validated(()=>acknowledge(s,id,u.name));});return c.json({ok:true,id:event.id,acknowledged:true,acknowledged_at:event.acknowledged_at,acknowledged_by:event.acknowledged_by,watch_state_cleared:false});
});
app.all('/api/*',()=>fail(404,'not_found','Endpoint not found.'));
app.all('*',async c=>{const response=await c.env.ASSETS.fetch(c.req.raw);const headers=new Headers(response.headers);headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");headers.set('X-Content-Type-Options','nosniff');headers.set('Referrer-Policy','no-referrer');return new Response(response.body,{status:response.status,headers});});
export default app;
