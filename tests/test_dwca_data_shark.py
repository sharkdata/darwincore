from darwincore.dwca_generator import dwca_filters, dwca_translate
from darwincore.dwca_generator.dwca_data_shark import DwcaDataSharkStandard
from tests import fixtures


def test_add_shark_dataset_windows_zip_file():
    # Given shark data
    given_shark_data_rows = [
        {"parameter": "test", "value": "1"},
        {"parameter": "test", "value": "2"},
        {"parameter": "test", "value": "3"},
        {"parameter": "test", "value": "4"},
        {"parameter": "test", "value": "5"},
    ]

    # Given the data is added to a csv file
    given_shark_csv = fixtures.data_rows_as_csv(given_shark_data_rows)

    # Given the csv is added to a zip file generated on Windows
    given_windows_zip_file = fixtures.given_windows_shark_zip(given_shark_csv)

    # Given a DwcaDataSharkStandard object
    given_filters = dwca_filters.DwcaFilters([])
    given_translate = dwca_translate.DwcaTranslate([])
    shark_data = DwcaDataSharkStandard(None, given_filters, given_translate)

    # When adding the shark data zip file to the DwcaDataSharkStandard object
    shark_data.add_shark_dataset(given_windows_zip_file)

    # Then the given data is added
    shark_data_rows = shark_data.get_data_rows()
    assert shark_data_rows == given_shark_data_rows


def test_add_shark_dataset_posix_zip_file():
    # Given shark data
    given_shark_data_rows = [
        {"parameter": "test", "value": "1"},
        {"parameter": "test", "value": "2"},
        {"parameter": "test", "value": "3"},
        {"parameter": "test", "value": "4"},
        {"parameter": "test", "value": "5"},
    ]

    # Given the data is added to a csv file
    given_shark_csv = fixtures.data_rows_as_csv(given_shark_data_rows)

    # Given the csv is added to a zip file generated on POSIX system
    given_windows_zip_file = fixtures.given_posix_shark_zip(given_shark_csv)

    # Given a DwcaDataSharkStandard object
    given_filters = dwca_filters.DwcaFilters([])
    given_translate = dwca_translate.DwcaTranslate([])
    shark_data = DwcaDataSharkStandard(None, given_filters, given_translate)

    # When adding the shark data zip file to the DwcaDataSharkStandard object
    shark_data.add_shark_dataset(given_windows_zip_file)

    # Then the given data is added
    shark_data_rows = shark_data.get_data_rows()
    assert shark_data_rows == given_shark_data_rows
