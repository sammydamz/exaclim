import '@fontsource/inter/latin-400.css';
import '@fontsource/inter/latin-500.css';
import '@fontsource/inter/latin-600.css';
import '@fontsource/inter/latin-700.css';
import './styles.css';
import { agent, onAction, inputValue, setInput, setSelect, escapeHTML as esc, icon, mountIcons } from './components/ui.js';

globalThis.exaclim = Object.freeze({ agent });
mountIcons();
const $ = selector => document.querySelector(selector);
const state = {user:null, site:'accra', snapshot:null, offline:false, busy:false, epoch:0, day:'today', hour:null, forecastSignature:'', emergencySignature:'', siteSignature:'', setup:null, ackErrors:new Map(), pendingAcks:new Set(), editingCrew:null, streamLive:false};
let toastTimer;
const scenarios = [
  ['normal','Routine shift','Refresh readings for a routine shift.'],
  ['rising-heat','Rising heat','Increase the scenario heat load and update planning advice.'],
  ['connection-lost','Gateway disconnected','Make watch readings stale; retain a cautious crew state.'],
  ['reconnect','Reconnect gateway','Refresh readings. Keep unresolved help requests active.'],
  ['help','Worker calls for help','Show a worker help request.'],
  ['delayed-help','Delayed help delivery','Deliver an older queued help event after reconnection.'],
  ['resolve-help','Watch-local resolution','Resolve the device help state. Unacknowledged requests remain visible.']
];

