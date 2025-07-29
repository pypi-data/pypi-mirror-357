# llm-fragments-sourcehut

[![PyPI](https://img.shields.io/pypi/v/llm-fragments-sourcehut.svg)](https://pypi.org/project/llm-fragments-sourcehut/)
[![Changelog](https://img.shields.io/badge/changelog-refs-brightgreen)](https://git.sr.ht/~amolith/llm-fragments-sourcehut/refs)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://git.sr.ht/~amolith/llm-fragments-sourcehut/tree/main/item/LICENSE)

Load SourceHut repository contents and todos as fragments

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-fragments-sourcehut
```

## Repo contents

Use `-f srht:~user/repo` to include every text file from the specified SourceHut repository as a fragment.

The prefix accepts the standard `~user/repo` shorthand format. For example:

```bash
llm -f srht:~amolith/adresilo-server 'suggest new features for this tool'
```

There's also a fallback to allow `srht:user/repo`.

## TODOs

Use `-f todo:~user/repo/issue` to query SourceHut's GraphQL API for the ticket
details, render them as Markdown, and include them as fragments.

```bash
# Use default todo.sr.ht instance
llm -m 'openrouter/google/gemini-2.5-flash-lite-preview-06-17' \
    -f todo:~amolith/willow/47 'Briefly describe the outcome of this ticket.'

# Specify a different instance, requiring HTTPS
llm -m 'openrouter/google/gemini-2.5-flash-lite-preview-06-17' \
    -f todo:todo.sr.ht/~amolith/willow/47 'Briefly describe the outcome of this ticket.'

# Specify a different instance, not requiring HTTPS
llm -m 'openrouter/google/gemini-2.5-flash-lite-preview-06-17' \
    -f todo:http://192.168.1.28/~amolith/willow/47 'Briefly describe the outcome of this ticket.'
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash
cd llm-fragments-sourcehut
python -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
llm install -e '.[test]'
```

To run the tests:

```bash
python -m pytest
```

## Contributions are welcome

This repo is on SourceHut ([repo][srhtrepo]) and Radicle ([web][radrepo],
`rad:z4RLodmmoj1APnZxC1onrYBuzuHtC`, [what is Radicle?][rad]).

[srhtrepo]: https://git.sr.ht/~amolith/llm-fragments-sourcehut
[radrepo]: https://radicle.secluded.site/nodes/seed.secluded.site/rad:z4RLodmmoj1APnZxC1onrYBuzuHtC
[rad]: https://radicle.xyz
