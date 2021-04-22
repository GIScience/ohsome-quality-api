# Contributing

## How to Contribute

Please contribute to this repository through creating [issues](https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-analyst/-/issues/new) and [merge requests](https://docs.gitlab.com/ce/user/project/merge_requests/creating_merge_requests.html#new-merge-request-from-your-local-environment).


### Issues

Bugs reports and enhancement suggestions are tracked via issues. Each issue can contain following information:

- A clear and descriptive title
- Description
- Current behavior and expected behavior
- Error message and stack trace

Issues should serve as the basis for creating a merge request. They should have at least one tag associated with them.


### Merge Requests

Merge requests are created to address one single issue or multiple. Either the assignee or the creator of the merge request is responsible for merging.
Each merge request has to be approved by at least one reviewer before merging it. A person can be assigned as reviewer by either mark them as such or asking for a review by tagging the person in the description/comment of the merge request.

A merge request can be made even if the branch is not ready to yet to be merged. When doing so please mark them as Work-in-Progress by writing `WIP` at the beginning of the title. This way people/reviewer know that currently someone is working to address an issue. This gives them the opportunity share their thoughts knowing that the merge request is still subject to changes and does not need a full review yet.

The [CHANGELOG.md](CHANGELOG.md) describes changes made in a merge request. It should contain a short description of the performed changes, as well as (a) link(s) to issue(s) or merge request.


#### Review Process

1. Dev makes a PR/MR.
2. Rev reviews and raises some comments.
3. Dev addresses the comments and leaves responses explaining what has be done. In cases where Dev just implemented Rev's suggestion, a simple "Done" is sufficient.
4. Rev reviews the changes and
    - If Rev is happy with a change, then Rev resolves the comment.
    - If Rev is still unsatisfied with a change, then Rev adds a further comment explaining what is still missing.
5. Restart from 3 until all comments are resolved.


### Git Workflow

All development work is based on the main branch (`master`). Merge requests are expected to target the main branch.


## Style Guide

### Tools

This project uses [black](https://github.com/psf/black), [flake8](https://gitlab.com/pycqa/flake8) and [isort](https://github.com/PyCQA/isort) to ensure consistent codestyle. Those tools should already be installed in your virtual environment since they are dependencies defined in the `pyproject.toml` file.

The configuration of flake8 and isort is stored in `setup.cfg`.

Run black, flake8 and isort with following commands:

```bash
cd workers/
black .
flake8 .
isort .
```

Black and isort will autoformat the code. Flake8 shows only what should be fixed but will not make any changes to the code base.

Changes can be checked manually with `git diff`.

> Tip: Mark in-line that flake8 should not raise any error: `print()  # noqa`


### Pre-Commit

In addition [pre-commit](https://pre-commit.com/) is setup to run those tools prior to any git commit. In contrast to above described commands running these hooks will not apply any changes to the code base. Instead 'pre-commit' checks if there would be any changes to be made. In that case simply run above commands manually.


## Tests

Please provide [tests](docs/development_setup.md#tests).


## Miscellaneous

- Troubleshooting -> [docs/troubleshooting.md](docs/troubleshooting.md)
- How to create a new indicator? -> [docs/indicator_creation.md](docs/indicator_creation.md).
