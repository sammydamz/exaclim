> Deployment update, 20 November 2026: the synthetic demo is live at https://exaclim.kasalite-business.workers.dev using Hono + Workers + D1. See [executed verification](verification.md) for current results; unchecked release items below remain separate gates.

# Exaclim — demo preparation

Prepared 19 November 2026 for the 20 November demonstration. This pack supports the supervisor-dashboard build; it does not certify its completion.

The demonstration is a synthetic software prototype. One supervisor screen contains exactly three areas: today's/tomorrow's heat forecast, crew status, and suggested breaks/rotation. Login, setup and a priority help banner support those areas. Simulation belongs in an explicitly labeled demo-controls drawer, not a fourth dashboard section.

Use [scenario-runbook.md](scenario-runbook.md) for the three-minute walkthrough and local fallback, and [release-checklist.md](release-checklist.md) to record verification and the capability boundary. The PRD in `docs/dashboard-v1/01-product-requirements.md` governs the current scope; earlier station/badge reports are historical planning, not the current dashboard contract.

## Presenter wording

“Exaclim helps a supervisor plan work around heat and respond to help calls. This demonstration uses synthetic crew, watch and weather events. The dashboard groups small crews for privacy and keeps a cautious state when information is incomplete. Acknowledging a help call confirms receipt; it does not declare the worker safe. Real watches, Bluetooth delivery, independent watch alerts and field performance still require implementation and testing.”

Do not describe an illustrative policy as a clinically approved limit, a forecast as a trained personal-health model, or synthetic outcomes as prevented illness. Do not promise remote help delivery while the connection is absent.

## Synthetic access

- Account: `demo@exaclim.test`
- Password: `Exaclim2026!`
- Scope: synthetic demonstration only. These published credentials must never protect real workers or a production deployment.
- Initial site: Accra. Expected crew sizes: five, two and one. The two smaller crews form one non-overlapping group of three; they must not appear as separate routine numeric risk rows.

The person recording the demo should rehearse on the final build and record its commit, date and verified test evidence in the release checklist. No test count in the earlier prototype reports establishes readiness of this new dashboard.
