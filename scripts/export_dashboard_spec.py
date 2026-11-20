"""Export the dashboard PRD, engineering sheet and quality plan as PDFs."""
import argparse
import importlib.util
import json
import zipfile
from pathlib import Path
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT/'docs/dashboard-v1'
module = importlib.util.spec_from_file_location('exaclim_pdf_base', ROOT/'scripts/export_pdfs.py')
base = importlib.util.module_from_spec(module)
module.loader.exec_module(base)
DOCUMENTS = [
    ('01-product-requirements.md', 'Exaclim-Dashboard-PRD.pdf', 'Exaclim Dashboard — Product Requirements'),
    ('02-engineering-task-sheet.md', 'Exaclim-Dashboard-Engineering-Tasks.pdf', 'Exaclim Dashboard — Engineering Task Sheet'),
    ('03-testing-and-quality-plan.md', 'Exaclim-Dashboard-Testing-and-Quality.pdf', 'Exaclim Dashboard — Testing and Quality Plan'),
]

def footer(canvas, doc):
    canvas.setFont(base.FONT, 7)
    canvas.setFillColor(colors.HexColor('#52656b'))
    canvas.drawString(45, 25, 'Exaclim | Dashboard V1 planning | 19 November 2026')
    canvas.drawRightString(566, 25, str(doc.page))

def render(path, title, content):
    document = SimpleDocTemplate(str(path), pagesize=(612,792), leftMargin=45,
                                 rightMargin=63, topMargin=42, bottomMargin=43,
                                 title=title, author='Exaclim Team')
    document.build(content, onFirstPage=footer, onLaterPages=footer)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='/workspace/artifacts/exaclim-dashboard-spec')
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    combined = [base.paragraph('Exaclim Supervisor Dashboard', 'Title'),
                base.paragraph('PRD, Engineering Tasks and Quality Plan', 'Heading2'),
                base.paragraph('Version 1.0 · 19 November 2026'), Spacer(1,18),
                base.paragraph('Prepared from the user-supplied two-page dashboard requirements and Deel visual references. All 24 original requirements are traced to 27 engineering jobs and 48 planned acceptance cases.'),
                base.paragraph('This is a build-planning package. The redesigned dashboard has not been implemented. All target QA cases remain Not run. The existing prototype separately passed 23 Python tests and 22 Chromium checks; those do not prove target V1 compliance.'),
                base.paragraph('Contents', 'Heading2'),
                base.paragraph('1. Product Requirements — scope, behavior, privacy, emergency semantics and proposed decisions.'),
                base.paragraph('2. Engineering Task Sheet — assignable work, dependencies, contracts and acceptance criteria.'),
                base.paragraph('3. Testing and Quality Plan — detailed cases, release gates and evidence requirements.'),
                base.paragraph('Editable task, QA and traceability sheets are included in the ZIP. Watch/phone qualification, language selection, reviewed risk/acclimatization policy and real-data release gates remain explicit dependencies.')]
    for source, filename, title in DOCUMENTS:
        text = (SPEC/source).read_text()
        render(output/filename, title, base.flowables(text))
        combined.extend([PageBreak(), *base.flowables(text)])
        print(output/filename)
    combined_name = 'Exaclim-Dashboard-Full-Planning-Pack.pdf'
    render(output/combined_name, 'Exaclim Dashboard — Full Planning Pack', combined)
    print(output/combined_name)
    archive = output/'Exaclim-Dashboard-PRD-Tasks-QA.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as package:
        for pdf in sorted(output.glob('*.pdf')):
            package.write(pdf, 'pdfs/'+pdf.name)
        for path in sorted(SPEC.rglob('*')):
            if path.is_file():
                package.write(path, 'editable-and-source/'+str(path.relative_to(SPEC)))
        for script in ['check_dashboard_spec.py', 'export_dashboard_spec.py', 'export_pdfs.py']:
            package.write(ROOT/'scripts'/script, 'scripts/'+script)
        package.write(ROOT/'requirements-pdf.txt', 'requirements-pdf.txt')
    print(archive)

if __name__ == '__main__':
    main()
