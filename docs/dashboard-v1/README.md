# Exaclim Supervisor Dashboard V1 — Delivery Pack

Prepared 19 November 2026 from the user's two-page dashboard requirements PDF and the previously supplied Deel screenshot references.

1. `01-product-requirements.md`: product scope, behavior, source changes, proposed decisions and acceptance targets.
2. `02-engineering-task-sheet.md`: 27 engineering jobs, dependency order, owners by role, rough effort and technical contracts.
3. `03-testing-and-quality-plan.md`: 48 target test cases, release gates, quality checklist and existing-prototype baseline results.

Editable sheets: `engineering-tasks.csv`, `qa-cases.csv`, and `requirements-traceability.csv`. JSON companions preserve structured data for tooling. `source/` contains the original source PDF, text extraction and SHA-256 metadata; `baseline/` contains the old prototype's newly executed 23 Python/22 browser regression evidence.

The original 24 IDs (D1–D15, P1–P3, S1–S3, U1–U3) are all linked to tasks and target tests. All new target QA cases are Not run. Passing old tests is not evidence of new requirements being implemented. The main product changes are supervisor-only UI, watch/crew-phone architecture, grouping to a minimum of three, named help exception, durable acknowledgement and watch-local private issuance settings.

Run document checks with `python3 scripts/check_dashboard_spec.py`. Export PDFs with `python3 scripts/export_dashboard_spec.py --output /workspace/artifacts/exaclim-dashboard-spec`. The export requires the optional ReportLab dependency already used by the project's report tooling. This work package changes planning documents and tooling only; it does not silently build or claim the redesigned application.

Current implementation status: [27-job engineering audit](04-implementation-audit.md), with [editable CSV](implementation-audit.csv) and [JSON](implementation-audit.json). Updated 20 November 2026.
