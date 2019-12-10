# Darwincore

Generator for extended/event-based DwC-A, DarwinCore-Archive, files.

## Usage

The dwca_generator library converts a text file containing data and 
metadata to a DwC-A file. It supports the extended DwC-A format only
where the event table is in the center of the mandatory star schema and the 
eMoF, extendednmeasurementorfact, is allowed to reference both the 
event and the occurrence table.

The mapping between the input data file and DwC-A is controlled by an Excel
file. The excel file is divided in a set of sheets:

- **dwc_columns** Lists of terms used in each DwC table.
- **field_mapping** Mapping rules for fields and params/units to the corresponding DwC terms.
- **dwc_keys** Keys used to group data together at different event types and for occurrences.
- **dwc_dynamic_fields** There are some dynamic fields in DwC that can be used as key/value lists.
- **filter** Used to not use specific rows in the input data file. 
- **translate** Used to translate values. Both "source field" and "dwc field" content can be translated.
- **metadata_mapping** Metadata mainly for the EML.XML file describing the whole dataset.
- **README** Short description of the Excel file.

## Installation

To install the library only. Check the dwca_test.py file for usage examples.

    python -m venv venv
    source venv/bin/activate # On Linux and macOS.
    # venv\Scripts\activate # On Windows.
    pip install -m requirements.txt
    pip install git+https://github.com/sharkdata/darwincore
    
    python
    >>> import dwca_generator

## Development

    python -m venv venv
    source venv/bin/activate # On Linux and macOS.
    # venv\Scripts\activate # On Windows.
    pip install -m requirements.txt
    git clone https://github.com/sharkdata/darwincore.git
    
## Contact

Arnold Andreasson, Sweden.
info@mellifica.se
