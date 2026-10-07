#!/usr/bin/env python3
"""Check source and Comparator module paths against Git's case-sensitive tree.

Requires Python 3.8+ and Git. This checks catalogue wiring, not Lean proofs.
Run from a checkout containing lean/formalization.yaml and challenge JSON files.
"""
import argparse
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys


def check(repo):
    result = subprocess.run(
        ['git', '-C', str(repo), 'ls-tree', '-r', '-z', '--name-only', 'HEAD'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    paths = set(result.stdout.decode('utf-8').split('\0'))
    catalogue = repo / 'lean/formalization.yaml'
    sources = 0
    errors = []
    for line_no, line in enumerate(catalogue.read_text(encoding='utf-8').splitlines(), 1):
        match = re.match(r'^\s+id: (\.\./preprints/.+)$', line)
        if not match:
            continue
        sources += 1
        target = posixpath.normpath(posixpath.join('lean', match.group(1)))
        if target not in paths:
            errors.append('lean/formalization.yaml:{}: missing source {}'.format(line_no, target))
    if not sources:
        errors.append('No unquoted ../preprints/ source IDs found; check catalogue format.')

    configs = sorted(p for p in paths if p.startswith('lean/ComparatorChallenges/') and p.endswith('.json'))
    if not configs:
        errors.append('No tracked Comparator challenge JSON files found.')
    for path in configs:
        try:
            data = json.loads((repo / path).read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                raise ValueError('configuration must be a JSON object')
            for field in ('challenge_module', 'solution_module'):
                module = data.get(field)
                if not isinstance(module, str) or not module:
                    errors.append('{}: missing or invalid {}'.format(path, field))
                    continue
                target = 'lean/' + module.replace('.', '/') + '.lean'
                if target not in paths:
                    errors.append('{}: {} points to missing {}'.format(path, field, target))
        except (OSError, ValueError) as exc:
            errors.append('{}: {}'.format(path, exc))
    return sources, len(configs), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd(), help='repository root (default: current directory)')
    args = parser.parse_args()
    try:
        sources, configs, errors = check(args.repo.resolve())
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        print('Cannot check catalogue: {}'.format(exc), file=sys.stderr)
        return 2
    print('Checked {} source paths and {} Comparator configurations.'.format(sources, configs))
    for error in errors:
        print(error, file=sys.stderr)
    print('{} errors. No Lean compilation or mathematical verification performed.'.format(len(errors)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
