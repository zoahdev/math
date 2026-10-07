# Community contribution proposal

This branch contains independently prepared community materials for `openai/math`. It is not an official OpenAI release or an accepted upstream contribution.

## Catalogue path checker

The standard-library Python tool in `tools/check_catalogue.py` checks the unquoted local paper IDs used by `lean/formalization.yaml` and the challenge/solution module paths in tracked `lean/ComparatorChallenges/*.json` files against Git's case-sensitive `HEAD` tree. It does not execute repository scripts, compile Lean, check theorem equivalence, or certify mathematical results.

From the repository root, with Python 3.8+ and Git installed:

```sh
python tools/check_catalogue.py
python tools/test_catalogue.py
```

The checker reads the working-tree catalogue and JSON files; use a clean checkout for reproducible results. It requires these files to be present even when using sparse checkout. Other YAML source-ID formats are outside its scope. Exit codes: 0 means all checked paths resolve, 1 means a catalogue/configuration issue was found, and 2 means the repository or catalogue could not be read.

At upstream commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, the checker resolved **162 source paths and 405 Comparator configurations**, with no path errors. Integration tests passed for a valid fixture, case mismatch, missing module, missing fields, non-object/malformed JSON, a sparse checkout gap, and a missing catalogue. Validation used Python 3.8.6 on Windows. No Lean proof checks were run.

## Chinese reading guide

[READING.zh-CN.md](READING.zh-CN.md) provides source links, a reading sequence, an explanation of verification scope, and a worked navigation example for family 003. Its six distinct local link destinations were checked against the upstream repository.

## Upstream status

As of 2026-10-07, upstream PR creation is restricted to collaborators, and Issues and Discussions are disabled. These materials are offered for review; their publication here does not imply upstream acceptance or collaborator status. Attribution should remain attached to the original GitHub commits if the maintainers elect to incorporate them.
