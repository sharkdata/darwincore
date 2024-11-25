from unittest.mock import MagicMock

import dwca_generator
from tests import fixtures


def test_aphia_id_is_added_for_phytoplankton():
    # Given phytoplankton names from add_aphia_id_phytoplankton.txt
    phytoplankton_names = [
        {"scientificName": "Eupodiscales"},
        {"scientificName": "Ebria"},
        {"scientificName": "Cylindrotheca"},
        {"scientificName": "Cladopyxis"},
    ]

    # Given shark data using given names
    given_shark_data = fixtures.given_dwca_shark_standard_data(phytoplankton_names)

    # Given a DwcaFormatStandard object based on minimal settings
    mock_config = MagicMock()
    mock_config.field_mapping = {
        "dwcaOccurrenceContent": [
            {
                "eventType": "sample",
                "dwcTerms": {
                    "dynamicProperties": {
                        "dynamic": [
                            {
                                "dynamicKey": "SHARK_Phytoplankton",
                                "sourceKey": "dataset_name",
                            }
                        ]
                    },
                    "scientificName": {"sourceKey": "scientificName"},
                },
            }
        ],
    }
    mock_config.dwca_keys = {
        "eventTypeKeys": {
            "occurrence": [
                {
                    "eventType": "sample",
                    "keyName": "dataset_event_key",
                }
            ]
        }
    }

    dwca_format = dwca_generator.DwcaFormatStandard(
        given_shark_data, mock_config, MagicMock(), MagicMock()
    )

    # Given there is no dwca_occurence
    assert len(dwca_format.dwca_occurrence) == 0
    dwca_format.create_dwca_occurrence()

    # Then a dwa_occurence has been added for each event_id
    assert len(dwca_format.dwca_occurrence) == 4

    # And it has scientificNameId added
    assert "scientificNameID" in dwca_format.dwca_occurrence[0]
    assert "scientificNameID" in dwca_format.dwca_occurrence[1]
    assert "scientificNameID" in dwca_format.dwca_occurrence[2]
    assert "scientificNameID" in dwca_format.dwca_occurrence[3]
