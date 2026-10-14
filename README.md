# Darwincore
Generator for extended/event-based DarwinCore-Archive (DwC-A) files.

## Usage
This DwC-A generator converts a text file containing data and 
metadata to a DwC-A-file. At the moment only text files embedded in
zip files for the SHARK data format is supported.

The extended DwC-A format is used where the event table is in the center 
of the mandatory star schema and the extendedmeasurementorfact (eMoF) is allowed 
to reference both the event and the occurrence tables.

The mapping between the input data file and DwC-A is controlled by an number
of YAML files located in the directory dwca_config.

## Installation
Darwincore is installed using uv. Follow instructions on https://docs.astral.sh/uv/ to install uv.

With uv, you can run darwincore directly without installing first.
```bash
$ uv run dwca-generato-main 
```

### Virtual environment
You can also run from a virtual environment. First you need to initialize the virtual environment.
```bash
$ uv venv
```

Activate the venv (Mac/Linux):
```bash
$ source venv/bin/activate
```

Activate the venv (Windows) 
```bash
$ venv\Scripts\activate
```

When the environment is activated, you can run the scripts using python:
```bash
(darwincore) $ dwca-generator-cli
```

## Usage
Before running darwincore, add zipped datasets to the directory `data_in/datasets`.

### darwincor-generator-main
Run all configurations:
```bash
$ uv run dwca-generator-main
```

### darwincore-generator-cli
Cli to choose which configuration to run. Without arguments it asks which configuration
to run and whether to fetch the datasets from SHARK instead of using `data_in/datasets`.
```bash
$ uv run dwca-generator-cli
```

Run a specific configuration (row number as listed by the interactive mode, 0 runs all):
```bash
$ uv run dwca-generator-cli --row 3
```

#### Fetching datasets from SHARK
The `fetch` command downloads the datasets from the SHARK API instead of reading them from
`data_in/datasets`. The datasets are selected by `sharkDatatype` and `globSearch` under
`sourceFiles` in each configuration. Configurations without `sharkDatatype` are skipped.
```bash
$ uv run dwca-generator-cli fetch --row 3
$ uv run dwca-generator-cli fetch --row 3 --from 2025-01-01 --to 2025-06-30
```

`--from` and `--to` are optional and filter on the publication date of the dataset version,
not on the sampling date.

Downloaded datasets are stored in `data_in/tmp_datasets` and reused in later runs. When a
newer version of a dataset is downloaded, the older version is moved to
`data_in/tmp_datasets/old_datasets`.

### put-metadatafile-to-yamr
Post yame json metadata files to existing metadata record in yamr.

```bash
$ uv put-metadatafile-to-yamr
```

### publish-to-yamr
Post from yame test to yamr prod.
```bash
$ uv run publish-to-yamr
```

## Development
### Testing
Run all tests:
```bash
$ uv run pytest
```

### Adding dependencies
Add project dependencies:
```bash
$ uv add <name-of-dependency>
```

Add developer dependencies:
```bash
$ uv add --dev <name-of-dependency>
```

### Formatting and linting
The project is configured to use `ruff` for both formatting and linting. Specific rulesets are configured in
`pyproject.toml`.

Run formatting for all files:
```bash
$ uv run ruff format
```

Run formatting for a specific file or directory:
```bash
$ uv run ruff format <path>
```

Run linting of code:
```bash
$ uv run ruff check
```

### pre-commit
Optionally you can activate pre-commit that automatically runs formatting and linting on everything you commit.

Initialize it once:
```bash
$ uv run pre-commit install
```

After this, a commit will fail if there are formatting or linting errors for the specific files. For formatting errors
the fix will be applied to the files but you must accept the changes by adding the affected files to the commit again.

To skip this step for a specific commit (e.g. you just want to store work in progress) you can use the `--no-verify`
flag in git.
```bash
$ git commit --no-verify
```

## Contact

shark@smhi.se
