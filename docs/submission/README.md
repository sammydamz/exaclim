# Exaclim: Future Health submission pack

Prepared 20 November 2026 from the organizer’s 16-slide template.

- `Exaclim_Future_Health_Submission.pptx`: editable completed deck, including a native editable architecture diagram and source notes.
- `Exaclim_Future_Health_Submission.pdf`: rendered PDF for review/upload where accepted.
- `Exaclim_Architecture.pdf` / `.png`: standalone architecture slide.
- `validation.json`: checks, version boundary and document digest.

The team-member slide and team name/size fields are intentionally unfilled. The capability answer is 679 characters. The user confirmed no relationships to disclose; slide 14 records that declaration. All other requested sections are populated.

The deck separates the checked hosted core from simulated watch/Android behaviour and unreleased operational extensions. It does not claim field/clinical validation or confirmed pilot partners. Application login/logout was checked successfully on the hosted URL during preparation.

Primary sources were verified during preparation: WHO/WMO (2025), NIOSH criteria and workplace recommendations, Open-Meteo terms and attribution conditions, Ghana DPC and Adafruit product 4062. Source links and detailed claim boundaries are in PowerPoint speaker notes and the final reference slide. Installed package licences were also checked; UI SDK is Apache-2.0.

The organizer’s artwork and overall slide sequence are retained. The PDF was rendered and checked for clipped text; the team-slide XML was compared canonically with the source and is unchanged.

Rebuild with the original uploaded template:

```sh
python3 -m pip install -r requirements-submission.txt
python3 scripts/build_submission_deck.py --template /path/to/template.pptx --output-dir /path/to/output
soffice --headless --convert-to pdf --outdir /path/to/output /path/to/output/Exaclim_Future_Health_Submission.pptx
```

After any future application release, recheck application access and update the feature/evidence boundary before regenerating the deck. Team entries still need to be supplied by the team.
