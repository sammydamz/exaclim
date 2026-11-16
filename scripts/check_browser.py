"""Optional real Chromium checks; requires Playwright and a Chromium executable.
Run from repository root. Starts and stops its own loopback server.
"""
import json
import sys
import threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from exaclim.server import Handler
from playwright.sync_api import sync_playwright, expect


def main():
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    passed = []
    def check(name):
        passed.append(name)
        print('PASS:', name)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
            context = browser.new_context(viewport={'width':1440, 'height':1000})
            page = context.new_page()
            errors = []
            console_errors = []
            page.on('console', lambda message: console_errors.append(message.text) if message.type == 'error' else None)
            def reset():
                page.locator('#reset-worker').click()
                page.locator('#confirm-reset').click()
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{httpd.server_port}', wait_until='networkidle')
            expect(page.locator('#crew-summary')).to_contain_text('8 synthetic workers')
            check('Crew fixture loaded with explicit synthetic provenance')
            page.locator('#crew-size').fill('4')
            page.locator('#refresh-crew').click()
            expect(page.locator('#crew-summary')).to_contain_text('withheld')
            expect(page.locator('#crew-counts')).to_be_empty()
            check('Small crew counts withheld in browser')
            page.locator('[data-tab=worker]').click()
            page.locator('[data-preset=normal]').click()
            expect(page.locator('#badge-level')).to_have_text('GREEN')
            check('Routine scenario green')
            page.locator('[data-preset=hot]').click()
            expect(page.locator('#badge-level')).to_have_text('RED')
            page.locator('[data-preset=stale]').click()
            expect(page.locator('#badge-level')).to_have_text('RED')
            check('Hot scenario red retained during sensor loss')
            reset()
            expect(page.locator('#badge-level')).to_have_text('GREEN')
            page.locator('[data-preset=stale]').click()
            expect(page.locator('#badge-level')).to_have_text('AMBER')
            check('Lost sensor cannot display green')
            page.locator('#emergency').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            page.locator('#acknowledge').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            page.locator('[data-preset=normal]').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            check('Help remains emergency after acknowledgement and cooler inputs')
            page.locator('#field-language button').click()
            page.get_by_role('option', name='French · draft translation').click()
            expect(page.locator('#translated-action')).to_contain_text('urgence')
            check('French draft emergency message shown')
            reset()
            expect(page.locator('#badge-level')).to_have_text('GREEN')
            page.locator('#field-use_forecast').focus()
            page.keyboard.press('Space')
            expect(page.locator('#field-use_forecast')).to_have_attribute('aria-checked', 'true')
            page.locator('#worker-form button[type=submit]').click()
            expect(page.locator('#worker-projection')).to_contain_text('Synthetic look-ahead')
            expect(page.locator('#badge-level')).not_to_have_text('GREEN')
            check('Optional synthetic projection escalates baseline and labels interpretation')
            page.locator('#field-use_forecast').focus()
            page.keyboard.press('Space')
            expect(page.locator('#field-use_forecast')).to_have_attribute('aria-checked', 'false')
            reset()
            expect(page.locator('#badge-level')).to_have_text('GREEN')
            context.set_offline(True)
            expect(page.locator('#badge-level')).to_have_text('AMBER')
            page.locator('#emergency').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            page.wait_for_timeout(250)
            context.set_offline(False)
            expect(page.locator('#acknowledge')).to_be_enabled()
            page.wait_for_function("() => sessionStorage.getItem('exaclim_pending_emergency') !== 'true'", timeout=10000)
            state = context.request.get(f'http://127.0.0.1:{httpd.server_port}/api/worker').json()
            assert state['level'] == 'emergency', state
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            check('Offline help latched locally and synchronized after reconnect')
            page.reload(wait_until='networkidle')
            page.locator('[data-tab=worker]').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            check('Browser reload retains server emergency session')
            reset()
            expect(page.locator('#badge-level')).to_have_text('GREEN')
            page.evaluate("""() => { const original = window.fetch; window.fetch = (url, options) => String(url).includes('/api/evaluate') ? new Promise(resolve => setTimeout(resolve, 1200)).then(() => original(url, options)) : original(url, options); }""")
            page.locator('#worker-form button[type=submit]').click()
            expect(page.locator('#emergency')).to_be_enabled()
            page.locator('#emergency').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            page.wait_for_timeout(1500)
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            check('Help remains available during delayed scenario request')
            page.locator('#reset-worker').click()
            expect(page.get_by_role('alertdialog')).to_be_visible()
            page.get_by_role('button', name='Keep session').click()
            expect(page.locator('#badge-level')).to_contain_text('EMERGENCY')
            expect(page.locator('#reset-worker')).to_be_focused()
            page.locator('#reset-worker').click()
            page.keyboard.press('Escape')
            expect(page.locator('#reset-worker')).to_be_focused()
            reset()
            expect(page.locator('#badge-level')).to_have_text('GREEN')
            check('SDK reset dialog cancel/Escape preserves state and returns focus; confirm resets')
            page.locator('#field-acclimatized').focus()
            page.keyboard.press('Space')
            expect(page.locator('#field-acclimatized')).to_have_attribute('aria-checked', 'false')
            page.keyboard.press('Space')
            expect(page.locator('#field-acclimatized')).to_have_attribute('aria-checked', 'true')
            check('SDK checkbox changes with Space; switch checked by keyboard earlier')
            page.locator('#field-workload button').focus()
            page.keyboard.press('Enter')
            page.keyboard.press('End')
            page.keyboard.press('Enter')
            expect(page.locator('#field-workload ui-select-value')).to_have_text('Heavy')
            expect(page.locator('#field-workload button')).to_be_focused()
            check('SDK select supports keyboard selection and returns focus')
            for key, value in [('temperature_c','27'),('humidity_pct','55'),('duration_minutes','0'),('sensor_age_seconds','0')]:
                field = page.locator('#'+key)
                field.fill('')
                page.locator('#worker-form button[type=submit]').click()
                assert page.locator('#worker-form').evaluate('(el) => !el.checkValidity()'), key
                field.fill(value)
                field.press('Tab')
            check('All required numeric fields block empty submission')
            result = page.evaluate("""async () => {
              const entries = exaclim.agent.snapshot().filter(entry => !entry.offPage && entry.component !== 'more');
              const missing = entries.filter(entry => !entry.label);
              const expected = ['Air temperature (°C)', 'Relative humidity (%)', 'Declared workload', 'Clothing', 'Elapsed exposure (minutes)', 'Sensor reading age (seconds)', 'Scenario worker is acclimatized', 'Synthetic forecast look-ahead', 'Additional worker message', 'Evaluate scenario', 'Acknowledge', 'Call for help', 'Reset the badge simulation?'];
              const absent = expected.filter(label => !entries.some(entry => entry.label === label));
              const choice = name => entries.find(entry => entry.label === name).items.at(-1).label;
              const result = await exaclim.agent.act({ steps: [
                {ref:'Air temperature (°C)', action:'setValue', args:[30]},
                {ref:'Relative humidity (%)', action:'setValue', args:[60]},
                {ref:'Declared workload', action:'setValue', args:[choice('Declared workload')]},
                {ref:'Clothing', action:'setValue', args:[choice('Clothing')]},
                {ref:'Elapsed exposure (minutes)', action:'setValue', args:[60]},
                {ref:'Sensor reading age (seconds)', action:'setValue', args:[0]},
                {ref:'Scenario worker is acclimatized', action:'setChecked', args:[false]},
                {ref:'Synthetic forecast look-ahead', action:'setChecked', args:[true]},
                {ref:'Additional worker message', action:'setValue', args:[choice('Additional worker message')]},
                {ref:'Evaluate scenario', action:'press'},
              ]});
              return {missing,absent,result};
            }""")
            assert not result['missing'], result
            assert not result['absent'], result
            assert result['result']['ok'], result
            expect(page.locator('#temperature_c')).to_have_value('30')
            expect(page.locator('#field-workload ui-select-value')).to_have_text('Heavy')
            expect(page.locator('#field-clothing ui-select-value')).to_have_text('Protective / restrictive')
            expect(page.locator('#field-acclimatized')).to_have_attribute('aria-checked','false')
            expect(page.locator('#field-use_forecast')).to_have_attribute('aria-checked','true')
            expect(page.locator('#badge-level')).to_have_text('RED')
            check('SDK agent discovers named controls and changes every scenario field through real actions')
            page.locator('[data-tab=crew]').focus()
            page.keyboard.press('ArrowDown')
            expect(page.locator('[data-tab=worker]')).to_be_focused()
            expect(page.locator('[data-tab=worker]')).to_have_attribute('aria-selected','true')
            page.keyboard.press('End')
            expect(page.locator('[data-tab=system]')).to_be_focused()
            expect(page.locator('#tab-system')).to_be_visible()
            check('SDK vertical tabs support arrows, End, focus and panel relationships')
            page.locator('[data-tab=worker]').click()
            assert page.locator('button').evaluate_all("els => els.every(el => el.hasAttribute('data-slot'))")
            assert page.locator('select').count() == 0
            check('Every interactive button uses an SDK part; no native select remains')
            page.locator('html').evaluate("el => el.dir = 'rtl'")
            page.set_viewport_size({'width':390,'height':844})
            page.locator('[data-tab=crew]').focus()
            page.keyboard.press('ArrowLeft')
            expect(page.locator('[data-tab=worker]')).to_be_focused()
            page.locator('html').evaluate("el => el.dir = 'ltr'")
            page.set_viewport_size({'width':1440,'height':1000})
            check('SDK horizontal tabs follow RTL reading direction')
            tokens = page.evaluate("""() => {
              const style = getComputedStyle(document.documentElement);
              return Object.fromEntries(['foreground','background','muted','muted-foreground','primary','primary-foreground','input','ring'].map(key => [key, style.getPropertyValue('--ui-'+key).trim()]));
            }""")
            def luminance(color):
                color = color.lstrip('#')
                if len(color) == 3:
                    color = ''.join(character * 2 for character in color)
                values = [int(color[i:i+2],16)/255 for i in (0,2,4)]
                linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
                return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
            for first, second, minimum in [('foreground','background',4.5),('muted-foreground','background',4.5),('muted-foreground','muted',4.5),('primary-foreground','primary',4.5),('input','background',3),('ring','background',3)]:
                a,b=sorted([luminance(tokens[first]),luminance(tokens[second])])
                assert (b+.05)/(a+.05) >= minimum, (first,second)
            check('Browser-resolved SDK tokens meet text, control-edge and focus contrast targets')

            artifact = Path('/workspace/artifacts')
            artifact.mkdir(exist_ok=True)
            page.screenshot(path=str(artifact/'exaclim-worker.png'), full_page=True)
            page.set_viewport_size({'width':390, 'height':844})
            for tab in ['crew','worker','system']:
                page.locator(f'[data-tab={tab}]').click()
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), tab
            page.locator('[data-tab=crew]').focus()
            page.keyboard.press('ArrowRight')
            expect(page.locator('[data-tab=worker]')).to_be_focused()
            check('All three views fit 390px viewport without horizontal overflow')
            assert not errors, errors
            unexpected_errors = [error for error in console_errors if 'net::ERR_INTERNET_DISCONNECTED' not in error]
            assert not unexpected_errors, unexpected_errors
            check('No unexpected browser JavaScript, console or CSP errors')
            browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()
    print(json.dumps({'browser_checks_passed':len(passed), 'checks':passed}, indent=2))

if __name__=='__main__':
    main()
