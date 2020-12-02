# Darwincore

Generator for extended/event-based DarwinCore-Archive (DwC-A) files.

## Usage

This DwC-A generator converts a text file containing data and 
metadata to a DwC-A-file. At the moment only text files embedded in
zip files for SHARK data are supported.

The extended DwC-A format is used where the event table is in the center 
of the mandatory star schema and the extendednmeasurementorfact (eMoF) is allowed 
to reference both the event and the occurrence tables.

The mapping between the input data file and DwC-A is controlled by an number
of YAML files located in the directory dwca_config.

## Installation

    git clone https://github.com/sharkdata/darwincore.git
    cd darwincore
    python3 -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate 
    pip install -r requirements.txt

## Development

    python3 dwca_generator_main.py
    
## Run from the command line

    python3 dwca_generator_cli.py
    
## Contact

shark@smhi.se
