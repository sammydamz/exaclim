# Job 01 — Alert ladder, worker messages and pictograms

Exaclim | Submission specification | 16 November 2026

## Outcome and scope

Adopt four visible levels: green, amber, red and emergency. Pair every color with a level name, distinct icon and action. The prototype uses synthetic scenarios and an illustrative exposure index; its thresholds are demonstration settings, not occupational limits or permission to keep working. The badge is a proposed device represented by a software simulator until physical bench testing is completed.

English messages below are ready for prototype use. Twi is the proposed second language, subject to worker preference and fluent-speaker review. No verified Twi translation or recorded voice prompt is supplied in this report. The software includes English and a French draft alert-message option; French still needs intended-user review and does not replace a Ghanaian-language requirement for the proposed site. Multilingual field readiness remains incomplete until review and implementation occur.

## Alert ladder

| Level | Trigger and meaning | Worker message | Immediate action | Proposed badge pattern |
|---|---|---|---|---|
| Green — routine precautions | Valid, fresh inputs; illustrative model below caution; no higher-priority condition | “Keep water nearby. Follow the site's water and rest plan. Report feeling unwell.” | Continue only under the site's approved controls | Green indicator and heartbeat; water-drop icon |
| Amber — take precautions | Illustrative caution threshold, elevated forecast risk or unavailable/invalid environmental inputs | “Take a shaded break and reduce effort. Check the site heat plan.” | Move to cooling/shade and use site controls; supervisor reviews workload | Amber indicator, two short vibrations; shade/cup icon |
| Red — stop and cool | Illustrative high-risk threshold or retained red state during data loss | “Stop the task. Move to a cooler place. Contact the site safety lead.” | Stop exposure and request assistance under the site plan | Red indicator, repeated buzzer and vibration; stop-hand icon |
| Emergency — help requested | Worker help button or symptom-report emergency event, regardless of index or sensor state | “Help requested. Follow the site emergency procedure. Get trained assistance now.” | Activate the site emergency response; do not leave a person who needs help alone | Flashing red, repeating audible/haptic signal; help/cross icon |

These are short operational prompts, not treatment instructions. A person feeling unwell can request help at any level. Do not require a high exposure score, a confirmed diagnosis or network access to generate the local emergency state. Green must never be described as “safe.”

## Prototype trigger settings

The prototype uses an illustrative index from 0 to 100. Amber begins at 40 and red at 70; a reading older than 120 seconds is stale. These are deliberately explicit software demonstration parameters, not NIOSH/ISO thresholds or clinically established limits. The model report documents the formula and its limitations. Emergency is event-triggered rather than inferred from a numeric score.

The implemented demonstration index is the clamped sum of four times temperature in degrees Celsius above 25 (negative temperature contribution set to zero), 0.3 times relative-humidity percentage points above 40 (negative humidity contribution set to zero), declared workload (light 0, moderate 10, heavy 20), protective-clothing flag (12), unacclimatized flag (8), and duration in minutes divided by 12. Do not treat this invented additive scale as a measured heat dose or compare it with occupational WBGT limits.

## Pictogram and accessibility specification

Use a water drop for routine precautions, a person under shade/cup for caution, an open hand for stop, and a person calling for help for emergency. Add a broken-link icon and the text “Data unavailable — precautions active” when readings are stale or invalid. Icons should be simple vector shapes with text alternatives; do not rely on platform-dependent emoji as the sole visual signal.

The badge concept has separate acknowledge and help buttons with distinct tactile shapes. The interface must support keyboard access, readable contrast and reduced-motion preference. Never encode severity only through color, sound or vibration. Physical sunlight visibility, noisy-site audibility, haptic discrimination, glove use and accessibility remain post-hackathon validation tasks; software rendering cannot prove them.

## State and priority rules

