import csv
import io
import zipfile

from darwincore.dwca_generator import dwca_filters, dwca_translate
from darwincore.dwca_generator.dwca_data_shark import DwcaDataSharkStandard


def data_rows_as_csv(data):
    string_buffer = io.StringIO()
    field_names = {key for row in data for key in row.keys()}
    writer = csv.DictWriter(string_buffer, field_names, delimiter="\t")
    writer.writeheader()
    writer.writerows(data)
    return string_buffer.getvalue()


def given_windows_shark_zip(shark_csv):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        file=zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zip_archive:
        zip_archive.writestr(r"processed_data\delivery_note.txt", "status: prod")
        zip_archive.writestr(r"shark_data.txt", shark_csv)
    zip_buffer.seek(0)
    return zip_buffer


def given_posix_shark_zip(shark_csv):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        file=zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zip_archive:
        zip_archive.writestr(r"processed_data/delivery_note.txt", "status: prod")
        zip_archive.writestr(r"shark_data.txt", shark_csv)
    zip_buffer.seek(0)
    return zip_buffer


def given_dwca_shark_standard_data(value_list: list[dict]):
    shark_data_rows = []
    for n, values in enumerate(value_list, start=1):
        base_values = {
            "parameter": "test",
            "value": str(n),
            "dataset_event_key": f"event_{n}",
            "dataset_name": "dataset_1",
        }
        shark_data_rows.append(base_values | values)

    shark_csv = data_rows_as_csv(shark_data_rows)
    windows_zip_file = given_posix_shark_zip(shark_csv)

    # Given a DwcaDataSharkStandard object
    shark_data = DwcaDataSharkStandard(
        None, dwca_filters.DwcaFilters([]), dwca_translate.DwcaTranslate([])
    )
    shark_data.add_shark_dataset(windows_zip_file)

    return shark_data
