import './styles.css';
import { agent, getValue, setValue, onAction } from './components/ui.js';

globalThis.exaclim = Object.freeze({ agent });
const $ = selector => document.querySelector(selector);
const levels = ['green', 'amber', 'red', 'emergency'];
let worker = null;
let pendingEmergency = sessionStorage.getItem('exaclim_pending_emergency') === 'true';
let busy = false;
const frenchMessages = {
  green: 'Suivez le plan du site pour l’eau et les pauses. Signalez tout malaise.',
  amber: 'Faites une pause à l’ombre, réduisez l’effort et vérifiez le plan du site.',
  red: 'Arrêtez la tâche. Rejoignez un endroit plus frais et prévenez le responsable de sécurité.',
  emergency: 'Déclenchez la procédure d’urgence du site et demandez une aide urgente. Ne laissez pas la personne seule.'
};
function updateTranslation() {
  const node = $('#translated-action');
  node.hidden = getValue('language') !== 'fr';
  node.textContent = frenchMessages[worker?.level || 'amber'];
}
const events = [];

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
async function api(path, body) {
  const options = {credentials: 'same-origin', headers: {'Accept': 'application/json'}};
  if (body !== undefined) {
    options.method = 'POST';
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  const controller = new AbortController();
  options.signal = controller.signal;
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, options);
    if (!response.ok) throw new Error(`Request failed (${response.status})`);
    const data = await response.json();
    $('#connection-label').textContent = 'Local simulator connected';
    return data;
  } finally { clearTimeout(timeout); }
}
function log(message) {
  events.unshift(`${new Date().toLocaleTimeString('en-GB', {timeZone: 'UTC', hour12: false})} UTC · ${message}`);
  const list = $('#event-log');
  list.replaceChildren(...events.slice(0, 25).map(item => element('li', '', item)));
}
function paintWorker(result, allowReset = false) {
  if (!allowReset && (pendingEmergency || worker?.level === 'emergency') && result.level !== 'emergency') {
    result = {...result, level: 'emergency', action: 'Emergency remains latched. Use the site emergency procedure; check whether help has been reached directly.'};
  }
  worker = result;
  updateTranslation();
  const level = levels.includes(result.level) ? result.level : 'amber';
  const score = Number(result.score);
  $('#badge-device').dataset.level = level;
  $('#badge-level').textContent = level === 'emergency' ? 'EMERGENCY · HELP' : level.toUpperCase();
  const scoreNode = $('#badge-score');
  scoreNode.replaceChildren(document.createTextNode(Number.isFinite(score) && result.score !== null ? String(Math.round(score)) : '—'), element('small', '', '/ 100'));
  $('#exposure-meter').value = Number.isFinite(score) ? Math.max(0, Math.min(100, score)) : 0;
  $('#badge-action').textContent = result.action || 'Check conditions and follow the site procedure.';
  const quality = typeof result.data_quality === 'object' ? JSON.stringify(result.data_quality) : (result.data_quality || 'unknown');
  $('#data-quality').textContent = `Data quality: ${quality}`;
  const reasons = Array.isArray(result.reasons) ? result.reasons : [];
  $('#risk-reasons').replaceChildren(...reasons.map(reason => element('li', '', String(reason))));
  const projection = result.forecast;
  const crossing = projection?.minutes_to_illustrative_red;
  $('#worker-projection').textContent = projection?.status === 'available'
    ? (crossing !== null && crossing !== undefined ? `Synthetic look-ahead: illustrative red threshold crossed at +${crossing} minutes. This is not time to illness or a safe work allowance.` : 'Synthetic look-ahead calculated; no red threshold crossing in the scenario horizon. This does not establish safety.')
    : 'No forecast projection available. Current conditions remain the baseline.';
}
function cautiousFallback(message, emergency = false) {
  $('#connection-label').textContent = 'Connection interrupted · cautious local display';
  const previous = levels.indexOf(worker?.level);
  const level = emergency || worker?.level === 'emergency' ? 'emergency' : previous >= 2 ? 'red' : 'amber';
  paintWorker({
    ...(worker || {}), level,
    data_quality: 'offline — last result retained; current conditions unverified',
    reasons: [message, 'Local display cannot confirm delivery to another person.'],
    action: level === 'emergency' ? 'Use the site emergency procedure now. Seek help directly; delivery is not confirmed.' : 'Data unavailable. Pause and check conditions; follow the site fallback procedure.'
  });
  log(`${level.toUpperCase()} · ${message}`);
}
function payload() {
  const keys = ['temperature_c', 'humidity_pct', 'workload', 'clothing', 'acclimatized', 'duration_minutes', 'sensor_age_seconds', 'use_forecast'];
  return {
    ...Object.fromEntries(keys.map(key => [key, getValue(key)])),
    emergency: pendingEmergency || worker?.level === 'emergency',
  };
}
async function workerRequest(path, data, message, emergency = false) {
  if (busy && !emergency) return;
  if (emergency) {
    pendingEmergency = true;
    sessionStorage.setItem('exaclim_pending_emergency', 'true');
    cautiousFallback('Help requested. Contact site responders directly; network delivery is being checked.', true);
  }
  busy = true;
  const buttons = [...$('#tab-worker').querySelectorAll('ui-button')];
  buttons.forEach(button => { button.disabled = !button.querySelector('#emergency'); });
  try {
    const result = await api(path, data);
    if (path === '/api/reset') {
      pendingEmergency = false;
      sessionStorage.removeItem('exaclim_pending_emergency');
    } else if (path === '/api/emergency' && result.level === 'emergency') {
      pendingEmergency = false;
      sessionStorage.removeItem('exaclim_pending_emergency');
    }
    paintWorker(result, path === '/api/reset');
    log(`${message} · ${result.level.toUpperCase()}`);
  } catch (error) {
    cautiousFallback(`${message}: server response unavailable.`, emergency);
  } finally {
    busy = false;
    buttons.forEach(button => { button.disabled = false; });
  }
}
async function loadCrew() {
  const size = Math.max(1, Math.min(100, getValue('crew_size') ?? 8));
  setValue('crew_size', size);
  try {
    const data = await api(`/api/crew?size=${size}`);
    const counts = $('#crew-counts');
    counts.replaceChildren();
    if (data.suppressed || size < 5) {
      $('#crew-summary').className = 'suppressed';
      $('#crew-summary').textContent = 'Crew information withheld. At least five consenting workers are required for this aggregate view.';
      $('#crew-recommendation').textContent = 'No small-crew status is shown. Use general site precautions and the local site safety procedure.';
      return;
    }
    $('#crew-summary').className = '';
    $('#crew-summary').textContent = `${data.crew_size ?? size} synthetic workers · independent demonstration fixture`;
    levels.forEach(level => {
      const cell = element('div', `status-cell ${level}`);
      cell.append(element('strong', '', String(data.counts?.[level] ?? 0)), element('span', '', level === 'emergency' ? 'Emergency' : level[0].toUpperCase() + level.slice(1)));
      counts.append(cell);
    });
    $('#crew-recommendation').textContent = data.recommendation || 'Review the forecast before assigning heavier tasks. Arrange shade, water and site-approved rest controls.';
  } catch (error) {
    $('#connection-label').textContent = 'Connection interrupted · crew data unavailable';
    $('#crew-counts').replaceChildren();
    $('#crew-summary').className = 'suppressed';
    $('#crew-summary').textContent = 'Current crew information unavailable. No reassuring status is inferred from lost data.';
    $('#crew-recommendation').textContent = 'Follow the site fallback procedure and check conditions directly.';
  }
}
async function loadForecast(mode = 'fixture') {
  try {
    const data = await api(mode === 'live' ? '/api/forecast?mode=live' : '/api/forecast');
    const hours = Array.isArray(data.hourly) ? data.hourly : [];
    const source = data.source || 'Unknown source';
    $('#forecast-source').textContent = `${source} · ${data.status || 'source status unreported'}${data.fetched_at ? ` · fetched ${data.fetched_at}` : ''}${data.error ? ` · ${data.error}` : ''}`;
    $('#forecast-chart').replaceChildren(...hours.slice(0, 8).map(item => {
      const temperature = Number(item.temperature_c);
      const node = element('div', `forecast-hour ${temperature >= 34 ? 'hot' : temperature >= 30 ? 'warm' : ''}`);
      const bar = element('div', 'forecast-bar');
      bar.style.setProperty('--bar-height', `${Math.max(15, Math.min(100, (temperature - 18) * 5))}px`);
      bar.setAttribute('aria-hidden', 'true');
      node.append(element('span', 'forecast-temp', Number.isFinite(temperature) ? `${temperature.toFixed(0)}°` : '—'), bar, element('span', 'forecast-time', String(item.hour || '—')), element('span', 'forecast-humidity', `${item.humidity_pct ?? '—'}% RH`));
      return node;
    }));
    if (!hours.length) $('#forecast-chart').append(element('p', 'error-note', 'No hourly forecast available. Follow the site fallback procedure.'));
    $('#forecast-limitation').textContent = data.limitation || 'Grid weather does not establish work-zone WBGT or personal heat strain.';
  } catch (error) {
    $('#forecast-source').textContent = 'Forecast unavailable · no current forecast claimed';
    $('#forecast-chart').replaceChildren(element('p', 'error-note', 'Check conditions locally. Lost forecast data does not imply low risk.'));
    $('#forecast-limitation').textContent = 'No live forecast could be obtained. Demonstration fixture and live weather must be distinguished.';
  }
}

