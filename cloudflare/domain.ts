/** Synthetic Exaclim domain. No physical delivery, clinical threshold or protection claims. */
export const POLICY_VERSION = 'synthetic-dashboard-v1';
export const STALE_SECONDS = 120;
type Level = 'green' | 'amber' | 'red';
const LEVELS: Level[] = ['green', 'amber', 'red'];
export interface Crew { id:string; name:string; count:number; watch_ids:string[] }
export interface Assignment { id:string; crew_id:string; worker_name:string; watch_id:string; version:number; assigned_at:string }
export interface Sample { level:Level; sampled_at:string; received_at:string }
export interface HelpEvent { id:string; worker_name:string; watch_id:string; crew_id:string; assignment_id:string; assignment_version:number; occurred_at:string; received_at:string|null; delayed:boolean; acknowledged_at:string|null; acknowledged_by:string|null; resolved_at:string|null }
export interface Site { id:string; name:string; latitude:number; longitude:number; timezone:string; crews:Crew[]; assignments:Assignment[]; samples:Record<string,Sample>; events:HelpEvent[]; scenario:string; forecast_generated_at:string; gateway_connected:boolean; pending_events:HelpEvent[]; weather_cache?:WeatherCache }
export interface State { schema_version:number; sites:Record<string,Site> }
type Clock = Date|string;
const iso = (date:Date) => date.toISOString();
function now(value?:Clock):Date {
  if (typeof value === 'string' && !/(Z|[+-]\d\d:\d\d)$/.test(value)) throw new Error('Timestamp must include timezone');
  const date = value === undefined ? new Date() : value instanceof Date ? new Date(value.getTime()) : new Date(value);
  if (!Number.isFinite(date.getTime())) throw new Error('Invalid timestamp');
  return date;
}
function text(value:unknown,label:string,limit=100):string {
  if(typeof value !== 'string' || !value.trim() || value.trim().length>limit || /[\x00-\x1f]/.test(value)) throw new Error(`${label} must be nonempty text, at most ${limit} characters`);
  return value.trim();
}
function siteFor(state:State,id:string):Site {
  if(!state?.sites || typeof id!=='string' || !Object.hasOwn(state.sites,id)) throw new Error('Unknown site');
  return state.sites[id];
}
function crewFor(site:Site,id:string):Crew {
  const crew=site.crews.find(c=>c.id===id); if(!crew) throw new Error('Unknown crew'); return crew;
}
const rank = (level:Level)=>LEVELS.indexOf(level);
function worst(levels:Level[],fallback:Level='amber'):Level {return levels.length ? levels.reduce((a,b)=>rank(a)>rank(b)?a:b) : fallback;}
function emptySite(id:string,name:string,lat:number,lon:number,zone:string,clock:Date):Site {
  return {id,name,latitude:lat,longitude:lon,timezone:zone,crews:[],assignments:[],samples:{},events:[],scenario:'normal',forecast_generated_at:iso(clock),gateway_connected:true,pending_events:[]};
}
export function addSite(state:State,name:string,lat:number,lon:number,timezone:string):Site {
  name=text(name,'Site name');
  if(typeof lat!=='number'||typeof lon!=='number'||!Number.isFinite(lat)||!Number.isFinite(lon)||lat < -90||lat >90||lon < -180||lon >180) throw new Error('Coordinates must be finite latitude/longitude');
  if(typeof timezone!=='string') throw new Error('Unknown IANA timezone');
  try {new Intl.DateTimeFormat('en',{timeZone:timezone}).format();} catch {throw new Error('Unknown IANA timezone');}
  if(!state?.sites) throw new Error('Invalid state');
  const id=crypto.randomUUID(); const site=emptySite(id,name,lat,lon,timezone,now()); state.sites[id]=site; return {...site};
}
export function addCrew(state:State,siteId:string,name:string,count:number):Crew {
  const site=siteFor(state,siteId); name=text(name,'Crew name');
  if(!Number.isInteger(count)||count<1||count>20) throw new Error('Crew count must be an integer from 1 to 20');
  if(site.crews.length>=10) throw new Error('Demo supports at most 10 crews per site');
  if(site.crews.some(c=>c.name.toLocaleLowerCase()===name.toLocaleLowerCase())) throw new Error('Crew name already exists');
  const crew={id:crypto.randomUUID(),name,count,watch_ids:[] as string[]}; site.crews.push(crew); return {...crew};
}
export function renameCrew(state:State,siteId:string,crewId:string,name:string,count:number):Crew {
  const site=siteFor(state,siteId),crew=crewFor(site,crewId); name=text(name,'Crew name');
  if(!Number.isInteger(count)||count<1||count>20) throw new Error('Crew count must be an integer from 1 to 20');
  if(count<crew.watch_ids.length) throw new Error('Crew count cannot drop below assigned watches');
  if(site.crews.some(c=>c.id!==crewId&&c.name.toLocaleLowerCase()===name.toLocaleLowerCase())) throw new Error('Crew name already exists');
  crew.name=name;crew.count=count;return {...crew};
}
export function removeCrew(state:State,siteId:string,crewId:string):void {
  const site=siteFor(state,siteId),crew=crewFor(site,crewId);
  if(crew.watch_ids.length) throw new Error('Reassign watches before removing this crew');
  const ids=new Set(privacyGroups(site).flat().map(c=>c.id));
  site.crews=site.crews.filter(c=>c.id!==crewId);
  site.events=site.events.filter(e=>e.crew_id!==crewId);
  if(site.crews.length&&ids.has(crewId)) snapshot(state,siteId); // refresh derived grouping caches
}
export function assignWatch(state:State,siteId:string,crewId:string,workerName:string,watchId:string):Assignment {
  const site=siteFor(state,siteId),crew=crewFor(site,crewId); workerName=text(workerName,'Worker name'); watchId=text(watchId,'Watch ID',64);
  if(Object.values(state.sites).some(s=>s.assignments.some(a=>a.watch_id.toLowerCase()===watchId.toLowerCase()))) throw new Error('Watch already has an active assignment');
  if(crew.watch_ids.length>=crew.count) throw new Error('Crew roster is full');
  const assignment={id:crypto.randomUUID(),crew_id:crewId,worker_name:workerName,watch_id:watchId,version:1,assigned_at:iso(now())};
  site.assignments.push(assignment); crew.watch_ids.push(watchId); return {...assignment};
}
export function initialState(at?:Clock):State {
  const clock=now(at),state:State={schema_version:1,sites:{}};
  const site=emptySite('accra','Accra Construction Site',5.6037,-.187,'Africa/Accra',clock); state.sites.accra=site;
  const names=['Ama Mensah','Kofi Owusu','Akosua Boateng','Kwame Asare','Abena Osei','Yaw Addo','Efua Arthur','Kojo Agyeman'];
  for(const [label,count] of [['Concrete crew',5],['Roofing crew',2],['Lifting crew',1]] as const) {
    const crew=addCrew(state,'accra',label,count);
    for(let i=0;i<count;i++) {
      assignWatch(state,'accra',crew.id,names[site.assignments.length],`DEMO-${String(site.assignments.length+1).padStart(3,'0')}`);
      site.assignments.at(-1)!.assigned_at=iso(clock);
    }
  }
  scenario(state,'accra','normal',clock);
  state.sites.tema=emptySite('tema','Tema Construction Site',5.6698,-.0166,'Africa/Accra',clock);
  return state;
}
function privacyGroups(site:Site):Crew[][] {
  const small=site.crews.filter(c=>c.count<3),eligible=site.crews.filter(c=>c.count>=3),groups:Crew[][]=[];
  let pending:Crew[]=[];
  for(const crew of small) {pending.push(crew);if(pending.reduce((a,c)=>a+c.count,0)>=3){groups.push(pending);pending=[];}}
  if(pending.length) {if(eligible.length){pending.push(eligible.shift()!);groups.push(pending);}else if(groups.length){groups.at(-1)!.push(...pending);}else groups.push(pending);}
  groups.push(...eligible.map(c=>[c])); return groups;
}
function localParts(date:Date,zone:string) {
  const parts=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'}).formatToParts(date);
  const obj=Object.fromEntries(parts.filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));
  return {year:+obj.year,month:+obj.month,day:+obj.day,hour:+obj.hour,minute:+obj.minute,second:+obj.second};
}
const pad=(value:number)=>String(value).padStart(2,'0');
function dateLabel(p:{year:number;month:number;day:number}) {return `${p.year}-${pad(p.month)}-${pad(p.day)}`;}
function shiftDay(label:string,offset:number) {const d=new Date(`${label}T12:00:00Z`);d.setUTCDate(d.getUTCDate()+offset);return d.toISOString().slice(0,10);}
function midnight(label:string,zone:string):Date {
  const desired=Date.parse(`${label}T00:00:00Z`); let candidate=desired; const seen:number[]=[];
  for(let i=0;i<8;i++) {const p=localParts(new Date(candidate),zone),wall=Date.UTC(p.year,p.month-1,p.day,p.hour,p.minute,p.second);const delta=desired-wall;if(delta===0)return new Date(candidate);seen.push(candidate);candidate+=delta;}
  // Some zones skip local midnight during DST; select first representable instant of the day.
  const options=[candidate,...seen].filter(t=>dateLabel(localParts(new Date(t),zone))===label);
  if(!options.length) throw new Error('Local date is not representable');
  return new Date(Math.min(...options));
}
function localISO(date:Date,zone:string):string {
  const p=localParts(date,zone),wall=Date.UTC(p.year,p.month-1,p.day,p.hour,p.minute,p.second);
  const minutes=Math.round((wall-Math.floor(date.getTime()/1000)*1000)/60000),sign=minutes<0?'-':'+';
  return `${dateLabel(p)}T${pad(p.hour)}:${pad(p.minute)}:${pad(p.second)}${sign}${pad(Math.floor(Math.abs(minutes)/60))}:${pad(Math.abs(minutes)%60)}`;
}
interface Window {start:string;end:string;start_local:string;end_local:string}
export interface ForecastRow {start:string;end:string;local_time:string;label:string;risk:Level;temperature_c:number|null;humidity_pct:number|null;source_type:string;data_quality:string;caution:boolean;display_risk:Level|'unknown'}
export interface Forecast {source:string;source_type:string;provider:string;generated_at:string;fetched_at?:string;stale:boolean;age_seconds:number;data_quality:string;provider_issue_time:string|null;timezone:string;latitude:number;longitude:number;days:{date:string;label:string;hours:ForecastRow[];red_windows:Window[];windows:Window[]}[];policy_version:string;limitations:string}
function forecastFor(site:Site,clock:Date) {
  const today=dateLabel(localParts(clock,site.timezone)),age=(clock.getTime()-now(site.forecast_generated_at).getTime())/1000,stale=age>21600||age<0;
  const days=[];
  for(let offset=0;offset<2;offset++) {
    const date=shiftDay(today,offset),start=midnight(date,site.timezone),end=midnight(shiftDay(date,1),site.timezone);
    const hours:ForecastRow[]=[],windows:Window[]=[];let window:Window|null=null;
    for(let millis=start.getTime();millis<end.getTime();millis+=3600000) {
      const instant=new Date(millis),next=new Date(Math.min(millis+3600000,end.getTime())),local=localISO(instant,site.timezone),hour=localParts(instant,site.timezone).hour;
      const risk:Level=hour>=11&&hour<15?'red':hour>=9&&hour<17?'amber':'green';
      const row:ForecastRow={start:iso(instant),end:iso(next),local_time:local,label:`${pad(hour)}:${pad(localParts(instant,site.timezone).minute)} ${local.slice(-6).replace(':','')}`,risk,temperature_c:Math.round((26+Math.max(0,Math.sin((hour-6)*Math.PI/14))*9+offset*.5)*10)/10,humidity_pct:65,source_type:'synthetic',data_quality:stale?'stale':'synthetic',caution:stale,display_risk:stale?'unknown':risk};
      hours.push(row);
      if(risk==='red'&&!window)window={start:row.start,end:row.end,start_local:local,end_local:localISO(next,site.timezone)};
      else if(risk==='red'&&window){window.end=row.end;window.end_local=localISO(next,site.timezone);}
      else if(window){windows.push(window);window=null;}
    }
    if(window)windows.push(window);
    days.push({date,label:offset===0?'Today':'Tomorrow',hours,red_windows:windows,windows});
  }
  return {source:'Synthetic scenario forecast — not live weather',source_type:'synthetic',provider:'Exaclim simulator',generated_at:site.forecast_generated_at,stale,age_seconds:Math.max(0,age),data_quality:stale?'stale':'synthetic',provider_issue_time:null,timezone:site.timezone,latitude:site.latitude,longitude:site.longitude,days,policy_version:POLICY_VERSION,limitations:'Illustrative heat labels; not WBGT or clinical thresholds.'};
}
export interface WeatherCache {fetched_at:string;provider_issue_time:string|null;hours:Record<string,{temperature_c:number|null;humidity_pct:number|null}>}
/** Store a live provider payload on the site; hours keyed by local ISO minute `YYYY-MM-DDTHH:00`. */
export function recordWeather(site:Site,payload:WeatherCache,clock:Date):void {
  if(!payload||typeof payload!=='object'||typeof payload.hours!=='object'||payload.hours===null) throw new Error('Weather payload must include an hours object');
  for(const [key,value] of Object.entries(payload.hours)) {
    if(!/^\d{4}-\d{2}-\d{2}T\d{2}:00$/.test(key)) throw new Error('Weather hours must be keyed by local YYYY-MM-DDTHH:00');
    if(value!==null&&(typeof value!=='object'||typeof (value as {temperature_c?:unknown}).temperature_c!=='number'&&((value as {temperature_c?:unknown}).temperature_c!==null))) throw new Error('Weather hours must provide a temperature or null');
  }
  const fetched=now(payload.fetched_at);if(fetched.getTime()>clock.getTime()+300000) throw new Error('Weather fetch time is in the future');
  site.weather_cache={fetched_at:iso(fetched),provider_issue_time:payload.provider_issue_time?iso(now(payload.provider_issue_time)):null,hours:payload.hours};
  site.forecast_generated_at=iso(clock);
}
const WEATHER_STALE_SECONDS=10800;
/** Live forecast from cached provider hours; missing/stale hours degrade to explicit unknown, never synthetic. */
function liveForecastFor(site:Site,clock:Date):Forecast|null {
  const cache=site.weather_cache;
  if(!cache)return null;
  const age=(clock.getTime()-now(cache.fetched_at).getTime())/1000,stale=age>WEATHER_STALE_SECONDS||age<0;
  const today=dateLabel(localParts(clock,site.timezone)),days:Forecast['days']=[];
  for(let offset=0;offset<2;offset++) {
    const date=shiftDay(today,offset),start=midnight(date,site.timezone),end=midnight(shiftDay(date,1),site.timezone);
    const hours:ForecastRow[]=[],windows:Window[]=[];let window:Window|null=null;
    for(let millis=start.getTime();millis<end.getTime();millis+=3600000) {
      const instant=new Date(millis),next=new Date(Math.min(millis+3600000,end.getTime())),local=localISO(instant,site.timezone),hour=localParts(instant,site.timezone).hour;
      const key=local.slice(0,13)+':00',reading=cache.hours[key],known=reading!==undefined&&typeof reading.temperature_c==='number';
      const temperature=known?(reading as {temperature_c:number}).temperature_c:null;
      const level:Level=temperature!==null&&temperature>=32?'red':temperature!==null&&temperature>=29?'amber':'green';
      const row:ForecastRow={start:iso(instant),end:iso(next),local_time:local,label:`${pad(hour)}:${pad(localParts(instant,site.timezone).minute)} ${local.slice(-6).replace(':','')}`,risk:level,temperature_c:temperature,humidity_pct:reading?.humidity_pct??null,source_type:'live',data_quality:known?'live':'missing',caution:!known,display_risk:known&&!stale?level:'unknown'};
      hours.push(row);
      if(known&&level==='red'&&!window)window={start:row.start,end:row.end,start_local:local,end_local:localISO(next,site.timezone)};
      else if(known&&level==='red'&&window){window.end=row.end;window.end_local=localISO(next,site.timezone);}
      else if(window){windows.push(window);window=null;}
    }
    if(window)windows.push(window);
    days.push({date,label:offset===0?'Today':'Tomorrow',hours,red_windows:windows,windows});
  }
  return {source:`Live public weather via Open-Meteo — fetched ${cache.fetched_at}`,source_type:'live',provider:'Open-Meteo',generated_at:iso(clock),fetched_at:cache.fetched_at,stale,age_seconds:Math.max(0,age),data_quality:stale?'stale':'live',provider_issue_time:cache.provider_issue_time,timezone:site.timezone,latitude:site.latitude,longitude:site.longitude,days,policy_version:POLICY_VERSION,limitations:'Air-temperature illustration; not WBGT or clinical thresholds.'};
}
export function snapshot(state:State,siteId='accra',at?:Clock) {
  const site=siteFor(state,siteId),clock=now(at),forecast=liveForecastFor(site,clock)??forecastFor(site,clock),groups=[],suggestions=[];
  for(const crews of privacyGroups(site)) {
    const ids=crews.map(c=>c.id),watchIds=crews.flatMap(c=>c.watch_ids),expected=crews.reduce((a,c)=>a+c.count,0),fresh:Sample[]=[],known:Level[]=[],sampleTimes:number[]=[],receiptTimes:number[]=[];
    for(const watch of watchIds) {
      const sample=site.samples[watch];if(!sample||!LEVELS.includes(sample.level))continue;known.push(sample.level);
      try {const measured=now(sample.sampled_at).getTime(),received=now(sample.received_at).getTime();sampleTimes.push(measured);receiptTimes.push(received);const age=(clock.getTime()-measured)/1000;if(age>=0&&age<=STALE_SECONDS&&received<=clock.getTime())fresh.push(sample);}catch{/* malformed samples remain cautionary */}
    }
    const unknown=Math.max(0,expected-fresh.length),suppressed=fresh.length<3||expected<3;
    let heat=worst(known);if(unknown||suppressed)heat=worst([heat,'amber']);
    const active=site.events.filter(e=>ids.includes(e.crew_id)&&!e.resolved_at),overall:Level=active.length?'red':heat;
    const counts=suppressed?null:{green:fresh.filter(s=>s.level==='green').length,amber:fresh.filter(s=>s.level==='amber').length,red:fresh.filter(s=>s.level==='red').length};
    const budget=!suppressed&&!unknown?{green:20,amber:55,red:85}[heat]:null,id=`group-${ids.join('-')}`;
    const sampled=sampleTimes.length?iso(new Date(Math.max(...sampleTimes))):null,received=receiptTimes.length?iso(new Date(Math.max(...receiptTimes))):null;
    const group={id,name:crews.map(c=>c.name).join(' + '),crew_ids:ids,expected_contributors:expected,fresh_contributors:fresh.length,unknown_contributors:unknown,counts,budget,state:overall,heat_state:heat,help_active:!!active.length,suppressed,status_message:suppressed?'Group status unavailable — insufficient contributors':active.length?'Help state active':unknown?'Caution — incomplete or stale data':'Fresh simulated crew summary',last_sample_at:sampled,last_received_at:received,level:overall,total_workers:expected,valid_contributors:fresh.length,updated_at:sampled,received_at:received,data_quality:suppressed?'insufficient':unknown?'stale':'synthetic',budget_source:'Synthetic group-level illustration; not individual watch data'};
    groups.push(group);
    const windows=forecast.days.flatMap(d=>d.red_windows).filter(w=>now(w.end)>clock),window=windows.length&&!forecast.stale?windows[0]:null;
    const action=active.length?'Follow the site emergency procedure. Acknowledgement confirms receipt, not resolution.':overall==='red'?'Pause the affected task; arrange cooling and review rotation under the site heat-control plan.':unknown||suppressed?'Check the crew connection and use general site heat controls; no exposure-based rest duration is available.':forecast.stale?'Forecast is stale; check current conditions and use general site heat controls rather than a precise planning window.':window?'Plan heavier tasks outside the upcoming high-risk window; prepare shaded breaks and review rotation.':'Maintain site heat controls and review conditions before changing task intensity.';
    suggestions.push({group_id:id,group_name:group.name,state:overall,title:unknown||suppressed?'Review site controls':'Plan breaks and rotation',level:overall,reason:'Uses the most cautious group state and upcoming forecast; uncertainty never lowers caution.',action,window,policy_version:POLICY_VERSION,source:'Synthetic forecast + simulated privacy-safe group state',data_quality:unknown||suppressed?'incomplete':forecast.stale?'stale':'synthetic',limitations:'Advice — supervisor decides. No clinical rest prescription or safe-work allowance.'});
  }
  const emergencies=site.events.filter(e=>!e.acknowledged_at).map(e=>({id:e.id,worker_name:e.worker_name,watch_id:e.watch_id,crew_id:e.crew_id,occurred_at:e.occurred_at,received_at:e.received_at,acknowledged_at:e.acknowledged_at,acknowledged_by:e.acknowledged_by,resolved_at:e.resolved_at,delayed:e.delayed,crew_name:crewFor(site,e.crew_id).name})).sort((a,b)=>a.occurred_at.localeCompare(b.occurred_at)||a.id.localeCompare(b.id));
  return {site:{id:site.id,name:site.name,latitude:site.latitude,longitude:site.longitude,timezone:site.timezone},mode:'Synthetic demo — no real workers or devices',policy_version:POLICY_VERSION,generated_at:iso(clock),scenario:site.scenario,forecast,groups,suggestions,emergencies,active_help_count:site.events.filter(e=>!e.resolved_at).length,weather_source:forecast.source_type};
}
export function scenario(state:State,siteId:string,kind:string,at?:Clock) {
  const site=siteFor(state,siteId),clock=now(at),allowed=['normal','rising-heat','connection-lost','reconnect','help','symptom','delayed-help','resolve-help'];
  if(!allowed.includes(kind))throw new Error('Unknown scenario');
  if(['help','symptom','delayed-help'].includes(kind)) {
    const assignment=site.assignments[0];if(!assignment)throw new Error('Assign a watch before creating a help event');
    const occurred=kind==='delayed-help'?new Date(clock.getTime()-720000):clock;
    const event:HelpEvent={id:crypto.randomUUID(),worker_name:assignment.worker_name,watch_id:assignment.watch_id,crew_id:assignment.crew_id,assignment_id:assignment.id,assignment_version:assignment.version,occurred_at:iso(occurred),received_at:iso(clock),delayed:kind==='delayed-help',acknowledged_at:null,acknowledged_by:null,resolved_at:null};
    if(kind!=='delayed-help'&&site.gateway_connected===false){event.received_at=null;(site.pending_events??=[]).push(event);}else site.events.push(event);
  } else if(kind==='resolve-help') {for(const event of site.events)if(!event.resolved_at)event.resolved_at=iso(clock);
  } else if(kind==='connection-lost') {site.gateway_connected=false;for(const sample of Object.values(site.samples))sample.sampled_at=iso(new Date(clock.getTime()-180000));
  } else {
    site.gateway_connected=true;const existing=new Set(site.events.map(e=>e.id));
    for(const queued of site.pending_events??[])if(!existing.has(queued.id)){site.events.push({...queued,received_at:iso(clock),delayed:true});existing.add(queued.id);}site.pending_events=[];
    site.assignments.forEach((assignment,i)=>{const old=site.samples[assignment.watch_id];let level:Level=kind==='rising-heat'?LEVELS[i%3]:i===1?'amber':'green';if(kind==='reconnect')level=old?.level??'amber';site.samples[assignment.watch_id]={level,sampled_at:iso(clock),received_at:iso(clock)};});
  }
  if(['normal','rising-heat','reconnect'].includes(kind))site.forecast_generated_at=iso(clock);
  site.scenario=kind;return snapshot(state,siteId,clock);
}
export function acknowledge(state:State,eventId:string,actor='Demo Supervisor',at?:Clock):HelpEvent {
  eventId=text(eventId,'Event ID');actor=text(actor,'Actor');const clock=now(at);
  for(const site of Object.values(state.sites))for(const event of site.events)if(event.id===eventId){if(!event.acknowledged_at){event.acknowledged_at=iso(clock);event.acknowledged_by=actor;}return {...event};}
  throw new Error('Unknown help event');
}
export interface GatewayBatchEntry {watch_id:string;level:Level;sampled_at:string;sequence:number}
export interface GatewayHelpEntry {event_id:string;watch_id:string;occurred_at:string;kind:'help'|'symptom'}
/** Validate an aggregate batch for a site: known watches, ordered sequences, no future samples.
 * Returns the highest accepted sequence; throws with a readable reason otherwise. */