1. Emergency overrides all environmental, forecast and exposure calculations. Store the emergency latch separately from ordinary severity.
2. The displayed severity is at least the conservative baseline. A forecast or optional model may raise the warning but cannot lower it.
3. Invalid, missing, stale, implausible or out-of-order readings never produce green. Apply at least amber and preserve a previously higher red/emergency level until the documented recovery condition is satisfied.
4. Acknowledge records receipt. It does not erase exposure history, lower risk, resolve an emergency or prove the recommended action was taken. Suppression of repeated sound must never remove the visible alert.
5. Ordinary downgrade requires valid fresh inputs and the model's documented recovery rule. A short dip in readings must not silently clear a warning. The simulator may expose explicit reset controls for synthetic scenarios, labeled as such.
6. Resolve emergency only through an explicit resolution action separate from acknowledge, after the simulated safety lead confirms the emergency workflow. Real deployment requires a defined authorized responder, identity checks and an incident procedure; a UI role toggle is not authorization.
7. Reboot/reconnect must not silently erase an unresolved emergency. Recompute data age from timestamps, restore persisted safety state if supported, and reject invalid stored data. Document whether persistence is implemented or only specified.

## Message delivery and failure behavior

| Situation | Required local behavior | Supervisor or gateway behavior | Honest submission description |
|---|---|---|---|
| Normal connectivity | Badge calculates and displays its current state | Receive only permitted aggregates | Software simulation, unless device tested |
| Zone reading stale | Mark reading age; at least amber; retain higher warning | Show degraded source and no reassuring crew status | Demonstrate by fault injection |
| Internet lost | Preserve local warnings and help latch | Mark dashboard connection stale; queue allowed events if implemented | Offline simulation is distinct from hardware autonomy |
| Badge cannot relay help | Local help signal continues with “Not delivered” status | No false “responder notified” confirmation | Delivery confirmation requires real acknowledgement |
| Forecast unavailable | Use valid zone baseline or conservative degraded state | Mark forecast unavailable; do not substitute unlabeled synthetic data | Forecast scenario data must be labeled |
| Battery low | Distinct low-power notice while retaining active risk display | Maintenance notice where supported | Runtime and low-battery behavior require physical testing |

SMS, voice and site sirens are proposed channels. Unless a real provider/integration is configured and tested, show a labeled message preview rather than “SMS sent” or “call placed.” No outside communication should be triggered by the simulator. Use the site's actual emergency contacts after agreement; do not invent a phone number.

## Translation and voice handoff

Give a fluent Twi reviewer the four source messages, stale-data message, help-delivery failure message and a glossary for shade, stop, rest, acknowledge and emergency. Ask for a plain-language translation, back-translation and audio pronunciation. Test comprehension with intended workers and retain reviewer/version/date metadata. The site's languages should follow its workers, not an assumption that all Ghanaian workers speak Twi.

Treat clinical and emergency translations as reviewed content with version control. A disabled “Twi — review pending” option is more honest than presenting an unreviewed translation as supported. Keep English and icons usable meanwhile. The French draft option demonstrates a second-language message path, but list Ghanaian-language and field-language review as outstanding.

## Acceptance checks for the implemented prototype

| Check | Expected result |
|---|---|
| Trigger help at green | Immediate emergency state; calculation cannot override |
| Acknowledge emergency | Receipt recorded; emergency remains active |
| Replace a red reading with stale input | Red remains, with degraded-data notice |
| Supply stale or invalid data to a new scenario | At least amber; no green status |
| Remove forecast | Missing source identified; no invented live values |
| Trigger help without network | Local emergency continues; delivery status honest |
| Show each severity without color | Text, icon and action remain understandable |
| Restart an unresolved emergency | Persisted latch restored if implemented; otherwise limitation documented |

This report defines intended behavior. Only the repository's executed tests and validation report establish which checks currently pass.

## Submission and post-hackathon boundary

Before submission: implement and test the software alert path; show the emergency and stale-data scenarios; include English messages and pictograms; accurately state translation and channel status. After the hackathon: obtain occupational-health review, worker language validation and physical human-factors testing before field deployment.

Basis: supplied Climate-Resilient Worker Health challenge and team proposal; project research brief. No medically validated thresholds or field performance are claimed.
