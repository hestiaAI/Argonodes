# json-ld-semantics

## Setup

This project requires Python 3.7

1. Create a virtual environment

```sh
$ python -m venv ./env --upgrade-deps
```

2. Activate the virtual environment

POSIX:

```sh
$ source env/bin/activate
```

Windows PowerShell:

```sh
PS C:\> env\Scripts\Activate.ps1
```

Windows cmd.exe

```sh
C:\> env\Scripts\activate.bat
```

3. After activating the environment, install required libraries:

```sh
$ pip install -U -r requirements.txt
```

4. Activate pre-commit

```sh
$ pre-commit install
```

You can also run `pre-commit` independently:

```sh
$ pre-commit run --all-files
```

## Linting

```sh
$ python -m pylint *.py
```

## Testing

TODO

### JSON & JSON paths

- You can check that the JSON is valid by using https://jsonformatter.curiousconcept/.
- You can check that the JSON paths are correct by using https://jsonpathfinder.com/.
