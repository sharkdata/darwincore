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

Python 3 and git must be installed.

    # Linux:
    git clone https://github.com/sharkdata/darwincore.git
    cd darwincore
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Windows (with example path to Python).
    git clone https://github.com/sharkdata/darwincore.git
    cd darwincore
    C:\Python39\python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

## Development

    python dwca_generator_main.py
    
## Run from the command line

Example for Windows:

    # Go to directory:
    cd darwincore
    # Activate the virtual environment for Python:
    venv\Scripts\activate
    
    # Run the DwC-A generator in Command Line Interface (CLI) mode:
    python dwca_generator_cli.py

## Contact

shark@smhi.se
