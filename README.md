# Argonodes

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hestiaAI/Argonodes/HEAD?labpath=examples%2Fnotebook%2FExample.ipynb) ![example workflow](https://github.com/hestiaAI/Argonodes/actions/workflows/python-package.yml/badge.svg)

## Introduction

This package aims to facilitate the analysis of large data sets from various sources. The main objective is to allow to efficiently augment datasets, and to create models of them, in the form of JSON-LD frames, to then transform the raw data into JSON-LD, with notably the augmentation of information with semantics.

### Why the name?

Because [JSON](https://en.wikipedia.org/wiki/Jason) explores with Argo[nodes](https://en.wikipedia.org/wiki/Node_(computer_science))!

## Usage

### Setup

This project requires Python 3.7+

1. Clone that repository and cd into it.
2. Create a virtual environment: `python -m venv ./env`
3. Activate that virtual environment: `source ./env/bin/activate`
4. Install the package: `pip install -e .`
5. Drink water, because it is important to stay hydrated.

### Quickstart

A worked example is available [here](./examples/notebook/Example.ipynb).

```python
import json

filename = "/path/to/json/file.json"

with open(filename, "r") as jsonfile:
    json_data = json.loads(jsonfile.read())

from json_ld_semantics.semantics import Tree
tree = Tree(json_data)

from json_ld_semantics.model import Model
model = Model(name="My model", traversal=tree.export_traversal())

# or
model = Model(name="My model").add_files(filename).process_files()
```

### Applications

Example:
```json
{
   "url":"https://example.com/me",
   "user":"Jean-Michel",
   "age":"42"
}
```
- Pickle the model for archive.
- Export to JSON.
   
   ```json
   {
      "$.url":{
         "foundType":"str",
         "descriptiveType":"https://schema.org/url",
         "unique":false,
         "default":"None",
         "description":"URL to the personal page of the person.",
         "example":[
            "https://domain.com/me"
         ],
         "regex":"https:\/\/domain\\.com/[a-z]+",
         "traversal":{
            
         }
      }
   }
   ```
- Export to JSON-LD frame (Soon ™️).
- Export to Markdown.

   | path | foundType | descriptiveType | description                             |
   |-----------|---|-----------------------------------------|---|
   | `$` | Root      | https://schema.org/Person | A specific person.                      |
   | `$.url` | str       | https://schema.org/url | URL to the personal page of the person. |
   | `$.user` | str       | https://schema.org/name | Name of the person.                     |
   | `$.age` | int       | https://example.org/Age | Age of the person.                      |
- Export to SQL (Soon ™️).

## Contributing

To contribute, fork the project, and open a PR.

### Environment

1. First, activate your venv, as explained in [Usage](#usage).
2. Install dev requirements: `pip install -r requirements/dev.txt`.
3. Activate `pre-commit`: `pre-commit install`.

Notes:

- You can run `pre-commit` independently: `pre-commit run --all-files`.
- If, for some reason, you need to commit without a check, use ` git commit --no-verify [...]`.
- You can check you code using `python3 -m pylint *.py`.

### Testing

We are in need of tests! Write them under the [`tests`](./tests/) folder.
#### JSON & JSON paths
- You can check that the JSON is valid by using [https://jsonformatter.curiousconcept.com/](https://jsonformatter.curiousconcept.com/).
- You can check that the JSON paths are correct by using [https://jsonpathfinder.com/](https://jsonpathfinder.com/).

### Documentation

1. `cd docs/`
2. `sphinx-apidoc -o source/ ../src/`
3. `make html`

### Examples

1. First, activate your venv, as explained in [Usage](#usage).
2. Install examples requirements: `pip install -r requirements/examples.txt`.

Notes:
- If you are changing one of the [examples](./examples/), and want to keep track of the change: `git update-index --no-assume-unchanged ./examples/name_of_the_file`.
- Else, please use `git update-index --assume-unchanged ./examples/`.
