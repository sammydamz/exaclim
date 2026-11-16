# Job 06 — Prototype budget and sourcing plan

Exaclim · Climate-Resilient Worker Health · 16 November 2026

**Deliverable status:** a transparent planning budget and sourcing specification. These numbers are internal allowances in USD, **not supplier quotes, verified market prices or confirmed availability**. Procurement is not required to run the software submission. Do not describe this report as a quoted bill of materials.

## 1. Funding decision

Keep three budgets separate: the software submission, the one-station/two-badge bench kit, and the later human pilot. This avoids presenting a small development-board budget as the cost of a validated deployment.

Use open-source tools and a local synthetic demonstration for the submission. The cloud environment and team time are not priced here; zero incremental spending does not mean the project has no operating cost. Do not buy a custom PCB, commit to a bulk order, or pay for a model-training service before the bench and model evidence justify it.

## 2. Bench kit planning allowances

The kit contains three controller boards: one station and two badges. Sensor and haptic boards are development breakouts, not optimized production electronics. Battery and enclosure costs can change materially with safety, capacity and shipping requirements.

| Item | Quantity | Low unit allowance USD | High unit allowance USD | Low total USD | High total USD |
|---|---|---|---|---|---|
| BLE controller development board | 3 | 25 | 45 | 75 | 135 |
| SHT4x temperature/humidity breakout | 1 | 10 | 25 | 10 | 25 |
| Optional motion breakout | 2 | 5 | 15 | 10 | 30 |
| Haptic driver and compatible actuator set | 2 | 10 | 20 | 20 | 40 |
| LEDs, resistors, buzzer driver and two buttons per badge | 2 sets | 8 | 20 | 16 | 40 |
| Protected compatible battery | 2 | 10 | 20 | 20 | 40 |
| Badge enclosure and clip/armband | 2 | 10 | 25 | 20 | 50 |
| Station enclosure and radiation-shield materials | 1 set | 20 | 60 | 20 | 60 |
| Cables, prototyping materials and power accessories | 1 set | 25 | 60 | 25 | 60 |
| **Bench electronics subtotal** | | | | **216** | **480** |

The optional motion boards can be omitted: the subtotal then becomes USD 206–450. Do not substitute motion for task-based workload declaration.

A discretionary 20% planning contingency on the full subtotal is USD 43.20–96.00, giving **USD 259.20–576.00 before shipping, taxes, import fees, reference equipment and labor**. Contingency is not a way to hide unknown freight or duties; those require separate quotes. Amounts are not a recommended purchase authorization.

## 3. Costs deliberately not guessed

| Cost | Required next evidence | Treatment |
|---|---|---|
| International freight and lithium-battery carriage | Supplier courier quote to actual Ghana destination | Separate from electronics subtotal |
| Ghana taxes/import charges | Applicable classification and qualified local advice | No made-up percentage |
| Reference WBGT instrument | Rental/loan or purchase quote with calibration status | Required before measurement validation, not before simulated submission |
| Calibration and verification | Lab or competent-provider quotation and scope | Separate recurring/initial line |
| Assembly and repair labor | Hours and local labor estimate | Report paid and donated time separately |
| Occupational-health/hygiene reviewer | Scope, deliverables and professional quote | Cannot be replaced with an AI subscription |
| Ethics and site permissions | Relevant institutional/site determination | Do not assume a fee or approval |
| Pilot training, worker engagement and translations | Site-specific schedule and competent providers | Separate from software development |
| SMS/voice delivery | Provider pricing for actual Ghana routes and volume | Not necessary for local badge simulation; no delivery guarantee |
| Hosting, monitoring and maintenance | Architecture and actual usage | Local demo does not establish production operating cost |

The hackathon budget can truthfully list supplier-priced hardware as pending while showing design feasibility and these allowances. If the portal requires verified commercial pricing, obtain it rather than relabel estimates as quotes.

## 4. Sourceable component specification

| Component | Candidate source/product | What must match |
|---|---|---|
| Controller | Adafruit Feather nRF52840 Express, product 4062, or equivalent documented board | BLE support, supported toolchain, I/O, compatible charging/power |
| Station sensor | SHT4x breakout; candidate Adafruit product 4885 | Exact sensor variant, environmental range, supply, enclosure mounting |
| Motion | LIS3DH breakout; candidate Adafruit product 2809 | Supply/interface, mounting and sensor orientation |
| Haptic | DRV2605L breakout; candidate Adafruit product 2305 | Actuator type/rating, supply and waveform mode |
| Reference | Qualified calibrated WBGT instrument, borrowed/rented if practical | Measurement method, range, calibration certificate and data export |

Candidate product identifiers come from official library/BSP repositories, not live stock or price checks. Prefer existing team equipment where its specifications are known. A local reseller is acceptable only with traceability to the actual part, compatible specifications and a clear return/replacement route.

## 5. Supplier request template

Subject: Exaclim engineering prototype — quotation request

Request the exact manufacturer part number and revision, unit price and quantity breaks, current stock, dispatch lead time, delivery estimate to the actual Ghana destination, shipping and import terms, battery-shipping restrictions, currency/payment terms, warranty and returns, and quote-validity date. For instruments request calibration certificate, measurement specifications, rental option, accessories and recalibration service. Do not ask a supplier to certify our assembled system through a component purchase.

Record quote reference, supplier legal name/contact, source URL, date, SKU/revision, currency, quantity, price, freight, taxes treatment, stock, delivery estimate, warranty, exclusions and evidence-file path. Preserve the original quote. Convert currencies only with a named rate source and date; this report intentionally uses USD without inventing a GHS exchange rate.

No supplier messages have been sent. Sending requests requires the team's chosen supplier contacts and authorization; this report only prepares the request.

## 6. Pilot scaling model

Do not extrapolate two bench badges into a validated price per worker. A pilot cost model is:

`stations × validated_station_cost + badges × validated_badge_cost + gateways + spare_devices + reference/calibration + assembly + freight/import + training + ethics/site work + occupational review + connectivity + maintenance + evaluation`.

Determine station count from site microclimates and validation, not worker count alone. Determine gateway count from a radio survey. Budget spares based on observed failure/repair lead times. Keep capital purchases, operating costs and donated resources separate. A full pilot budget is pending a named partner, site survey, participant plan and quotations; it is not a blocker to a synthetic software prototype.

## 7. Research and verification record

Accessed 16 November 2026: official [Adafruit nRF52 BSP](https://github.com/adafruit/Adafruit_nRF52_Arduino), [SHT4X library](https://github.com/adafruit/Adafruit_SHT4X), [LIS3DH library](https://github.com/adafruit/Adafruit_LIS3DH) and [DRV2605 library](https://github.com/adafruit/Adafruit_DRV2605_Library). These support component/interface feasibility.

The direct Adafruit Feather product-page request returned a proxy HTTP 403. No live supplier quote, shipping cost, stock level or delivery promise has been verified. The report therefore distinguishes observed source facts from planning allowances throughout. Resolve procurement evidence before placing orders; do not hold the working software submission for physical deliveries.

## 8. Completion criteria

Completed for this job: scoped bench BOM, arithmetic, explicit exclusions, sourceable part candidates, quote request content and pilot cost model. Remaining external work: supplier responses, local availability, import/shipping terms and reference-instrument access. These do not become verified merely because a PDF exists.
