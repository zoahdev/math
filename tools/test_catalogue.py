"""Integration checks using a temporary Git repository; no upstream writes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

tool = Path(__file__).with_name('check_catalogue.py')
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    files = {
        'lean/formalization.yaml': 'sources:\n  - title: Example\n    id: ../preprints/Example/paper.pdf\n',
        'preprints/Example/paper.pdf': 'fixture, not a PDF',
        'lean/ComparatorChallenges/Example.lean': '-- fixture',
        'lean/OAI/Example.lean': '-- fixture',
        'lean/ComparatorChallenges/Example.json': json.dumps({'challenge_module': 'ComparatorChallenges.Example', 'solution_module': 'OAI.Example'}),
    }
    for path, content in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture'], check=True)

    def expect(code, text):
        result = subprocess.run([sys.executable, str(tool), '--repo', str(root)], capture_output=True, text=True)
        assert result.returncode == code, result.stdout + result.stderr
        assert text in result.stdout + result.stderr, result.stdout + result.stderr

    expect(0, '0 errors')
    catalogue = root / 'lean/formalization.yaml'
    catalogue.write_text(files['lean/formalization.yaml'].replace('Example/paper.pdf', 'example/paper.pdf'), encoding='utf-8')
    expect(1, 'missing source')
    catalogue.write_text(files['lean/formalization.yaml'], encoding='utf-8')
    config = root / 'lean/ComparatorChallenges/Example.json'
    config.write_text(json.dumps({'challenge_module': 'ComparatorChallenges.Example', 'solution_module': 'OAI.Absent'}), encoding='utf-8')
    expect(1, 'points to missing lean/OAI/Absent.lean')
    config.write_text('{}', encoding='utf-8')
    expect(1, 'missing or invalid solution_module')
    config.write_text('[]', encoding='utf-8')
    expect(1, 'configuration must be a JSON object')
    config.write_text('{', encoding='utf-8')
    expect(1, 'Example.json')
    config.unlink()
    expect(1, 'Example.json')
    catalogue.unlink()
    expect(2, 'Cannot check catalogue')
print('PASS: valid fixture, case mismatch, missing module, missing fields, non-object JSON, malformed JSON, sparse checkout gap, missing catalogue')