export function validateBatch(state:State,siteId:string,entries:GatewayBatchEntry[],lastSequence:number,clock:Date):number {
  const site=siteFor(state,siteId);
  if(!Array.isArray(entries)||entries.length>200) throw new Error('Batch must contain at most 200 entries');
  const watches=new Map(site.assignments.map(a=>[a.watch_id.toLowerCase(),a])),known=new Set(watches.keys());
  let highest=lastSequence;
  const seenSequences=new Set<number>();
  for(const entry of entries) {
    if(typeof entry.watch_id!=='string'||typeof entry.sequence!=='number'||!Number.isInteger(entry.sequence)) throw new Error('Each batch entry needs a watch ID and integer sequence');
    if(!known.has(entry.watch_id.toLowerCase())) throw new Error(`Unknown watch ID in batch`);
    if(entry.sequence<=lastSequence) throw new Error('Batch sequence was already processed');
    if(seenSequences.has(entry.sequence)) throw new Error('Duplicate sequence within batch');
    seenSequences.add(entry.sequence);
    if(!LEVELS.includes(entry.level)) throw new Error('Batch level must be green, amber or red');
    const sampled=now(entry.sampled_at);
    if(sampled.getTime()>clock.getTime()+120000) throw new Error('Sample timestamp is in the future');
    if(sampled.getTime()<clock.getTime()-86400000) throw new Error('Sample timestamp is older than one day');
    highest=Math.max(highest,entry.sequence);
  }
  return highest;
}
/** Validate an authorized help event: known watch, immutable ID, plausible occurrence time. */
export function validateHelpEvent(state:State,siteId:string,entry:GatewayHelpEntry,clock:Date):{watch_id:string;assignment:Assignment;occurred:Date} {
  const site=siteFor(state,siteId);
  if(typeof entry.event_id!=='string'||!/^[A-Za-z0-9-]{8,64}$/.test(entry.event_id)) throw new Error('Help event needs an ID of 8-64 letters, digits or dashes');
  if(entry.kind!=='help'&&entry.kind!=='symptom') throw new Error('Help kind must be help or symptom');
  const assignment=site.assignments.find(a=>a.watch_id.toLowerCase()===entry.watch_id?.toLowerCase());
  if(!assignment) throw new Error('Unknown watch ID for help event');
  const occurred=now(entry.occurred_at);
  if(occurred.getTime()>clock.getTime()+120000) throw new Error('Help occurrence time is in the future');
  if(occurred.getTime()<clock.getTime()-86400000*2) throw new Error('Help occurrence time is older than two days');
  return {watch_id:assignment.watch_id,assignment,occurred};
}
/** Apply a validated batch: per-watch samples measured at their stated time. */
export function applyBatch(state:State,siteId:string,entries:GatewayBatchEntry[]):void {
  const site=siteFor(state,siteId);
  for(const entry of entries) {
    const assignment=site.assignments.find(a=>a.watch_id.toLowerCase()===entry.watch_id.toLowerCase())!;
    site.samples[assignment.watch_id]={level:entry.level,sampled_at:iso(now(entry.sampled_at)),received_at:iso(new Date())};
  }
  site.gateway_connected=true;
}
/** Apply a validated help event; duplicates (same immutable ID) are ignored. */
export function applyHelpEvent(state:State,siteId:string,entry:GatewayHelpEntry,assignment:Assignment,occurred:Date,clock:Date):HelpEvent {
  const site=siteFor(state,siteId);
  const existing=site.events.find(e=>e.id===entry.event_id);
  if(existing)return existing;
  const delayed=clock.getTime()-occurred.getTime()>600000;
  const event:HelpEvent={id:entry.event_id,worker_name:assignment.worker_name,watch_id:assignment.watch_id,crew_id:assignment.crew_id,assignment_id:assignment.id,assignment_version:assignment.version,occurred_at:iso(occurred),received_at:iso(clock),delayed,acknowledged_at:null,acknowledged_by:null,resolved_at:null};
  site.events.push(event);
  return event;
}
