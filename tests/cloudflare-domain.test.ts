import test from 'node:test';
import assert from 'node:assert/strict';
import { initialState,snapshot,addSite,addCrew,assignWatch,scenario,acknowledge } from '../cloudflare/domain.ts';
import type { State } from '../cloudflare/domain.ts';
const NOW='2026-11-19T10:00:00Z';
const later=(seconds:number)=>new Date(Date.parse(NOW)+seconds*1000);
function populated(state:State,site:string,count:number,name:string){const crew=addCrew(state,site,name,count);for(let i=0;i<count;i++)assignWatch(state,site,crew.id,`Synthetic ${name} ${i}`,`${name}-${i}`);return crew;}

test('initial 2+1 grouping is stable and nonoverlapping',()=>{
 const state=initialState(NOW),result=snapshot(state,'accra',NOW);
 assert.deepEqual(result.groups.map(g=>g.total_workers).sort(),[3,5]);
 const ids=result.groups.flatMap(g=>g.crew_ids);assert.equal(ids.length,new Set(ids).size);
 assert.equal(result.groups.reduce((sum,g)=>sum+Object.values(g.counts!).reduce((a,b)=>a+b,0),0),8);
 assert.deepEqual(snapshot(state,'accra',NOW).groups.map(g=>g.id),result.groups.map(g=>g.id));
});
test('2+4 combines whole crew with no overlapping standalone total',()=>{
 const state=initialState(NOW),site=addSite(state,'Test',5,0,'Africa/Accra').id;
 const a=populated(state,site,2,'A'),b=populated(state,site,4,'B');scenario(state,site,'normal',NOW);
 const groups=snapshot(state,site,NOW).groups;assert.equal(groups.length,1);assert.equal(groups[0].total_workers,6);assert.deepEqual(new Set(groups[0].crew_ids),new Set([a.id,b.id]));
});
test('fewer than three contributors suppress counts and budget and impose caution',()=>{
 const state=initialState(NOW),site=addSite(state,'Small',5,0,'Africa/Accra').id;populated(state,site,2,'Small');scenario(state,site,'normal',NOW);
 for(const sample of Object.values(state.sites[site].samples))sample.level='green';
 const group=snapshot(state,site,NOW).groups[0];assert.equal(group.counts,null);assert.equal(group.budget,null);assert.equal(group.state,'amber');
 for(const watch of state.sites.accra.crews[0].watch_ids.slice(2))delete state.sites.accra.samples[watch];
 const incomplete=snapshot(state,'accra',NOW).groups.find(g=>g.total_workers===5)!;assert.equal(incomplete.counts,null);assert.equal(incomplete.fresh_contributors,2);
});
test('sample freshness exact boundary and stale red preservation',()=>{
 const state=initialState(NOW);scenario(state,'accra','rising-heat',NOW);
 assert.ok(snapshot(state,'accra',later(120)).groups.every(g=>g.unknown_contributors===0));
 assert.ok(snapshot(state,'accra',later(120.01)).groups.every(g=>g.state==='red'&&g.counts===null));
});
test('future and malformed sample timestamps cannot falsely reassure',()=>{
 const state=initialState(NOW),samples=Object.values(state.sites.accra.samples);samples[0].sampled_at='2099-01-01T00:00:00Z';samples[1].sampled_at='not-a-time';
 const group=snapshot(state,'accra',NOW).groups.find(g=>g.total_workers===5)!;assert.equal(group.unknown_contributors,2);assert.notEqual(group.state,'green');
});
test('help acknowledgement is idempotent and does not remove active-help red floor',()=>{
 const state=initialState(NOW),event=scenario(state,'accra','help',NOW).emergencies[0];assert.equal(event.worker_name,'Ama Mensah');
 const first=acknowledge(state,event.id,'One',later(1));const second=acknowledge(state,event.id,'Two',later(2));assert.equal(first.acknowledged_at,second.acknowledged_at);assert.equal(second.acknowledged_by,'One');
 let result=snapshot(state,'accra',later(2));assert.equal(result.emergencies.length,0);assert.equal(result.active_help_count,1);assert.ok(result.groups.some(g=>g.help_active&&g.state==='red'));
 scenario(state,'accra','connection-lost',later(3));assert.ok(snapshot(state,'accra',later(3)).groups.some(g=>g.help_active&&g.state==='red'));
 result=scenario(state,'accra','resolve-help',later(4));assert.equal(result.active_help_count,0);
});
test('local resolution before ACK retains named urgent queue',()=>{
 const state=initialState(NOW),event=scenario(state,'accra','help',NOW).emergencies[0];const result=scenario(state,'accra','resolve-help',later(1));
 assert.equal(result.active_help_count,0);assert.equal(result.emergencies.length,1);assert.ok(result.emergencies[0].resolved_at);
 acknowledge(state,event.id,'Supervisor',later(2));assert.equal(snapshot(state,'accra',later(2)).emergencies.length,0);
});
test('delayed help retains occurrence ordering and ACK is event-specific',()=>{
 const state=initialState(NOW);scenario(state,'accra','help',NOW);const result=scenario(state,'accra','delayed-help',later(10));
 assert.equal(result.emergencies.length,2);assert.equal(result.emergencies[0].delayed,true);acknowledge(state,result.emergencies[0].id,'Supervisor',later(11));assert.equal(snapshot(state,'accra',later(11)).emergencies.length,1);
});
test('offline help outbox persists privately and delivers once after reconnect',()=>{
 const state=initialState(NOW);scenario(state,'accra','connection-lost',NOW);const offline=scenario(state,'accra','help',later(10));
 assert.equal(offline.emergencies.length,0);assert.equal(offline.active_help_count,0);assert.ok(!JSON.stringify(offline).includes('Ama Mensah'));assert.ok(!('pending_events' in offline));
 const queued=state.sites.accra.pending_events[0];assert.equal(queued.received_at,null);
 const restored:State=JSON.parse(JSON.stringify(state));assert.equal(snapshot(restored,'accra',later(20)).emergencies.length,0);
 const delivered=scenario(restored,'accra','reconnect',later(300)).emergencies[0];assert.equal(delivered.id,queued.id);assert.equal(delivered.occurred_at,later(10).toISOString());assert.equal(delivered.received_at,later(300).toISOString());assert.equal(delivered.delayed,true);
 scenario(restored,'accra','reconnect',later(301));assert.equal(restored.sites.accra.events.length,1);assert.equal(restored.sites.accra.pending_events.length,0);
});
test('normal scenario resumes gateway and preserves earlier active events',()=>{
 const state=initialState(NOW);scenario(state,'accra','help',NOW);scenario(state,'accra','connection-lost',later(1));scenario(state,'accra','symptom',later(2));
 const result=scenario(state,'accra','normal',later(3));assert.equal(result.emergencies.length,2);assert.equal(result.active_help_count,2);assert.equal(state.sites.accra.gateway_connected,true);
});
test('two site-local forecast days cover all hours and red windows are half-open',()=>{
 const forecast=snapshot(initialState(NOW),'accra',NOW).forecast;assert.deepEqual(forecast.days.map(d=>d.date),['2026-11-19','2026-11-20']);assert.deepEqual(forecast.days.map(d=>d.hours.length),[24,24]);
 for(const day of forecast.days){const window=day.red_windows[0];assert.ok(window.start_local.includes('T11:00'));assert.ok(window.end_local.includes('T15:00'));const red=day.hours.filter(h=>h.risk==='red');assert.equal(red.length,4);assert.equal(red.at(-1)!.end,window.end);}
 assert.equal(forecast.source_type,'synthetic');assert.equal(forecast.provider_issue_time,null);
});
test('DST repeats distinct local hour offsets and uses site calendar date',()=>{
 const state=initialState(NOW),site=addSite(state,'NY',40,-74,'America/New_York').id;const forecast=snapshot(state,site,'2026-11-01T03:00:00Z').forecast;
 assert.equal(forecast.days[0].date,'2026-10-31');assert.deepEqual(forecast.days.map(d=>d.hours.length),[24,25]);const labels=forecast.days[1].hours.map(h=>h.label);assert.ok(labels.includes('01:00 -0400'));assert.ok(labels.includes('01:00 -0500'));
 const spring=snapshot(state,site,'2026-03-08T05:00:00Z').forecast;assert.equal(spring.days[0].hours.length,23);
});
test('stale forecasts are explicit after six hours; GET does not refresh',()=>{
 const state=initialState(NOW);assert.equal(snapshot(state,'accra',later(21600)).forecast.stale,false);
 const stale=snapshot(state,'accra',later(21601));assert.equal(stale.forecast.stale,true);assert.equal(stale.forecast.days[0].hours[0].display_risk,'unknown');assert.ok(stale.suggestions.every(s=>s.window===null));assert.equal(state.sites.accra.forecast_generated_at,new Date(NOW).toISOString());
 assert.equal(scenario(state,'accra','reconnect',later(21601)).forecast.stale,false);
});
test('routine snapshot never exposes individual names or budgets',()=>{
 const state=initialState(NOW),result=snapshot(state,'accra',NOW),serialized=JSON.stringify(result);
 for(const forbidden of ['Ama Mensah','DEMO-001','assignments','pending_events','clothing','acclimatized'])assert.ok(!serialized.includes(forbidden),forbidden);
 assert.ok(Object.values(state.sites.accra.samples).every(s=>!('budget' in s)));
});
test('validation rejects malformed values and watch IDs are unique across sites',()=>{
 const state=initialState(NOW),crew=addCrew(state,'tema','New crew',3);
 for(const count of [0,21,true,'3'])assert.throws(()=>addCrew(state,'tema','Bad',count as number));
 assert.throws(()=>assignWatch(state,'tema',crew.id,'Name','demo-001'));assert.throws(()=>addCrew(state,'tema','NEW CREW',3));
 assert.throws(()=>addSite(state,'Bad',Infinity,0,'Africa/Accra'));assert.throws(()=>addSite(state,'Bad',0,0,'Not/AZone'));assert.throws(()=>scenario(state,'accra','invalid',NOW));assert.throws(()=>acknowledge(state,'missing'));assert.throws(()=>snapshot(state,'accra','2026-11-19T10:00:00'));assert.throws(()=>snapshot(state,'__proto__',NOW));
});
test('JSON round-trip reproduces state and Tema starts empty',()=>{
 const state=initialState(NOW);assert.deepEqual(snapshot(JSON.parse(JSON.stringify(state)),'accra',NOW),snapshot(state,'accra',NOW));
 const result=snapshot(state,'tema',NOW);assert.deepEqual(result.groups,[]);assert.deepEqual(result.suggestions,[]);assert.deepEqual(result.emergencies,[]);
});
