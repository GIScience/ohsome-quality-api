# Contributing

## How to Contribute

Please contribute to this repository through creating [issues](https://github.com/GIScience/ohsome-quality-api/issues/new) and [pull requests](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests).


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

A merge request can be made even if the branch is not ready to yet to be merged. When doing so please mark them as Work-in-Progress by writing `WIP` at the beginning of the title. This way people/reviewer know that currently someone is working to address an issue. This gives them the opportunity share their thoughts knowing that the merge request is still subject to change and does not need a full review yet.

The [CHANGELOG.md](CHANGELOG.md) describes changes made in a merge request. It should contain a short description of the performed changes, as well as (a) link(s) to issue(s) or merge request.


#### Review Process

1. Dev makes a PR/MR.
2. Rev reviews and raises some comments.
3. Dev addresses the comments and leaves responses explaining what has to be done. In cases where Dev just implemented Rev's suggestion, a simple "Done" is sufficient.
4. Rev reviews the changes and
    - If Rev is happy with a change, then Rev resolves the comment.
    - If Rev is still unsatisfied with a change, then Rev adds another comment explaining what is still missing.
5. Restart from 3 until all comments are resolved.


### Git Workflow

All development work is based on the main branch (`main`). Merge requests are expected to target the main branch.


## Style Guide

### Tools

This project uses [`ruff`](https://github.com/astral-sh/ruff) to ensure consistent code style. See the `pyproject.toml` file for configuration.


#### A Note on the Configuration

```bash
uv run ruff format .
uv run ruff check --fix .
```


### Pre-Commit

In addition, [pre-commit](https://pre-commit.com/) is set up to run those tools prior to any git commit. In contrast to above described commands running these hooks will not apply any changes to the code base. Instead, 'pre-commit' checks if there would be any changes to be made. In that case simply run above commands manually.


## Tests

Please provide [tests](/docs/development_setup.md#tests).


## Miscellaneous

- How are indicators structured? -> [docs/indicator.md](/docs/indicator.md).
