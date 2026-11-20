"""Synthetic Exaclim supervisor-domain logic; no physical or clinical claims."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from uuid import uuid4
import math

POLICY_VERSION = 'synthetic-dashboard-v1'
LEVELS = ('green', 'amber', 'red')
STALE_SECONDS = 120


def _now(value=None):
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError as exc:
            raise ValueError('Invalid timestamp') from exc
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError('Timestamp must include timezone')
    return value.astimezone(timezone.utc)


def _iso(value):
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def _text(value, label, limit=100):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise ValueError(f'{label} must be nonempty text, at most {limit} characters')
    if any(ord(c) < 32 for c in value):
        raise ValueError(f'{label} contains control characters')
    return value.strip()


def _site(state, site_id):
    if not isinstance(state, dict) or not isinstance(state.get('sites'), dict) or not isinstance(site_id, str) or site_id not in state['sites']:
        raise ValueError('Unknown site')
    return state['sites'][site_id]


def _crew(site, crew_id):
    for crew in site['crews']:
        if crew['id'] == crew_id:
            return crew
    raise ValueError('Unknown crew')


def add_site(state, name, lat, lon, timezone):
    name = _text(name, 'Site name')
    for value, minimum, maximum in ((lat, -90, 90), (lon, -180, 180)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not minimum <= value <= maximum or not math.isfinite(value):
            raise ValueError('Coordinates must be finite latitude/longitude')
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, TypeError, ValueError) as exc:
        raise ValueError('Unknown IANA timezone') from exc
    if not isinstance(state, dict) or not isinstance(state.get('sites'), dict):
        raise ValueError('Invalid state')
    site_id = str(uuid4())
    site = {'id': site_id, 'name': name, 'latitude': float(lat), 'longitude': float(lon),
            'timezone': timezone, 'crews': [], 'assignments': [], 'samples': {}, 'events': [],
            'scenario': 'normal', 'forecast_generated_at': _iso(_now()),
            'gateway_connected': True, 'pending_events': []}
    state['sites'][site_id] = site
    return dict(site)


def add_crew(state, site_id, name, count):
    site = _site(state, site_id)
    name = _text(name, 'Crew name')
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 20:
        raise ValueError('Crew count must be an integer from 1 to 20')
    if len(site['crews']) >= 10:
        raise ValueError('Demo supports at most 10 crews per site')
    if any(c['name'].casefold() == name.casefold() for c in site['crews']):
        raise ValueError('Crew name already exists')
    crew = {'id': str(uuid4()), 'name': name, 'count': count, 'watch_ids': []}
    site['crews'].append(crew)
    return dict(crew)


def assign_watch(state, site_id, crew_id, worker_name, watch_id):
    site = _site(state, site_id)
    crew = _crew(site, crew_id)
    worker_name = _text(worker_name, 'Worker name')
    watch_id = _text(watch_id, 'Watch ID', 64)
    if any(a['watch_id'].casefold() == watch_id.casefold() for s in state['sites'].values() for a in s['assignments']):
        raise ValueError('Watch already has an active assignment')
    if len(crew['watch_ids']) >= crew['count']:
        raise ValueError('Crew roster is full')
    assignment = {'id': str(uuid4()), 'crew_id': crew_id, 'worker_name': worker_name,
                  'watch_id': watch_id, 'version': 1, 'assigned_at': _iso(_now())}
    site['assignments'].append(assignment)
    crew['watch_ids'].append(watch_id)
    # Issuance is not a measurement. New watch stays Unknown until a simulated sample.
    return dict(assignment)


def initial_state(now=None):
    clock = _now(now)
    state = {'schema_version': 1, 'sites': {}}
    site = {'id': 'accra', 'name': 'Accra Construction Site', 'latitude': 5.6037,
            'longitude': -.187, 'timezone': 'Africa/Accra', 'crews': [], 'assignments': [],
            'samples': {}, 'events': [], 'scenario': 'normal', 'forecast_generated_at': _iso(clock),
            'gateway_connected': True, 'pending_events': []}
    state['sites']['accra'] = site
    names = iter(['Ama Mensah', 'Kofi Owusu', 'Akosua Boateng', 'Kwame Asare', 'Abena Osei',
                  'Yaw Addo', 'Efua Arthur', 'Kojo Agyeman'])
    for label, count in [('Concrete crew', 5), ('Roofing crew', 2), ('Lifting crew', 1)]:
        crew = add_crew(state, 'accra', label, count)
        for _ in range(count):
            assignment = assign_watch(state, 'accra', crew['id'], next(names), f'DEMO-{len(site["assignments"])+1:03d}')
            site['assignments'][-1]['assigned_at'] = _iso(clock)
    scenario(state, 'accra', 'normal', clock)
    state['sites']['tema'] = {'id': 'tema', 'name': 'Tema Construction Site', 'latitude': 5.6698,
        'longitude': -.0166, 'timezone': 'Africa/Accra', 'crews': [], 'assignments': [],
        'samples': {}, 'events': [], 'scenario': 'normal', 'forecast_generated_at': _iso(clock),
            'gateway_connected': True, 'pending_events': []}
    return state


def _groups(site):
    small = [c for c in site['crews'] if c['count'] < 3]
    eligible = [c for c in site['crews'] if c['count'] >= 3]
    groups, pending = [], []
    for crew in small:
        pending.append(crew)
        if sum(c['count'] for c in pending) >= 3:
            groups.append(pending)
            pending = []
    if pending:
        if eligible:
            pending.append(eligible.pop(0))
            groups.append(pending)
        elif groups:
            groups[-1].extend(pending)
        else:
            groups.append(pending)
    groups.extend([[crew] for crew in eligible])
    return groups


def _forecast(site, clock):
    zone = ZoneInfo(site['timezone'])
    local_today = clock.astimezone(zone).date()
    forecast_age = (clock - _now(site['forecast_generated_at'])).total_seconds()
    forecast_stale = forecast_age > 6 * 3600 or forecast_age < 0
    days = []
    for offset in range(2):
        date = local_today + timedelta(days=offset)
        start = datetime.combine(date, datetime.min.time(), zone).astimezone(timezone.utc)
        end = datetime.combine(date + timedelta(days=1), datetime.min.time(), zone).astimezone(timezone.utc)
        hours, windows, window = [], [], None
        instant = start
        while instant < end:
            local = instant.astimezone(zone)
            hour = local.hour
            temperature = round(26 + max(0, math.sin((hour - 6) * math.pi / 14)) * 9 + offset * .5, 1)
            risk = 'red' if 11 <= hour < 15 else 'amber' if 9 <= hour < 17 else 'green'
            row = {'start': _iso(instant), 'end': _iso(instant + timedelta(hours=1)),
                   'local_time': local.isoformat(), 'label': local.strftime('%H:%M %z'),
                   'risk': risk, 'temperature_c': temperature, 'humidity_pct': 65,
                   'source_type': 'synthetic', 'data_quality': 'stale' if forecast_stale else 'synthetic',
                   'caution': forecast_stale, 'display_risk': 'unknown' if forecast_stale else risk}
            hours.append(row)
            if risk == 'red' and window is None:
                window = {'start': row['start'], 'end': row['end'], 'start_local': local.isoformat(),
                          'end_local': (instant + timedelta(hours=1)).astimezone(zone).isoformat()}
            elif risk == 'red':
                window['end'] = row['end']
                window['end_local'] = (instant + timedelta(hours=1)).astimezone(zone).isoformat()
            elif window:
                windows.append(window)
                window = None
            instant += timedelta(hours=1)
        if window:
            windows.append(window)
        days.append({'date': date.isoformat(), 'label': 'Today' if offset == 0 else 'Tomorrow',
                     'hours': hours, 'red_windows': windows, 'windows': windows})
    return {'source': 'Synthetic scenario forecast — not live weather', 'source_type': 'synthetic',
            'provider': 'Exaclim simulator', 'generated_at': site['forecast_generated_at'],
            'stale': forecast_stale, 'age_seconds': max(0, forecast_age),
            'data_quality': 'stale' if forecast_stale else 'synthetic',
            'provider_issue_time': None, 'timezone': site['timezone'],
            'latitude': site['latitude'], 'longitude': site['longitude'], 'days': days,
            'policy_version': POLICY_VERSION, 'limitations': 'Illustrative heat labels; not WBGT or clinical thresholds.'}


def snapshot(state, site_id='accra', now=None):
    site, clock = _site(state, site_id), _now(now)
    forecast = _forecast(site, clock)
    groups, suggestions = [], []
    for crews in _groups(site):
        ids = [c['id'] for c in crews]
        watch_ids = [w for c in crews for w in c['watch_ids']]
        expected = sum(c['count'] for c in crews)
        fresh, known, samples = [], [], []
        for watch in watch_ids:
            sample = site['samples'].get(watch)
            if not isinstance(sample, dict):
                continue
            level = sample.get('level')
            if level not in LEVELS:
                continue
            known.append(level)
            try:
                measured = _now(sample['sampled_at'])
                received = _now(sample['received_at'])
            except (KeyError, ValueError):
                continue
            samples.append((measured, received))
            age = (clock - measured).total_seconds()
            if 0 <= age <= STALE_SECONDS and received <= clock:
                fresh.append(sample)
        unknown = max(0, expected - len(fresh))
        suppressed = len(fresh) < 3 or expected < 3
        heat_state = max(known, key=LEVELS.index, default='amber')
        if unknown or suppressed:
            heat_state = max((heat_state, 'amber'), key=LEVELS.index)
        active = [e for e in site['events'] if e['crew_id'] in ids and not e.get('resolved_at')]
        overall = 'red' if active else heat_state
        counts = None if suppressed else {level: sum(s['level'] == level for s in fresh) for level in LEVELS}
        # This is an explicitly synthetic GROUP fixture; no individual budget is stored.
        budget = {'green': 20, 'amber': 55, 'red': 85}[heat_state] if not suppressed and not unknown else None
        group_id = 'group-' + '-'.join(ids)
        group = {'id': group_id, 'name': ' + '.join(c['name'] for c in crews), 'crew_ids': ids,
                 'expected_contributors': expected, 'fresh_contributors': len(fresh), 'unknown_contributors': unknown,
                 'counts': counts, 'budget': budget, 'state': overall, 'heat_state': heat_state,
                 'help_active': bool(active), 'suppressed': suppressed,
                 'status_message': 'Group status unavailable — insufficient contributors' if suppressed else
                    'Help state active' if active else 'Caution — incomplete or stale data' if unknown else 'Fresh simulated crew summary',
                 'last_sample_at': _iso(max(s[0] for s in samples)) if samples else None,
                 'last_received_at': _iso(max(s[1] for s in samples)) if samples else None}
        group.update(level=overall, total_workers=expected, valid_contributors=len(fresh),
                     updated_at=group['last_sample_at'], received_at=group['last_received_at'],
                     data_quality='insufficient' if suppressed else 'stale' if unknown else 'synthetic',
                     budget_source='Synthetic group-level illustration; not individual watch data')
        groups.append(group)
        future_windows = [w for d in forecast['days'] for w in d['red_windows'] if _now(w['end']) > clock]
        next_window = future_windows[0] if future_windows and not forecast['stale'] else None
        if active:
            advice = 'Follow the site emergency procedure. Acknowledgement confirms receipt, not resolution.'
        elif overall == 'red':
            advice = 'Pause the affected task; arrange cooling and review rotation under the site heat-control plan.'
        elif unknown or suppressed:
            advice = 'Check the crew connection and use general site heat controls; no exposure-based rest duration is available.'
        elif forecast['stale']:
            advice = 'Forecast is stale; check current conditions and use general site heat controls rather than a precise planning window.'
        elif next_window:
            advice = 'Plan heavier tasks outside the upcoming high-risk window; prepare shaded breaks and review rotation.'
        else:
            advice = 'Maintain site heat controls and review conditions before changing task intensity.'
        suggestions.append({'group_id': group_id, 'group_name': group['name'], 'state': overall,
                            'title': 'Review site controls' if unknown or suppressed else 'Plan breaks and rotation',
                            'level': overall, 'reason': 'Uses the most cautious group state and upcoming forecast; uncertainty never lowers caution.',
                            'action': advice, 'window': next_window, 'policy_version': POLICY_VERSION,
                            'source': 'Synthetic forecast + simulated privacy-safe group state',
                            'data_quality': 'incomplete' if unknown or suppressed else 'stale' if forecast['stale'] else 'synthetic',
                            'limitations': 'Advice — supervisor decides. No clinical rest prescription or safe-work allowance.'})
    emergency_fields = ('id', 'worker_name', 'watch_id', 'crew_id', 'occurred_at', 'received_at',
                        'acknowledged_at', 'acknowledged_by', 'resolved_at', 'delayed')
    events = [{**{key: e.get(key) for key in emergency_fields}, 'crew_name': _crew(site, e['crew_id'])['name']}
              for e in site['events'] if not e.get('acknowledged_at')]
    events.sort(key=lambda e: (e['occurred_at'], e['id']))
    return {'site': {key: site[key] for key in ('id', 'name', 'latitude', 'longitude', 'timezone')},
            'mode': 'Synthetic demo — no real workers or devices', 'policy_version': POLICY_VERSION,
            'generated_at': _iso(clock), 'scenario': site['scenario'], 'forecast': forecast,
            'groups': groups, 'suggestions': suggestions, 'emergencies': events,
            'active_help_count': sum(not e.get('resolved_at') for e in site['events'])}


def scenario(state, site_id, kind, now=None):
    site, clock = _site(state, site_id), _now(now)
    allowed = ('normal', 'rising-heat', 'connection-lost', 'reconnect', 'help', 'symptom', 'delayed-help', 'resolve-help')
    if kind not in allowed:
        raise ValueError('Unknown scenario')
    if kind in ('help', 'symptom', 'delayed-help'):
        if not site['assignments']:
            raise ValueError('Assign a watch before creating a help event')
        assignment = site['assignments'][0]
        occurred = clock - timedelta(minutes=12) if kind == 'delayed-help' else clock
        event = {'id': str(uuid4()), 'worker_name': assignment['worker_name'],
                 'watch_id': assignment['watch_id'], 'crew_id': assignment['crew_id'],
                 'assignment_id': assignment['id'], 'assignment_version': assignment['version'],
                 'occurred_at': _iso(occurred), 'received_at': _iso(clock), 'delayed': kind == 'delayed-help',
                 'acknowledged_at': None, 'acknowledged_by': None, 'resolved_at': None}
        if kind != 'delayed-help' and not site.get('gateway_connected', True):
            # Simulated local outbox: this state is never exposed to supervisors.
            event['received_at'] = None
            site.setdefault('pending_events', []).append(event)
        else:
            site['events'].append(event)
    elif kind == 'resolve-help':
        # Simulator-only explicit local resolution evidence. Not a remote watch-clear command.
        for event in site['events']:
            if not event.get('resolved_at'):
                event['resolved_at'] = _iso(clock)
    elif kind == 'connection-lost':
        site['gateway_connected'] = False
        for sample in site['samples'].values():
            sample['sampled_at'] = _iso(clock - timedelta(seconds=180))
    else:
        # Normal/reconnect/rising-heat explicitly resume the synthetic gateway.
        # A state transaction persists both delivery and outbox removal together.
        site['gateway_connected'] = True
        existing_ids = {event['id'] for event in site['events']}
        for queued in site.get('pending_events', []):
            if queued['id'] not in existing_ids:
                delivered = dict(queued)
                delivered['received_at'] = _iso(clock)
                delivered['delayed'] = True
                site['events'].append(delivered)
                existing_ids.add(queued['id'])
        site['pending_events'] = []
        for i, assignment in enumerate(site['assignments']):
            old = site['samples'].get(assignment['watch_id'], {})
            level = ('green', 'amber', 'red')[i % 3] if kind == 'rising-heat' else 'amber' if i == 1 else 'green'
            if kind == 'reconnect':
                level = old.get('level', 'amber')
            site['samples'][assignment['watch_id']] = {'level': level,
                 'sampled_at': _iso(clock), 'received_at': _iso(clock)}
    if kind in ('normal', 'rising-heat', 'reconnect'):
        site['forecast_generated_at'] = _iso(clock)
    site['scenario'] = kind
    return snapshot(state, site_id, clock)


def acknowledge(state, event_id, actor='Demo Supervisor', now=None):
    event_id, actor, clock = _text(event_id, 'Event ID'), _text(actor, 'Actor'), _now(now)
    for site in state.get('sites', {}).values():
        for event in site['events']:
            if event['id'] == event_id:
                if not event.get('acknowledged_at'):
                    event['acknowledged_at'] = _iso(clock)
                    event['acknowledged_by'] = actor
                return dict(event)
    raise ValueError('Unknown help event')
