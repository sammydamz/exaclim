"""Check planning-pack traceability and consistency, not application compliance."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'docs/dashboard-v1'

def read(name):
    return json.loads((ROOT/name).read_text())

def main():
    tasks = read('engineering-tasks.json')
    cases = read('qa-cases.json')
    trace = read('requirements-traceability.json')
    metadata = read('source/metadata.json')
    source_ids = {f'{prefix}{n}' for prefix,count in [('D',15),('P',3),('S',3),('U',3)] for n in range(1,count+1)}
    assert {row['requirement_id'] for row in trace} == source_ids
    assert len(trace) == 24
    extracted = (ROOT/'source/requirements-extracted.txt').read_text()
    assert set(re.findall(r'\b([DPSU]\d+)\.', extracted)) == source_ids
    assert hashlib.sha256((ROOT/'source'/metadata['source_filename']).read_bytes()).hexdigest() == metadata['source_sha256']
    assert [row['id'] for row in tasks] == [f'ENG{i:02}' for i in range(1,28)]
    assert [row['id'] for row in cases] == [f'QA{i:02}' for i in range(1,49)]
    task_ids = {row['id'] for row in tasks}
    case_ids = {row['id'] for row in cases}
    allowed = source_ids | {'UX1'}
    for task in tasks:
        assert set(task['dependencies']) <= task_ids
        assert set(task['qa']) <= case_ids
        assert set(task['requirements']) <= allowed
        assert task['acceptance'] and task['status'] == 'Planned'
    for case in cases:
        assert set(case['requirements']) <= allowed
        assert case['status'] == 'Not run'
        assert all(case.get(k) for k in ['preconditions','steps','expected','evidence','release_gate'])
    complete = set()
    while len(complete) < len(tasks):
        ready = {row['id'] for row in tasks if set(row['dependencies']) <= complete} - complete
        assert ready, 'Engineering dependency cycle'
        complete |= ready
    for row in trace:
        rid = row['requirement_id']
        assert row['engineering_tasks'] == [t['id'] for t in tasks if rid in t['requirements']]
        assert row['qa_cases'] == [c['id'] for c in cases if rid in c['requirements']]
        assert row['engineering_tasks'] and row['qa_cases']
    assert {qa for task in tasks for qa in task['qa']} == case_ids
    for stem,rows in [('engineering-tasks',tasks),('qa-cases',cases),('requirements-traceability',trace)]:
        with (ROOT/(stem+'.csv')).open(newline='') as stream:
            actual = list(csv.DictReader(stream))
        expected = [{k:'; '.join(v) if isinstance(v,list) else v for k,v in row.items()} for row in rows]
        assert actual == expected, stem+' CSV drift'
    engineering = (ROOT/'02-engineering-task-sheet.md').read_text()
    quality = (ROOT/'03-testing-and-quality-plan.md').read_text()
    assert set(re.findall(r'^### (ENG\d+) ', engineering, re.M)) == task_ids
    assert set(re.findall(r'^### (QA\d+) ', quality, re.M)) == case_ids
    baseline = read('baseline/results.json')
    assert all(command['exit_code'] == 0 for command in baseline['commands'])
    print('PASS: 24 original requirements traced to 27 engineering jobs and 48 planned QA cases.')
    print('PASS: source PDF hash, complete source-ID extraction, references, dependency DAG and CSV/JSON parity.')
    print('PASS: existing prototype baseline logs recorded separately; target cases remain Not run.')

if __name__ == '__main__':
    main()
