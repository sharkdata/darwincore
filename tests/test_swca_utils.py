import pytest

from dwca_generator.dwca_utils import config_with_suffix


@pytest.mark.parametrize(
    "given_config, given_suffix, expecrted_config",
    (
        ({}, None, {}),
        ({}, "Something", {}),
        ([], None, []),
        ([], "Something", []),
        ({"key": "value"}, None, {"key": "value"}),
        ({"key_SUFFIX": 42}, "_SUFFIX", {"key": 42}),
        (
            {"key": "original_value", "key_SUFFIX": "suffix_value"},
            "_SUFFIX",
            {"key": "suffix_value"},
        ),
        (
            {"nested": {"dict": {"key_SUFFIX": "deep_value"}}},
            "_SUFFIX",
            {"nested": {"dict": {"key": "deep_value"}}},
        ),
        (["a", "b", "c", "d"], "_SUFFIX", ["a", "b", "c", "d"]),
        ([[{"key_SUFFIX": "suffix_value"}]], "_SUFFIX", [[{"key": "suffix_value"}]]),
        (
            [
                {
                    "complex": [
                        {
                            "config": [
                                {
                                    "with": {
                                        "many_levels": [
                                            {"key": "value_A"},
                                            {
                                                "key1": "value_A",
                                                "key2": "initial_value_A",
                                                "key2_SUFFIX": "override_value_B",
                                            },
                                        ],
                                        "many_levels_SUFFIX": [
                                            {"key": "value_B"},
                                            {
                                                "key1": "value_B",
                                                "key2": "initial_value_B",
                                                "key2_SUFFIX": "override_value_B",
                                            },
                                        ],
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            "_SUFFIX",
            [
                {
                    "complex": [
                        {
                            "config": [
                                {
                                    "with": {
                                        "many_levels": [
                                            {"key": "value_B"},
                                            {
                                                "key1": "value_B",
                                                "key2": "override_value_B",
                                            },
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
        ),
    ),
)
def test_config_with_suffix(given_config, given_suffix, expecrted_config):
    filterd_config = config_with_suffix(given_config, given_suffix)

    assert filterd_config == expecrted_config