function notify(message) {
  $('#toast').textContent = `✓ ${message}`;
  $('#toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 4500);
}
function sourceText(source) {
  if (!source) return 'Source unavailable';
  if (typeof source === 'string') return source;
  return source.provider || source.name || source.label || 'Source metadata available';
}
function stamp(value, options={}) {
  const date = new Date(value);
  if (!value || !Number.isFinite(date.getTime())) return 'Time unverified';
  try { return new Intl.DateTimeFormat('en-GB', {timeZone:state.snapshot?.site?.timezone || 'Africa/Accra', hour:'2-digit',minute:'2-digit', ...options}).format(date); }
  catch { return date.toISOString(); }
}
function secondsOld(value) {
  const date = new Date(value).getTime();
  if (!value || !Number.isFinite(date) || date > Date.now() + 60000) return Infinity;
  return Math.max(0, (Date.now()-date)/1000);
}
function age(value) {
  const seconds = secondsOld(value);
  if (!Number.isFinite(seconds)) return 'age unverified';
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${Math.floor(seconds)}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds/60)}m ago`;
  return `${Math.floor(seconds/3600)}h ago`;
}
function statusLabel(level) {return {green:'Green',amber:'Amber / caution',red:'Red / act now',unknown:'Unknown / caution'}[level] || 'Unknown / caution';}
function cautionLevel(group) {
  const known = ['green','amber','red'].includes(group.level) ? group.level : ['green','amber','red'].includes(group.state) ? group.state : 'unknown';
  if (group.help_active || known === 'red') return 'red';
  if (state.offline || group.suppressed || secondsOld(group.updated_at)>120 || group.data_quality === 'stale' || group.data_quality === 'unknown' || group.data_quality === 'invalid' || (group.counts?.unknown || 0)>0) return 'amber';
  return known;
}
async function api(path, body, method = body===undefined ? 'GET' : 'POST') {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(path, {method,credentials:'same-origin',signal:controller.signal,headers:{Accept:'application/json',...(body===undefined?{}:{'Content-Type':'application/json'})},...(body===undefined?{}:{body:JSON.stringify(body)})});
    let result;
    try { result = await response.json(); } catch { throw new Error('The server returned an unreadable response. Please retry.'); }
    if (response.status===401 && !path.endsWith('/login') && state.user) { clearAuthenticated(); $('#login-error').textContent='Your session ended. Sign in again.'; }
    if (!response.ok) throw new Error(typeof result.error==='string' ? result.error : result.error?.message || `Request could not be completed (${response.status}).`);
    return result;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Connection timed out. No save or acknowledgement is confirmed.');
    throw error;
  } finally { clearTimeout(timeout); }
}
function showAuthenticated() {
  $('#login-page').hidden=true;$('#dashboard').hidden=false;
  ['#site-switcher','#header-utilities'].forEach(selector=>{$(selector).hidden=false;});
  const name=state.user?.name || 'Supervisor',email=state.user?.email || '';
  $('#user-initials').textContent=name.split(/\s+/).map(part=>part[0]).join('').slice(0,2).toUpperCase() || 'S';
  $('#user-menu-name').textContent=name;$('#user-menu-email').textContent=email;
}
function clearAuthenticated() {
  state.epoch++;state.busy=false;state.user=null;state.snapshot=null;state.setup=null;state.ackErrors.clear();state.pendingAcks.clear();state.forecastSignature='';state.emergencySignature='';state.siteSignature='';state.streamLive=false;
  stopStream();
  $('#dashboard').hidden=true;$('#login-page').hidden=false;
  ['#site-switcher','#header-utilities'].forEach(selector=>{$(selector).hidden=true;});
  $('#emergency-region').replaceChildren();$('#crew-list').replaceChildren();$('#suggestions-list').replaceChildren();$('#setup-crews').replaceChildren();$('#setup-assignments').replaceChildren();
  ['#setup-dialog','#demo-dialog'].forEach(selector=>{$(selector).open=false;});
  $('#login-email')?.focus?.();
}
async function signIn() {
  const form=$('#login-form');if (!form.reportValidity()) return;
  $('#login-error').textContent='';
  try {
    const result=await api('/api/v1/auth/login',{email:inputValue('login-email'),password:inputValue('login-password')});
    state.user=result.user;state.site=state.user?.site_ids?.[0] || 'accra';state.offline=false;
    setInput('login-password','');showAuthenticated();
    await refreshDashboard();notify('Signed in');
  } catch(error) {$('#login-error').textContent=error.message;}
}
function renderConnection() {
  const offline=state.offline;
  $('#connection-warning').hidden=!offline;
  $('#connection-warning').textContent='Connection lost. Readings may be out of date and new help requests may be delayed. Check the crew phone and follow the site emergency procedure.';
}
function renderSite() {
  const snapshot=state.snapshot;if(!snapshot)return;
  const site=snapshot.site || {};
  $('#site-name').textContent=site.name || 'Worksite';$('#site-timezone').textContent=site.timezone || 'Timezone unverified';
  try {$('#site-date').textContent=new Intl.DateTimeFormat('en-GB',{timeZone:site.timezone || 'Africa/Accra',weekday:'long',day:'numeric',month:'long'}).format(new Date());} catch {$('#site-date').textContent='Site-local date unverified';}
  const sites=Array.isArray(snapshot.sites)?snapshot.sites:[{id:state.site,name:site.name || state.site}];
  const signature=JSON.stringify(sites);
  if(signature!==state.siteSignature){state.siteSignature=signature;setSelect('site-select',sites.map(item=>({value:String(item.id),label:item.name || item.id})),state.site);}
}
function windowTime(value) {
  if (typeof value==='string' && /^\d{1,2}:\d{2}$/.test(value)) return value;
  return stamp(value);
}
function planningWindow(value) {
  if (!value) return 'Next work window';
  if (typeof value==='string') return value;
  if (value.start && value.end) return `${stamp(value.start,{weekday:'short'})}–${stamp(value.end)}`;
  return value.label || 'Next work window';
}
function getDay() {return state.snapshot?.forecast?.days?.[state.day==='tomorrow'?1:0];}
function forecastLevel(hour) {
  if (state.offline || state.snapshot?.forecast?.stale || hour.quality==='missing' || hour.quality==='stale' || hour.quality==='invalid' || hour.quality==='unknown') return 'unknown';
  const level=hour.display_risk || hour.level || hour.risk;
  return ['green','amber','red'].includes(level)?level:'unknown';
}
function detailHour(index) {
  state.hour=index;
  const row=getDay()?.hours?.[index];if(!row)return;
  $('#forecast-hours').querySelectorAll('.hour-card').forEach((node,i)=>{node.toggleAttribute('data-selected',i===index);});
  const temperature=typeof row.temperature_c==='number'?`${row.temperature_c.toFixed(1)}°C`:'temperature unavailable';
  const humidity=typeof row.humidity_pct==='number'?`${row.humidity_pct}% relative humidity`:'humidity unavailable';
  $('#hour-detail').textContent=`${row.label || row.hour || stamp(row.time)}, ${statusLabel(forecastLevel(row))}, ${temperature}, ${humidity}${state.offline?', Offline':row.quality && row.quality!=='synthetic'?`, ${row.quality}`:''}`;
}
function renderForecast(force=false) {
  const forecast=state.snapshot?.forecast;
  const signature=JSON.stringify([forecast,state.day,state.offline]);
  if(!force && signature===state.forecastSignature)return;
  state.forecastSignature=signature;
  const day=getDay();const hours=Array.isArray(day?.hours)?day.hours:[];
  $('#forecast-description').textContent=day?`${day.label || (state.day==='today'?'Today':'Tomorrow')}, ${day.date || ''}, ${state.snapshot?.site?.timezone || 'site-local time'}`:'Forecast unavailable. Check site conditions.';
  const windows=day?.windows || day?.red_windows || [];
  const window=$('#risk-window');
  window.classList.toggle('red-window',windows.length>0 && !state.offline && !forecast?.stale);
  window.classList.toggle('neutral-window',state.offline || forecast?.stale || !hours.length);
  const windowText=state.offline?'Offline. Check site conditions.':forecast?.stale?'Forecast out of date. Check site conditions.':windows.length?windows.map(item=>`${state.day==='today'?'Today':'Tomorrow'} ${windowTime(item.start)}–${windowTime(item.end)}: ${(item.label || 'High heat risk').replace(/high-risk scenario window/i,'High heat risk')}`).join(', '):hours.length?'No red periods forecast. Check conditions before starting work.':'No forecast available for this day. Use the manual site assessment.';
  window.innerHTML=`${icon(windows.length?'warning':'clock')}<span>${esc(windowText)}</span>`;
  const container=$('#forecast-hours');const previousScroll=$('.forecast-scroll').scrollLeft;
  container.replaceChildren();
  if(!hours.length){container.innerHTML='<div class="empty-state"><strong>Forecast unavailable</strong>There are no verified hours for this day. Check conditions locally.</div>';}
  hours.forEach((hour,index)=>{
    const level=forecastLevel(hour);const label=hour.label || hour.hour || stamp(hour.time);
    const temp=typeof hour.temperature_c==='number'?`${Math.round(hour.temperature_c)}°`:'N/A';
    const wrapper=document.createElement('ui-button');const button=document.createElement('button');
    button.type='button';button.className=`hour-card ${level}`;button.setAttribute('aria-label',`${label}, ${statusLabel(level)}, ${temp}`);
    button.innerHTML=`<span class="hour-label">${esc(label)}</span><span class="weather-symbol" aria-hidden="true">${level==='unknown'?'N/A':icon('sun')}</span><strong>${esc(temp)}</strong><span class="heat-label">${level==='unknown'?'Unknown':level[0].toUpperCase()+level.slice(1)}</span><span class="heat-bar" aria-hidden="true"></span>`;
    wrapper.append(button);container.append(wrapper);onAction(button,()=>detailHour(index));
  });
  $('.forecast-scroll').scrollLeft=previousScroll;
  $('#forecast-provenance').textContent=`Sample forecast${forecast?.fetched_at?`, Updated ${stamp(forecast.fetched_at,{day:'numeric',month:'short'})}`:''}`;
  if(hours.length)detailHour(Math.min(state.hour??Math.min(8,hours.length-1),hours.length-1));
}
function renderCrews() {
  const groups=state.snapshot?.groups || [];
  const crewList=$('#crew-list'),suggestions=$('#suggestions-list');
  crewList.replaceChildren();suggestions.replaceChildren();
  if(!groups.length){
    crewList.innerHTML=`<div class="empty-state">${icon('people')}<strong>Your crews will appear here</strong>Add a crew and assign watches in Site setup.</div>`;
    suggestions.innerHTML=`<div class="empty-state">${icon('clock')}<strong>No crew context yet</strong>Add a crew to see recommendations. Keep water and shade available.</div>`;
    return;
  }
  groups.forEach(group=>{
    const level=cautionLevel(group);const valid=Number(group.valid_contributors ?? group.fresh_contributors ?? 0);const total=Number(group.total_workers ?? group.expected_workers ?? 0);
    const suppressed=group.suppressed || valid<3 || !group.counts;
    const name=group.name || 'Privacy group';
    const row=document.createElement('wa-card');row.className=`crew-row ${level}`;row.dataset.groupId=group.id;
    const fresh=secondsOld(group.updated_at)<=120 && !state.offline && valid>=3 && valid===total && !(group.counts?.unknown>0) && !['stale','invalid','unknown','incomplete','insufficient'].includes(group.data_quality);
    row.innerHTML=`<div class="crew-row-header"><div class="crew-name"><span class="crew-icon">${icon('people')}</span><div><h3>${esc(name)}</h3><div class="crew-subtitle">${esc(total)} expected, ${esc(valid)} valid contributors</div></div></div><wa-badge class="status-pill" pill appearance="filled" variant="${level==='green'?'success':level==='red'?'danger':'warning'}">${esc(statusLabel(level))}</wa-badge></div>${suppressed?'<p class="suppressed-note">Not enough readings. Counts are hidden.</p>':`<div class="count-strip">${['green','amber','red','unknown'].map(key=>`<span class="count-item"><i class="dot ${key}"></i><strong>${esc(group.counts[key]??0)}</strong>${key[0].toUpperCase()+key.slice(1)}</span>`).join('')}</div>`}${group.help_active?`<div class="help-marker">${icon('help')} Help requested. Follow site procedure.</div>`:''}<div class="crew-row-foot"><span>${fresh?'Last valid sample':'Caution: last valid sample'} ${esc(age(group.updated_at))}<br>Server received ${esc(age(group.received_at))}</span><span>${state.offline?'Offline':fresh?'Fresh coverage':`Stale / incomplete`}<br>${esc(valid)} / ${esc(total)} contributors</span></div>`;
    crewList.append(row);
    const suggestion=group.suggestion || {};
    const caution=state.offline || !fresh || suppressed;
    const title=group.help_active?'Respond to the help request':caution?'Check site conditions':suggestion.title || 'Review the next task window';
    const action=group.help_active?'Follow the site emergency procedure. Confirm the worker has received help.':caution?'Check the crew phone and assess heat on site. Make sure shade and drinking water are available.':suggestion.action || 'Review upcoming heat before assigning heavier tasks; keep shade, water and task rotation available.';
    const item=document.createElement('wa-card');item.className=`suggestion-row ${level}`;
    item.innerHTML=`<div class="suggestion-topline"><span>${esc(name)}</span><span class="window-label">${icon('clock')} ${esc(caution?'Check now':planningWindow(suggestion.window))}</span></div><h3>${esc(title)}</h3><p>${esc(action)}</p><div class="suggestion-reason">${esc(caution?'Readings incomplete or out of date.':'Based on the forecast and latest crew readings.')}</div>`;
    suggestions.append(item);
  });
}
function renderEmergencies() {
  const events=(state.snapshot?.emergencies || []).filter(row=>!row.acknowledged);
  const signature=JSON.stringify([events,[...state.ackErrors],[...state.pendingAcks],state.offline]);
  if(signature===state.emergencySignature)return;state.emergencySignature=signature;
  const region=$('#emergency-region');region.replaceChildren();
  events.sort((a,b)=>String(a.occurred_at || '').localeCompare(String(b.occurred_at || ''))).forEach(event=>{
    const row=document.createElement('wa-card');row.className='emergency-banner';row.dataset.eventId=event.id;
    const id=String(event.id);const pending=state.pendingAcks.has(id);
    const occurrence=event.occurrence_time_unverified || !event.occurred_at?'Occurrence time unverified':`Occurred ${stamp(event.occurred_at,{day:'numeric',month:'short'})}`;
    row.innerHTML=`<div class="emergency-icon">${icon('help')}</div><div class="emergency-content"><span class="emergency-new">WORKER HELP REQUEST${state.offline?': DELIVERY STATUS UNVERIFIED':''}</span><h2>${esc(event.worker_name || 'Unassigned watch, help requested')}<span class="delayed-label" ${event.delayed?'':'hidden'}>Delayed delivery</span></h2><p>${esc(event.crew_name || 'Authorized crew')}, Use the site emergency procedure and seek urgent help directly.</p><div class="emergency-times">${esc(occurrence)}, Received ${esc(stamp(event.received_at,{day:'numeric',month:'short'}))}${event.resolved_at?', Device reports local resolution; receipt still needs acknowledgement.':''}</div>${state.ackErrors.has(id)?`<p class="ack-error">${esc(state.ackErrors.get(id))}</p>`:''}</div>`;
    const wrapper=document.createElement('ui-button');wrapper.setAttribute('pending-announcement','Acknowledging receipt');
    const button=document.createElement('button');button.type='button';button.className='button';button.setAttribute('aria-label',`Acknowledge help from ${event.worker_name || 'unassigned watch'}`);button.textContent=pending?'Confirming receipt…':'Acknowledge receipt';
    wrapper.disabled=pending;wrapper.append(button);row.append(wrapper);region.append(row);onAction(button,()=>acknowledge(id));
  });
}
async function acknowledge(id) {
  if(state.pendingAcks.has(id))return;
  state.pendingAcks.add(id);state.ackErrors.delete(id);renderEmergencies();
  const epoch=state.epoch;
  try {
    await api(`/api/v1/emergencies/${encodeURIComponent(id)}/ack`,{});
    if(epoch!==state.epoch)return;
    notify('Receipt acknowledged. The crew help state may remain active.');
    await refreshDashboard();
  } catch(error) {if(epoch===state.epoch)state.ackErrors.set(id,`Not confirmed: ${error.message} The request remains unacknowledged.`);}
  finally {state.pendingAcks.delete(id);if(epoch===state.epoch)renderEmergencies();}
}
function render() {renderSite();renderConnection();renderEmergencies();renderForecast();renderCrews();}
async function refreshDashboard() {
  if(!state.user || state.busy)return;
  state.busy=true;const epoch=state.epoch;const site=state.site;
  try {
    const snapshot=await api(`/api/v1/sites/${encodeURIComponent(site)}/dashboard`);
    if(epoch!==state.epoch || site!==state.site)return;
    state.snapshot=snapshot;state.offline=false;render();
  } catch(error) {
    if(epoch!==state.epoch || !state.user)return;
    state.offline=true;renderConnection();renderForecast();renderCrews();renderEmergencies();
    if(!state.snapshot)$('#connection-warning').textContent=`No verified site snapshot is available. ${error.message} No green or zero-worker status is inferred.`;
  } finally {if(epoch===state.epoch)state.busy=false;}
}
async function changeSite(id) {
  if(!id || id===state.site)return;
  state.epoch++;state.site=id;state.snapshot=null;state.setup=null;state.ackErrors.clear();state.pendingAcks.clear();state.forecastSignature='';state.emergencySignature='';state.hour=null;state.streamLive=false;
  stopStream();startStream();
  $('#emergency-region').replaceChildren();$('#crew-list').innerHTML='<div class="empty-state">Loading the selected site…</div>';$('#suggestions-list').replaceChildren();$('#forecast-hours').replaceChildren();$('#hour-detail').textContent='Waiting for authorized site data.';
  state.busy=false;await refreshDashboard();
}
function renderSetup(data) {
  state.setup=data;
  const site=data.site || state.snapshot?.site || {};
  setInput('setup-site-name',site.name || '');setInput('setup-latitude',String(site.latitude ?? ''));setInput('setup-longitude',String(site.longitude ?? ''));setInput('setup-timezone',site.timezone || 'Africa/Accra');
  const crews=data.crews || [];
  $('#setup-crews').innerHTML=crews.length?crews.map(crew=>`<div class="admin-row"><div><strong>${esc(crew.name)}</strong><small>${esc(crew.count ?? crew.worker_count ?? crew.expected_workers ?? 0)} expected workers</small></div><div class="crew-admin-actions"><ui-button><button class="text-button edit-crew" data-crew-id="${esc(crew.id)}" data-crew-name="${esc(crew.name)}" data-crew-count="${esc(crew.count)}" aria-label="Edit ${esc(crew.name)}">Edit</button></ui-button><ui-button><button class="text-button remove-crew" data-crew-id="${esc(crew.id)}" data-crew-name="${esc(crew.name)}" aria-label="Remove ${esc(crew.name)}">Remove</button></ui-button></div></div>`).join(''):'<div class="setup-info">No crews yet. Create your first crew below.</div>';
  setSelect('assignment-crew',crews.map(crew=>({value:String(crew.id),label:crew.name})),crews[0]?.id);
  $('#setup-assignments').innerHTML=(data.assignments || []).map(item=>`<div class="admin-row"><div><strong>${esc(item.worker_name || 'Unassigned')}</strong><br><small>${esc(crews.find(crew=>crew.id===item.crew_id)?.name || item.crew_name || item.crew_id)}</small></div><small>${esc(item.watch_id)}</small></div>`).join('') || '<div class="setup-info">No watch assignments yet.</div>';
}
async function loadSetup() {
  $('#setup-load-error').textContent='';
  try {renderSetup(await api(`/api/v1/sites/${encodeURIComponent(state.site)}/setup`));}
  catch(error){$('#setup-load-error').textContent=error.message;}
}
async function saveForm(formId,errorId,path,body,method,success) {
  const form=$(formId);if(!form.reportValidity())return;
  $(errorId).textContent='';
  try {
    await api(path,body(),method);notify(success);await loadSetup();await refreshDashboard();
  } catch(error){$(errorId).textContent=`Not saved: ${error.message}`;}
}
function wireActions() {
  onAction('#fill-demo',()=>{setInput('login-email','demo@exaclim.test');setInput('login-password','Exaclim2026!');});
  onAction('#submit-login',signIn);
  $('#login-form').addEventListener('submit',event=>event.preventDefault());
  onAction('#create-site',async()=>{
    const form=$('#site-create-form');if(!form.reportValidity())return;
    $('#site-create-error').textContent='';
    try {
      const result=await api('/api/v1/sites',{name:inputValue('new-site-name'),latitude:Number(inputValue('new-site-latitude')),longitude:Number(inputValue('new-site-longitude')),timezone:inputValue('new-site-timezone')});
      state.user.site_ids=[...new Set([...(state.user?.site_ids||[]),result.site.id])];
      setInput('new-site-name','');$('#toast').hidden=false;notify(`Site "${result.site.name}" created. Select it from the switcher.`);
      await loadSetup();await refreshDashboard();
    } catch(error){$('#site-create-error').textContent=`Not saved: ${error.message}`;}
  });
  $('#site-create-form').addEventListener('submit',event=>event.preventDefault());
  $('#setup-crews').addEventListener('click',async event=>{
    const button=event.target.closest('button');
    if(!button)return;
    if(button.classList.contains('edit-crew')) {
      setInput('new-crew-name',button.dataset.crewName||'');setInput('new-crew-count',button.dataset.crewCount||'3');
      state.editingCrew=button.dataset.crewId;$('#crew-form-title').textContent=`Edit crew: ${button.dataset.crewName}`;
      $('#cancel-crew-edit').hidden=false;
    } else if(button.classList.contains('remove-crew')) {
      $('#crew-error').textContent='';
      try {await api(`/api/v1/sites/${encodeURIComponent(state.site)}/crews/${encodeURIComponent(button.dataset.crewId)}`,{},'DELETE');notify('Crew removed');await loadSetup();await refreshDashboard();}
      catch(error){$('#crew-error').textContent=`Not removed: ${error.message}`;}
    }
  });
  onAction('#cancel-crew-edit',()=>{state.editingCrew=null;setInput('new-crew-name','');setInput('new-crew-count','3');$('#crew-form-title').textContent='New crew';$('#cancel-crew-edit').hidden=true;$('#crew-error').textContent='';});
  $('#user-menu').addEventListener('action',async event=>{
    if(event.detail.value==='signout'){try{await api('/api/v1/auth/logout',{});clearAuthenticated();notify('Signed out.');}catch(error){notify(`Sign out not confirmed: ${error.message}`);}}
    else if(event.detail.value==='setup'){await loadSetup();$('#setup-dialog').open=true;}
  });
  onAction('#open-setup',async()=>{await loadSetup();$('#setup-dialog').open=true;});
  onAction('#open-demo',()=>{$('#demo-dialog').open=true;});
  onAction('#refresh-dashboard',refreshDashboard);
  $('#site-select').addEventListener('valuechange',event=>changeSite(event.detail.value));
  $('#forecast-tabs').addEventListener('valuechange',event=>{state.day=event.detail.value;state.hour=null;renderForecast(true);});
  onAction('#save-site',()=>saveForm('#site-form','#site-error',`/api/v1/sites/${encodeURIComponent(state.site)}`,()=>({name:inputValue('setup-site-name'),latitude:Number(inputValue('setup-latitude')),longitude:Number(inputValue('setup-longitude')),timezone:inputValue('setup-timezone')}),'PATCH','Site details saved'));
  onAction('#create-crew',async()=>{
    const editing=state.editingCrew;
    if(editing) {
      $('#crew-error').textContent='';
      try {await api(`/api/v1/sites/${encodeURIComponent(state.site)}/crews/${encodeURIComponent(editing)}`,{name:inputValue('new-crew-name'),count:Number(inputValue('new-crew-count'))},'PATCH');notify('Crew updated');state.editingCrew=null;setInput('new-crew-name','');setInput('new-crew-count','3');$('#crew-form-title').textContent='New crew';$('#cancel-crew-edit').hidden=true;await loadSetup();await refreshDashboard();}
      catch(error){$('#crew-error').textContent=`Not saved: ${error.message}`;}
    } else await saveForm('#crew-form','#crew-error',`/api/v1/sites/${encodeURIComponent(state.site)}/crews`,()=>({name:inputValue('new-crew-name'),count:Number(inputValue('new-crew-count'))}),'POST','Crew created');
  });
  onAction('#save-assignment',()=>saveForm('#assignment-form','#assignment-error',`/api/v1/sites/${encodeURIComponent(state.site)}/assignments`,()=>({crew_id:inputValue('assignment-crew'),worker_name:inputValue('assignment-name'),watch_id:inputValue('assignment-watch')}),'POST','Watch assignment saved'));
  ['#site-form','#crew-form','#assignment-form'].forEach(id=>$(id).addEventListener('submit',event=>event.preventDefault()));
  const list=$('#demo-scenarios');
  scenarios.forEach(([scenario,title,description])=>{
    const wrapper=document.createElement('ui-button');const button=document.createElement('button');button.className='scenario-button';button.type='button';button.dataset.scenario=scenario;
    button.innerHTML=`<strong>${esc(title)}</strong><span data-show="idle">${esc(description)}</span><span data-show="pending">Applying scenario…</span>`;
    wrapper.append(button);list.append(wrapper);
    onAction(button,async()=>{
      $('#demo-error').textContent='';
      try {await api(`/api/v1/sites/${encodeURIComponent(state.site)}/simulate`,{scenario});await refreshDashboard();notify(scenario==='help'?'Help request added. Offline requests arrive after reconnection.':`${title} applied`);}
      catch(error){$('#demo-error').textContent=error.message;}
    });
  });
}
async function initialize() {
  wireActions();
  try {const result=await api('/api/v1/auth/me');state.user=result.user;state.site=state.user?.site_ids?.[0] || 'accra';showAuthenticated();await refreshDashboard();startStream();}
  catch {$('#login-page').hidden=false;}
  setInterval(()=>{if(state.user && !document.hidden && navigator.onLine && !state.streamLive)refreshDashboard();},1000);
  setInterval(()=>{if(state.user && state.snapshot){renderConnection();renderCrews();}},1000);
  window.addEventListener('offline',()=>{state.offline=true;if(state.user)render();});
  window.addEventListener('online',()=>{refreshDashboard();resetStream();});
}
let streamSource=null,streamBackoff=1000,streamTimer=null;
function startStream() {
  if(!state.user||!window.EventSource)return;
  stopStream();
  const site=encodeURIComponent(state.site),source=new EventSource(`/api/v1/sites/${site}/events`);
  streamSource=source;
  source.addEventListener('open',()=>{state.streamLive=true;state.offline=false;streamBackoff=1000;renderConnection();});
  source.addEventListener('dashboard',event=>{
    try {
      const detail=JSON.parse(event.data);
      if(detail.new_emergency){refreshDashboard();notify('New help request received');}
      else if(!document.hidden)refreshDashboard();
    } catch {/* malformed event; polling continues */}
  });
  source.onerror=()=>{state.streamLive=false;renderConnection();stopStream();streamBackoff=Math.min(streamBackoff*2,30000);streamTimer=setTimeout(startStream,streamBackoff);};
}
function stopStream() {if(streamSource){streamSource.close();streamSource=null;}if(streamTimer){clearTimeout(streamTimer);streamTimer=null;}}
function resetStream() {state.streamLive=false;streamBackoff=1000;if(state.user)startStream();}
initialize();
