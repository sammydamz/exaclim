# Exaclim — three-minute scenario runbook

Rehearse on the final verified build. All cases below are planned demonstrations until the release checklist records a pass. Keep a clean browser session for the recording and a second session ready for local fallback.

## Prepare before recording

1. Start the application using the current repository README. The standard production-style local sequence is `npm ci`, `npm run build`, then `npm start` from `/workspace/exaclim`. Keep the server terminal open. Dependencies must already be installed for the no-Internet fallback.
2. Sign in with `demo@exaclim.test` / `Exaclim2026!`. Confirm the synthetic-data and demo-policy labels are visible.
3. Open the demo-controls drawer and select `normal`. Confirm the Accra site, today's/tomorrow's site-local dates, and three core dashboard areas.
4. Confirm the fixture contains crews of five, two and one. Expect the smaller crews to be combined into one three-person group, with no overlapping individual small-crew breakdown.
5. Keep demo controls closed during the normal product introduction. Prepare the emergency/reset controls so no hidden state interrupts the recording.

## Three-minute judge walkthrough

| Time | Action | Explain or verify |
|---|---|---|
| 0:00–0:20 | Sign in; show Accra and the synthetic source label | “One supervisor view for heat planning, crews and action. This is simulated software evidence.” |
| 0:20–0:45 | Switch Today → Tomorrow and inspect the high-risk window | Explain site-local hourly planning and source freshness. Unknown hours must not look Green. |
| 0:45–1:10 | Show crew cards and suggested actions; run `rising-heat` from the demo drawer | Small crews combine to at least three; advice follows the most cautious permitted information. No individual exposure history is shown. |
| 1:10–1:35 | Run `connection-lost`; inspect status, then `reconnect` | “Missing information becomes caution, not reassurance.” This simulates a gateway/data outage; it does not prove real BLE reliability. Reconnect must not falsely refresh old samples. |
| 1:35–2:15 | Run `help`, show the named synthetic worker/crew/times, acknowledge | Named identity is an emergency exception. Confirm acknowledgement removes the urgent queue entry only after success, while the group's Red/help-active floor remains. |
| 2:15–2:35 | Run `resolve-help` through demo controls | “This simulates trusted watch-local resolution. There is no supervisor button that declares the worker safe.” Confirm the floor clears only according to fresh state, not ACK. |
| 2:35–3:00 | Briefly open setup, then close on the dashboard | Show saved site/crew/watch administration without individual health data. State physical watches, gateway qualification and clinical validation are future work. |

Do not race the acknowledgement step: its safety distinction is more valuable than showing every menu. Use `delayed-help` in a rehearsal or extended Q&A to demonstrate distinct occurrence and delivery times; a delayed call is not silently discarded.

## Scenario contract

The synthetic site action route is `/api/v1/sites/accra/simulate`. Supported scenario kinds are `normal`, `rising-heat`, `connection-lost`, `reconnect`, `help`, `delayed-help` and `resolve-help`. Use the authenticated UI demo drawer; request body, authentication and response details must follow the implemented server contract. The route is demo tooling, not an integration endpoint for physical watches.

`normal` is the initial rehearsal/reset fixture. Do not assume it may erase an unresolved help state; resolve existing synthetic help through the dedicated action before resetting if the final server requires that invariant.

## Local fallback if event Internet access fails

Before the event, complete installation/build and confirm the local server serves the app without fetching fonts, SDK code or other required UI assets from a public CDN. Rehearse the entire walkthrough with the public Internet unavailable while keeping the local browser-to-server connection working.

Use the existing local server or start it with `npm start`. Open its printed local address on the presenting machine. Sign in against that running local backend; offline login without a server is not supported. Select the synthetic forecast and simulation fixtures. Do not label cached or synthetic weather as live.

A local fallback proves the presentation can run without event Internet, not that a real watch works without a gateway. If the local backend/browser connection itself fails, retain the visible cautious state; do not pretend ACK succeeded. Restore the server and sign in again. If the live application cannot be restored, use a previously recorded genuine walkthrough labeled with its build/date, and disclose that it is a recording. Never substitute a generated concept video as evidence that the software ran.

## Quick Q&A answers

- **Where is the AI?** The demonstration uses an explainable versioned synthetic risk policy and a forecast adapter. It is not a trained or clinically validated personal heat-strain model.
- **Are the watches connected?** No physical BLE/watch implementation is claimed. Watch/gateway events are simulated explicitly.
- **Does Red diagnose heat illness?** No. It is a cautious action state; a help request follows the site emergency process independently of computed risk.
- **Why combine crews?** To avoid publishing routine risk breakdowns for groups below three. This alone does not establish legal anonymity or prevent every inference.
- **What does ACK mean?** Receipt by the supervisor. It does not resolve the watch's help state or prove care was delivered.
