"""Exercise the real Dashboard V1 in Chromium against its own temporary server.

Run after `npm run build`. Produces screenshots and a machine-readable report.
Passing software assertions never pass physical, clinical or full PRD QA gates.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile
import threading
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exaclim.server import make_server
from playwright.sync_api import sync_playwright, expect


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='/workspace/artifacts/exaclim-dashboard-v1')
    parser.add_argument('--base-url', help='Run against an already-started synthetic API instead of creating a Python server')
    parser.add_argument('--ignore-https-errors', action='store_true', help='Testing only: allow managed HTTPS inspection certificates')
    parser.add_argument('--backend-label', help='Backend name included in the evidence report')
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    checks, failures, screenshots = [], [], []
    page_errors, console_errors, response_errors = [], [], []
    started = datetime.now(timezone.utc).isoformat()

    def passed(name, qa):
        checks.append({'name': name, 'status': 'Pass', 'qa_cases_partially_exercised': qa})
        print('PASS:', name, flush=True)

    def capture(page, filename):
        target = output / filename
        toast = page.locator('#toast')
        if toast.is_visible():
            expect(toast).not_to_be_visible(timeout=10000)
        page.screenshot(path=str(target), full_page=True)
        screenshots.append(filename)

    with tempfile.TemporaryDirectory(prefix='exaclim-v1-browser-') as directory:
        httpd, thread = None, None
        if args.base_url:
            base = args.base_url.rstrip('/')
            if not base.startswith(('http://', 'https://')):
                raise ValueError('--base-url must be an HTTP(S) URL for a synthetic test deployment')
        else:
            httpd = make_server(host='127.0.0.1', port=0,
                                db_path=str(Path(directory) / 'dashboard.sqlite3'))
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            base = f'http://127.0.0.1:{httpd.server_port}'
        backend = args.backend_label or ('External synthetic API' if args.base_url else 'Python HTTP + SQLite')
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path='/usr/bin/chromium',
                    headless=True, args=['--no-sandbox'],
                    proxy={'server': os.environ['HTTPS_PROXY']}
                    if base.startswith('https://') and os.environ.get('HTTPS_PROXY') else None)
                # Accra forecast must not follow the viewer's different local day.
                context = browser.new_context(viewport={'width': 1440, 'height': 1000},
                    timezone_id='America/Los_Angeles', reduced_motion='reduce',
                    ignore_https_errors=args.ignore_https_errors)
                page = context.new_page()
                page.on('pageerror', lambda error: page_errors.append(str(error)))
                page.on('console', lambda msg: console_errors.append(msg.text)
                    if msg.type == 'error' else None)
                page.on('response', lambda response: response_errors.append({
                    'url': response.url, 'status': response.status})
                    if response.status >= 400 else None)

                def api(path, body=None):
                    response = context.request.get(base + path) if body is None else \
                        context.request.post(base + path, data=body,
                            headers={'Origin': base, 'Content-Type': 'application/json'})
                    assert response.ok, (path, response.status, response.text())
                    return response.json()

                def snapshot():
                    return api('/api/v1/sites/accra/dashboard')

                def scenario(name):
                    api('/api/v1/sites/accra/simulate', {'scenario': name})
                    page.get_by_role('button', name='Refresh dashboard', exact=True).click()

                def sign_in(password='Exaclim2026!'):
                    if not page.get_by_role('dialog').is_visible():
                        page.locator('#open-login').click()
                    expect(page.get_by_role('dialog')).to_be_visible()
                    page.locator('#login-email input').fill('demo@exaclim.test')
                    page.locator('#login-password input').fill(password)
                    page.locator('#submit-login').click()

                health = context.request.get(base + '/api/health')
                assert health.ok and 'synthetic' in json.dumps(health.json()).lower(), \
                    'This harness must only mutate an explicitly synthetic test backend'
                page.goto(base, wait_until='networkidle')
                expect(page.locator('#welcome')).to_be_visible()
                expect(page.locator('#dashboard')).to_be_hidden()
                assert context.request.get(base + '/api/v1/auth/me').status == 401
                passed('Signed-out landing does not expose dashboard or identity', ['QA23', 'QA35'])

                sign_in('incorrect-password')
                expect(page.locator('#login-error')).not_to_be_empty()
                expect(page.locator('#dashboard')).to_be_hidden()
                passed('Wrong password gives visible error without authenticated view', ['QA23', 'QA36'])

                page.locator('#login-password input').fill('Exaclim2026!')
                page.locator('#submit-login').click()
                expect(page.locator('#dashboard')).to_be_visible()
                expect(page.get_by_role('dialog')).not_to_be_visible()
                expect(page.locator('#forecast-hours button')).to_have_count(24)
                passed('Password login loads authenticated dashboard and closes SDK dialog', ['QA23', 'QA36'])

                headings = page.locator('#dashboard h2').all_text_contents()
                assert headings == ['Heat forecast', 'Crew status', 'Breaks & rotation'], headings
                assert page.locator('#badge-device, #worker-form, #event-log').count() == 0
                passed('Core screen contains exactly three specified areas and no worker analytics', ['QA44'])

                expect(page.locator('.mode-note')).to_contain_text('Synthetic')
                expect(page.locator('#forecast-provenance')).to_contain_text('ynthetic')
                expect(page.locator('#site-timezone')).to_contain_text('Accra')
                passed('Synthetic source and site timezone are visible in another browser timezone', ['QA01', 'QA02', 'QA42'])

                today = page.get_by_role('tab', name='Today', exact=True)
                tomorrow = page.get_by_role('tab', name='Tomorrow', exact=True)
                today.focus()
                page.keyboard.press('ArrowRight')
                expect(tomorrow).to_be_focused()
                expect(tomorrow).to_have_attribute('aria-selected', 'true')
                expect(page.locator('#forecast-hours button')).to_have_count(24)
                page.keyboard.press('ArrowLeft')
                expect(today).to_have_attribute('aria-selected', 'true')
                passed('SDK day tabs work by keyboard and retain full hourly coverage', ['QA01', 'QA36'])

                hour = page.locator('#forecast-hours button').nth(12)
                hour.focus()
                page.keyboard.press('Enter')
                expect(page.locator('#hour-detail')).not_to_contain_text('Choose an hour')
                assert '12' in page.locator('#hour-detail').inner_text()
                passed('Hourly forecast detail is keyboard-accessible without hover', ['QA03', 'QA36'])

                groups = snapshot()['groups']
                assert any(len(group['crew_ids']) > 1 for group in groups)
                expect(page.locator('#crew-list')).not_to_be_empty()
                expect(page.locator('.section-footnote').filter(has_text='at least 3')).to_be_visible()
                names = [row['worker_name'] for row in api('/api/v1/sites/accra/setup')['assignments']]
                routine_text = page.locator('#crew-list').inner_text()
                assert not any(name in routine_text for name in names)
                passed('Routine crew cards show grouped aggregates without worker identities', ['QA09', 'QA25'])

                expect(page.locator('#suggestions-list')).not_to_be_empty()
                expect(page.locator('#suggestions-list')).not_to_contain_text('[object Object]')
                expect(page.locator('#risk-window')).to_contain_text(re.compile(r'\d{2}:\d{2}'))
                expect(page.locator('.section-footnote').filter(has_text='Advice')).to_contain_text('supervisor decides')
                passed('Forecast windows are readable and suggestions are advice, not recorded adherence', ['QA03', 'QA14', 'QA15'])

                capture(page, 'dashboard-1440.png')
                page.set_viewport_size({'width': 1920, 'height': 1080})
                capture(page, 'dashboard-1920.png')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                passed('Dashboard renders at 1440px and 1920px with captured evidence', ['QA37'])

                page.locator('#open-setup').click()
                expect(page.get_by_role('dialog')).to_be_visible()
                expect(page.locator('#setup-site-name input')).not_to_have_value('')
                page.keyboard.press('Escape')
                expect(page.get_by_role('dialog')).not_to_be_visible()
                expect(page.locator('#open-setup')).to_be_focused()
                passed('SDK setup dialog Escape closes and restores trigger focus', ['QA36'])

                page.locator('#open-setup').click()
                page.locator('#setup-site-name input').fill('Accra synthetic browser QA')
                page.locator('#save-site').click()
                expect(page.locator('#toast')).to_be_visible()
                expect(page.locator('#site-name')).to_contain_text('Accra synthetic browser QA')
                page.get_by_role('button', name='Close site setup').click()
                page.reload(wait_until='networkidle')
                expect(page.locator('#site-name')).to_contain_text('Accra synthetic browser QA')
                passed('Site setup save is confirmed and survives browser reload', ['QA26', 'QA36'])

                page.locator('#open-setup').click()
                page.get_by_role('tab', name='Crews', exact=True).click()
                run_token = secrets.token_hex(3)
                new_crew_name = f'QA synthetic crew {run_token}'
                page.locator('#new-crew-name input').fill(new_crew_name)
                page.locator('#new-crew-count input').fill('3')
                page.locator('#create-crew').click()
                expect(page.locator('#setup-crews')).to_contain_text(new_crew_name)
                passed('New crew is persisted and shown with explicit saved feedback', ['QA26'])

                page.get_by_role('tab', name='Watch assignments', exact=True).click()
                assert not page.locator('#setup-dialog input[name=clothing], #setup-dialog input[name=acclimatization]').count()
                expect(page.locator('.setup-info')).to_contain_text('never entered')
                page.locator('#assignment-crew button').click()
                page.get_by_role('option', name=new_crew_name, exact=True).click()
                page.locator('#assignment-name input').fill('Browser synthetic worker')
                page.locator('#assignment-watch input').fill(f'QA-SYNTHETIC-{run_token}')
                page.locator('#save-assignment').click()
                expect(page.locator('#setup-assignments')).to_contain_text('Browser synthetic worker')
                page.get_by_role('button', name='Close site setup').click()
                expect(page.locator('#crew-list')).not_to_contain_text('Browser synthetic worker')
                passed('Assignment flow explicitly excludes private watch-local profiles', ['QA24', 'QA25'])
                passed('Simulated watch assignment saves without exposing identity in routine crew cards', ['QA25', 'QA26'])

                scenario('connection-lost')
                expect(page.locator('#crew-list')).to_contain_text('aution')
                assert all(group['level'] != 'green' for group in snapshot()['groups'])
                capture(page, 'dashboard-data-loss.png')
                passed('Injected gateway loss is cautious and never reassures green', ['QA07', 'QA12'])

                scenario('reconnect')
                expect(page.locator('#crew-list')).to_contain_text('resh')
                passed('Explicit reconnect restores fresh labeled synthetic data', ['QA08', 'QA30'])

                scenario('help')
                event = next(e for e in snapshot()['emergencies'] if not e['acknowledged'])
                expect(page.locator('#emergency-region')).to_contain_text(event['worker_name'])
                expect(page.locator('#emergency-region')).to_contain_text(event['crew_name'])
                capture(page, 'dashboard-help.png')
                passed('Named synthetic help is shown above the core information areas', ['QA17'])

                # Do not allow an optimistic ACK to hide the urgent banner when offline.
                context.set_offline(True)
                page.locator('#emergency-region button').first.click()
                expect(page.locator('#emergency-region')).to_contain_text(event['worker_name'])
                context.set_offline(False)
                page.locator('#emergency-region button').first.click()
                expect(page.locator('#emergency-region')).not_to_contain_text(event['worker_name'])
                help_groups = [group for group in snapshot()['groups'] if group['help_active']]
                assert help_groups and all(group['level'] in ('red', 'emergency') for group in help_groups)
                expect(page.locator('#crew-list')).to_contain_text('Help')
                passed('Offline ACK stays visible; confirmed ACK hides banner but retains group help floor', ['QA19', 'QA20'])

                scenario('delayed-help')
                expect(page.locator('#emergency-region')).to_contain_text('elayed')
                passed('Delayed help is identified rather than presented as immediate delivery', ['QA18'])

                # Use the explicit development control only, never a dashboard ACK, to resolve.
                scenario('resolve-help')
                for width, height in [(768, 1024), (390, 844), (360, 800)]:
                    page.set_viewport_size({'width': width, 'height': height})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
                    expect(page.locator('#forecast-title')).to_be_visible()
                    expect(page.locator('#crew-title')).to_be_visible()
                    expect(page.locator('#suggestions-title')).to_be_visible()
                    if width <= 390:
                        emergency = page.locator('.emergency-content').first
                        if emergency.is_visible():
                            assert emergency.bounding_box()['width'] >= width * .55, 'Emergency content is too narrow to read'
                    capture(page, f'dashboard-{width}.png')
                passed('All three areas fit tablet and 390/360px mobile layouts without page overflow', ['QA37'])

                page.set_viewport_size({'width': 1440, 'height': 1000})
                # UI SDK supplies the behavior on interactive buttons, including dynamic cards.
                assert page.locator('button').evaluate_all(
                    "els => els.every(el => !!el.closest('ui-button,ui-tabs-tab,ui-select-trigger,ui-dialog-close,ui-dialog-trigger'))")
                assert page.locator('select').count() == 0
                passed('Interactive buttons remain SDK-owned and native select controls are absent', ['QA36'])

                storage = page.evaluate("({local: Object.keys(localStorage), session: Object.keys(sessionStorage)})")
                serialized_storage = page.evaluate("JSON.stringify({local:{...localStorage},session:{...sessionStorage}})")
                assert not any(name in serialized_storage for name in names)
                assert 'Exaclim2026!' not in serialized_storage
                passed('Browser storage contains no synthetic emergency names or password', ['QA35'])

                page.locator('#sign-out').click()
                expect(page.locator('#dashboard')).to_be_hidden()
                expect(page.locator('#welcome')).to_be_visible()
                assert context.request.get(base + '/api/v1/auth/me').status == 401
                page.reload(wait_until='networkidle')
                expect(page.locator('#dashboard')).to_be_hidden()
                passed('Logout clears protected view and server session across reload', ['QA23', 'QA35'])

                assert not page_errors, page_errors
                # Deliberate invalid login/offline ACK produce expected network errors.
                unexpected = [message for message in console_errors if not any(token in message for token in
                    ['401', 'net::ERR_INTERNET_DISCONNECTED', 'Failed to fetch', 'ERR_NETWORK_CHANGED'])]
                assert not unexpected, unexpected
                passed('No unexpected JavaScript runtime, console or CSP errors', ['QA36', 'QA42'])
                browser.close()
        except Exception as error:
            failures.append({'type': type(error).__name__, 'message': str(error),
                             'traceback': traceback.format_exc()})
            print(traceback.format_exc(), file=sys.stderr)
        finally:
            if httpd:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=5)

    cases = json.loads((ROOT / 'docs/dashboard-v1/qa-cases.json').read_text())
    covered = {qa for check in checks for qa in check['qa_cases_partially_exercised']}
    result = {
        'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
        'mode': 'Synthetic software-only Chromium acceptance run',
        'backend': backend, 'base_url': base,
        'passed_check_count': len(checks), 'failure_count': len(failures),
        'checks': checks, 'failures': failures, 'screenshots': screenshots,
        'page_errors': page_errors, 'console_errors': console_errors,
        'response_errors': response_errors,
        'qa_case_coverage': [{'id': case['id'], 'title': case['title'],
            'status': 'Partial software coverage' if case['id'] in covered else 'Not run by this harness',
            'note': 'No complete QA-case, physical, clinical or pilot pass is inferred.'}
            for case in cases],
        'not_measured': ['Physical BLE/watch autonomy, queue durability and battery behavior',
                        'Clinical validity, language review and worker usability',
                        'p95 20-run latency/cold-load targets and weak-link performance distribution',
                        'Production security, site isolation review and real-worker data readiness'],
    }
    (output / 'browser-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed_checks': len(checks), 'failures': len(failures),
                      'report': str(output / 'browser-results.json')}, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
