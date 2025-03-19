import pytest
import yaml

from dwca_generator.dwca_transform_data import DwcaTransformData


@pytest.mark.parametrize(
    "given_row, expected_row, given_transform_config",
    (
        # Empty data and config is ok
        ({}, {}, []),
        # Data is left unchanged if config is empty
        ({"parameter": "value"}, {"parameter": "value"}, []),
        # Data is left unchanged if parameter doesn't match config
        (
            {"parameter": "untouched value"},
            {"parameter": "untouched value"},
            [
                {
                    "if": {"parameter": "specific value"},
                    "then": {"parameter": "new value"},
                }
            ],
        ),
        # Change parameter when value matches config
        (
            {"parameter": "old value"},
            {"parameter": "new value"},
            [{"if": {"parameter": "old value"}, "then": {"parameter": "new value"}}],
        ),
        # Change other parameter than the one that matches config
        (
            {"parameter1": "value to examine", "parameter2": "value to change"},
            {"parameter1": "value to examine", "parameter2": "changed value"},
            [
                {
                    "if": {"parameter1": "value to examine"},
                    "then": {"parameter2": "changed value"},
                }
            ],
        ),
        # Add parameter
        (
            {"parameter1": "value to examine"},
            {"parameter1": "value to examine", "parameter2": "value for new parameter"},
            [
                {
                    "if": {"parameter1": "value to examine"},
                    "then": {"parameter2": "value for new parameter"},
                }
            ],
        ),
        # Change and add parameters
        (
            {"parameter1": "value to examine"},
            {"parameter1": "changed", "parameter2": "changed", "parameter3": "added"},
            [
                {
                    "if": {"parameter1": "value to examine"},
                    "then": {
                        "parameter1": "changed",
                        "parameter2": "changed",
                        "parameter3": "added",
                    },
                }
            ],
        ),
        # Change parameter value when value matches one of two config values
        (
            {"parameter": "value b"},
            {"parameter": "had value b"},
            [
                {"if": {"parameter": "value a"}, "then": {"parameter": "had value a"}},
                {"if": {"parameter": "value b"}, "then": {"parameter": "had value b"}},
            ],
        ),
        # Change parameter value when two parameters matches
        (
            {"parameter a": "value a", "parameter b": "value b"},
            {"parameter a": "a matched", "parameter b": "and b matched"},
            [
                {
                    "if": {
                        "parameter a": "value a",
                        "parameter b": "value b",
                    },
                    "then": {
                        "parameter a": "a matched",
                        "parameter b": "and b matched",
                    },
                }
            ],
        ),
        # Match empty value
        (
            {"parameter": ""},
            {"parameter": "not empty anymore"},
            [
                {
                    "if": {"parameter": ""},
                    "then": {"parameter": "not empty anymore"},
                }
            ],
        ),
        # Match missing parameter to empty value
        (
            {},
            {"parameter": "parameter added"},
            [
                {
                    "if": {"parameter": ""},
                    "then": {"parameter": "parameter added"},
                }
            ],
        ),
    ),
)
def test_transform_row(given_row, expected_row, given_transform_config, tmp_path):
    # Given file path to the config
    given_config_path = tmp_path / "config.yaml"
    given_config_path.write_text(yaml.dump(given_transform_config))

    # Given a transform object
    given_transform_data = DwcaTransformData([given_config_path])

    # When transforming rows
    given_transform_data.transform_row(given_row)

    # Then the row looks like expected
    assert given_row == expected_row


def test_later_config_overwrites_prior(tmp_path):
    # Given a row with three parameters
    given_row = {
        "parameter1": "initial value",
        "parameter2": "initial value",
        "parameter3": "initial value",
    }

    # Given path to a config that will change all three parameters
    config_1 = [
        {
            "if": {"parameter1": "initial value"},
            "then": {"parameter1": "Changed by config_1"},
        },
        {
            "if": {"parameter2": "initial value"},
            "then": {"parameter2": "Changed by config_1"},
        },
        {
            "if": {"parameter3": "initial value"},
            "then": {"parameter3": "Changed by config_1"},
        },
    ]
    given_config_path_1 = tmp_path / "config1.yaml"
    given_config_path_1.write_text(yaml.dump(config_1))

    # Given path to a config that will change two of the parameters
    config_2 = [
        {
            "if": {"parameter2": "initial value"},
            "then": {"parameter2": "Changed by config_2"},
        },
        {
            "if": {"parameter3": "initial value"},
            "then": {"parameter3": "Changed by config_2"},
        },
    ]
    given_config_path_2 = tmp_path / "config2.yaml"
    given_config_path_2.write_text(yaml.dump(config_2))

    # Given path a config that will change on of the parameters
    config_3 = [
        {
            "if": {"parameter3": "initial value"},
            "then": {"parameter3": "Changed by config_3"},
        }
    ]
    given_config_path_3 = tmp_path / "config3.yaml"
    given_config_path_3.write_text(yaml.dump(config_3))

    # Given a transform object
    given_transform_data = DwcaTransformData(
        [given_config_path_1, given_config_path_2, given_config_path_3]
    )

    # When transforming rows
    given_transform_data.transform_row(given_row)

    # Then the row looks like expected
    expected_row = {
        "parameter1": "Changed by config_1",
        "parameter2": "Changed by config_2",
        "parameter3": "Changed by config_3",
    }
    assert given_row == expected_row
