# Argonodes

<p align="center"><img src="./img/logo/argonodes-logo-color.png"/></p>

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hestiaAI/Argonodes/HEAD?labpath=examples%2Fnotebook%2FExample.ipynb) ![example workflow](https://github.com/hestiaAI/Argonodes/actions/workflows/python-package.yml/badge.svg) [![Technical documentation](https://github.com/hestiaAI/Argonodes/actions/workflows/gh-pages.yml/badge.svg)](https://github.com/hestiaAI/Argonodes/actions/workflows/gh-pages.yml)

* [Introduction](#introduction)
  + [Why the name?](#why-the-name-)
* [Setup](#setup)
  + [Quickstart: I directly want to use Argonodes](#quickstart--i-directly-want-to-use-argonodes)
  + [Quickstart: I want to play with the examples of Argonodes](#quickstart--i-want-to-play-with-the-examples-of-argonodes)
  + [Quickstart: I want to work on Argonodes](#quickstart--i-want-to-work-on-argonodes)
* [Usage example](#usage-example)
  + [Ugly working one liner](#ugly-working-one-liner)
* [Contributing](#contributing)

## Introduction

This package aims to facilitate the analysis of large data sets from various sources. The main objective is to allow to efficiently augment datasets, and to create models of them, in the form of JSON-LD frames, to then transform the raw data into JSON-LD, with notably the augmentation of information with semantics.

### Why the name?

Because [JSON](https://en.wikipedia.org/wiki/Jason) explores with Argo[nodes](https://en.wikipedia.org/wiki/Node_(computer_science))!

## Setup

This project requires Python 3.7+.

### Quickstart: I directly want to use Argonodes

> Note: In general, it is recommended to create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) before using Python packages. You can use `python -m venv ./env` then `source ./env/bin/activate` if needed.

- You can simply use `pip install -e git+ssh://git@github.com/hestiaAI/Argonodes.git#egg=argonodes`. That's it.
- You can also directly add `-e git+ssh://git@github.com/hestiaAI/Argonodes.git#egg=argonode` in the requirements.txt of your project.

### Quickstart: I want to play with the examples of Argonodes

1. Clone that repository and cd into it.
2. (If not done already) Create a virtual environment: `python -m venv ./env`
3. (If not done already) Activate that virtual environment: `source ./env/bin/activate`
4. Install what is needed: `pip install -r requirements/examples.txt`
5. Go inside the examples directory: `cd examples`
6. Drink water, because it is important to stay hydrated.

### Quickstart: I want to work on Argonodes

> Note: Please read the [Contributing](#contributing) part!

1. Clone that repository and cd into it.
2. (If not done already) Create a virtual environment: `python -m venv ./env`
3. (If not done already) Activate that virtual environment: `source ./env/bin/activate`
4. Install what is needed: `pip install -r requirements/dev.txt`
5. Activate pre-commits: `pre-commit install`
6. Remember that you probably have a cup of tea or coffee getting cold.

## Usage example

You can find more information on how to use Argonodes in our [wiki](https://github.com/hestiaAI/Argonodes/wiki/General-usage-examples).

A worked example is available [here](./examples/notebook/Example.ipynb). Make sure you followed the [Quickstart](#quickstart--i-want-to-play-with-the-examples-of-argonodes) if you want to play with it directly.

```python
import json

filename = "/path/to/json/file.json"

# Load your raw data
with open(filename, "r") as jsonfile:
    json_data = json.loads(jsonfile.read())

# Create a Tree for exploration
from json_ld_semantics.semantics import Tree
tree = Tree(json_data)

# ... Do some work on the Tree

# Create a Model from the Tree
from json_ld_semantics.models import Model
model = Model(name="My model", trees=tree)

# ... Do some work on the Model

model.export_traversal(scheme="markdown")
```

### Ugly working one liner

```python
# This will create a Model to play with directly from raw data.
with open("input.json", "r") as json_file:
    model = Model(Tree(json.load(json_file)))
```

## Contributing

First of all, thank you for taking the time to help this project, it means a lot.

Please read our [CONTRIBUTING](CONTRIBUTING.md) file, which contains guidelines, information on what you can do to help the project, and good practices to apply.

To sum-up:
* You know how to Python? You can help the project by [reviewing code](https://github.com/hestiaAI/Argonodes/pulls), [fixing bugs](https://github.com/hestiaAI/Argonodes/issues), and [adding features](https://github.com/hestiaAI/Argonodes/issues)!
* You know how to data analysis? You can help the project by [providing insights about data sources](https://github.com/hestiaAI/Argonodes/wiki)!
* No matter what you know, you can always report a bug or [ask for a feature](https://github.com/hestiaAI/Argonodes/issues), [discuss about the project](https://github.com/hestiaAI/Argonodes/discussions), or [get in touch](https://hestia.ai/en/#contact)!