$('#workspace-tabs').addEventListener('valuechange', event => {
  const titles = { crew: 'Crew overview', worker: 'Badge simulator', system: 'System & safeguards' };
  $('#view-title').textContent = titles[event.detail.value] || 'Workspace';
});
$('#worker-form').addEventListener('submit', event => {
  event.preventDefault();
  workerRequest('/api/evaluate', payload(), 'Evaluated synthetic conditions');
});
const presets = {
  normal: {temperature_c: 26, humidity_pct: 45, workload: 'light', clothing: 'ordinary', acclimatized: true, duration_minutes: 15, sensor_age_seconds: 0},
  hot: {temperature_c: 39, humidity_pct: 75, workload: 'heavy', clothing: 'protective', acclimatized: false, duration_minutes: 180, sensor_age_seconds: 0},
  stale: {temperature_c: 28, humidity_pct: 60, workload: 'moderate', clothing: 'ordinary', acclimatized: true, duration_minutes: 60, sensor_age_seconds: 900}
};
for (const button of document.querySelectorAll('[data-preset]')) {
  onAction(`#${button.id}`, () => {
    Object.entries(presets[button.dataset.preset]).forEach(([name, value]) => setValue(name, value));
    return workerRequest('/api/evaluate', payload(), `Applied ${button.textContent} scenario`);
  });
}
onAction('#acknowledge', () => workerRequest('/api/acknowledge', {}, 'Acknowledged alert; emergency state is not cleared'));
onAction('#emergency', () => workerRequest('/api/emergency', {}, 'Simulated help request; no external responder contacted', true));
$('#reset-dialog').addEventListener('openchange', event => {
  if (!event.detail.value && event.detail.returnValue === 'confirm') {
    workerRequest('/api/reset', {}, 'Explicit synthetic session reset');
  }
});
onAction('#refresh-crew', loadCrew);
onAction('#refresh-forecast', () => loadForecast());
onAction('#live-forecast', () => loadForecast('live'));
$('#field-language').addEventListener('valuechange', updateTranslation);
window.addEventListener('offline', () => {
  cautiousFallback('Browser reports no network. Current conditions unverified.');
  $('#crew-counts').replaceChildren();
  $('#crew-summary').className = 'suppressed';
  $('#crew-summary').textContent = 'Offline. Current crew status unavailable.';
});
async function refreshWorker() {
  if (busy) return;
  if (pendingEmergency) return workerRequest('/api/emergency', {}, 'Retrying latched synthetic help request', true);
  try { paintWorker(await api('/api/worker')); }
  catch (error) { cautiousFallback('Worker refresh unavailable; current conditions unverified.'); }
}
window.addEventListener('online', () => { refreshWorker(); loadCrew(); });
await Promise.all(['ui-tabs','ui-button','ui-number-input','ui-select','ui-checkbox','ui-switch','ui-meter','ui-alert-dialog'].map(tag => customElements.whenDefined(tag)));
for (const select of document.querySelectorAll('ui-select')) {
  select.items = [...select.querySelectorAll('ui-select-item')].map(item => ({ value: item.getAttribute('value'), label: item.textContent.trim() }));
}
const mobileNavigation = window.matchMedia('(max-width: 640px)');
const updateOrientation = () => { $('#workspace-tabs').orientation = mobileNavigation.matches ? 'horizontal' : 'vertical'; };
mobileNavigation.addEventListener('change', updateOrientation);
updateOrientation();
await new Promise(resolve => requestAnimationFrame(resolve));
Promise.allSettled([loadCrew(), loadForecast(), refreshWorker()]);
setInterval(refreshWorker, 15000);
