# Contributing

- [Documentation](#documentation)
  * [Available resources](#available-resources)
- [Development](#development)
  * [Commits](#commits)
  * [Pull requests](#pull-requests)
  * [Tests](#tests)
  * [Documentation](#documentation-1)
  * [Examples](#examples)
- [Data](#data)
  * [Data sources](#data-sources)
  * [Semantics](#semantics)


First of all, thank you for taking the time to help this project, it means a lot.

To sum-up:
* You know how to Python? You can help the project by [reviewing code](https://github.com/hestiaAI/Argonodes/pulls), [fixing bugs](https://github.com/hestiaAI/Argonodes/issues), and [adding features](https://github.com/hestiaAI/Argonodes/issues)!
* You know how to data analysis? You can help the project by [providing insights about data sources](https://github.com/hestiaAI/Argonodes/wiki)!
* No matter what you know, you can always report a bug or [ask for a feature](https://github.com/hestiaAI/Argonodes/issues), [discuss about the project](https://github.com/hestiaAI/Argonodes/discussions), or [get in touch](https://hestia.ai/en/#contact)!

## Documentation

Documentation is particularly important for us, and for this project in particular. Thus, any help is welcome, let alone fixing typos.

- In general, you should not hesitate to be clear about "how it works"!
- This means documenting when you add something, documenting when you change something, documenting when you test something, ...
- In short, documenting so that the next person has to look for it as little as possible!

### Available resources

These ressources are available to guide the user with Argonode. Feel free to complete any particular aspect of any of those.

* [Technical reference](https://github.com/hestiaAI/Argonodes/tree/master/docs): Descriptions of all available classes, modules, methods and arguments. It is either available directly on the repo, or [online](https://hestiaai.github.io/Argonodes/).
  * See [Documentation](#documentation) for more information about generating it.
* [Wiki](https://github.com/hestiaAI/Argonodes/wiki/): Contains both explanations for how the package works, and schemas for structured data.
  * This is supposed to be both a manual and a [semantic reference](#semantics). Feel free to complete any of these.
* [Examples](https://github.com/hestiaAI/Argonodes/tree/master/examples): Several ready-to-use examples for that package.
  * You have an idea for an example that is missing? Please share it with us!

## Development

Before anything, make sure you followed the [quickstart](./README.md#quickstart--i-want-to-work-on-argonodes).

### Commits

We use pre-commits so that the code is pretty and quite standard. You can find what is happening in the [.pre-commit-config.yaml](./.pre-commit-config.yaml) and [pyproject.toml](./pyproject.toml) files, but basically, for each commit:

- [black](https://github.com/psf/black) formats the code correctly.
- [isort](https://pycqa.github.io/isort/) sorts the imports.
- [bump2version](https://github.com/c4urself/bump2version) increments the patch part of the package's version.

Regarding commit messages:
- [Don't do that](https://xkcd.com/1296/), and we're cool.
- When fixing an issue, please explicit it using the "Fix" keyword, and the exact title of the issue. (e.g., "Fix #42: Loader does not load").

Notes:

- You can run pre-commit independently using `pre-commit run --all-files`
- If, for some reason, you need to commit without a check, use `git commit --no-verify [...]`
- You can check you code using `python3 -m pylint *.py`

### Pull requests

We follow the [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow): all code contributions are submitted via a pull request towards the main branch.

1. Fork the project or open a new branch.
2. Manually bump minor version in `setup.py`.
3. Complete your modifications.
4. Open a PR.

Moreover:
- When creating a new branch to fix an issue, please refer to the issue in the branch name, starting by its number (e.g., `42-loader-does-not-load`).
- The title of your PR must be explicit.
- When fixing an issue, please explicit it using the "Fix" keyword, and the exact title of the issue. (e.g., "Fix #42: Loader does not load").
- The description may contain any additional information (the more the merrier!), but do not forget to mirror it in the documentation when needed.
- Please take into account that your PR will result in one commit; you may want to squash/rebase yourself beforehand.
- Please link the issues and the PR when needed.

### Tests

We are in need of tests! Write them under the [`tests`](./tests/) folder.

- You can check that JSON files are valid by using [https://jsonformatter.curiousconcept.com/](https://jsonformatter.curiousconcept.com/).
- You can check that JSON paths are valid by using [https://jsonpathfinder.com/](https://jsonpathfinder.com/).

### Documentation

The documentation is generated directly from the [docs](./docs/) folder, and pushed through a [GitHub Action](https://github.com/hestiaAI/Argonodes/actions/workflows/gh-pages.yml) directly to [another branch](https://github.com/hestiaAI/Argonodes/tree/gh-pages). From that branch, another [GitHub Action](https://github.com/hestiaAI/Argonodes/actions/workflows/pages/pages-build-deployment) publish it [online](https://hestiaai.github.io/Argonodes/).

You can regenerate locally all the autodoc based on docstring using the following commands:

1. Get in the correct folder: `cd docs/`
2. Generate: `sphinx-apidoc -o source/ ../src/`
3. Check the result: `make html`

### Examples

- You need to install both dev and examples requirements: `pip install -r requirements/dev.txt; pip install -r requirements/examples.txt`
- If you are changing one of the [examples](./examples/), and want to keep track of the change: `git update-index --no-assume-unchanged ./examples/name_of_the_file`.
- Else, please use `git update-index --assume-unchanged ./examples/`.
- Remember to clean Notebooks when possible!

## Data

The addition of data sources and semantic descriptions, to make them available to the community, is of course always welcome.

All the necessary information is available on the [wiki](https://github.com/hestiaAI/Argonodes/wiki); a summary is available below.

### Data sources

We want to ensure that as many source data models as possible are available to as many people as possible. This implies on the one hand regularly testing and updating existing models on new exports, but also completing them with missing sources.

More information about the format for adding semantic descriptions can be found [here](https://github.com/hestiaAI/Argonodes/wiki/Template%3AData-source).

### Semantics

A large part of the work is to make semantic descriptions of the concepts that can be found in the data sources. Although it is often possible to exploit pre-existing sources, such as [schema.org](https://schema.org), sometimes more complex concepts appear, which need to be described correctly.

More information about the format for adding semantic descriptions can be found [here](https://github.com/hestiaAI/Argonodes/wiki/Template%3AScheme).
