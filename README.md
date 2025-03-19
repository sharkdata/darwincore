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
$ uv run dwca_generator_main.py 
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
(darwincore) $ python dwca_generator_cli.py
```

## Usage
Before running darwincore, add zipped datasets to the directory `data_in/datasets`.

### darwincor-generator-main
Run all configurations:
```bash
$ uv run dwca_generator_main.py
```

### darwincore-generator-cli
Cli to choose which configuration to run.
```bash
$ uv run dwca_generator_cli.py
```

## Testing
Run all tests:
```bash
$ uv run pytest
```

To run pytest in the virtual environment you must have run the above command at least once. From withing the virtual
environment you can then run:
```bash
(darwincore) $ pytest
```

## Development
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
