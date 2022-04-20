# json-ld-semantics

## Cleaning
After activating your venv, in `src/`:

1. Install everything needed: `pip install -U black isort pre-commit pre-commit-hooks pylint`.
2. Activate `pre-commit`: `pre-commit install`.
   - You can also run `pre-commit` independently: `pre-commit run --all-files`.
3. Check the code: `python3 -m pylint *.py`.

## Testing
### JSON & JSON paths
- You can check that the JSON is valid by using https://jsonformatter.curiousconcept/.
- You can check that the JSON paths are correct by using https://jsonpathfinder.com/.