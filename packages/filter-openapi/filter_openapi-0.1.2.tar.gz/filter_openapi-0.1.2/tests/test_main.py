import sys
from unittest.mock import MagicMock, patch

import pytest
import yaml

from filter_openapi.main import main


@pytest.fixture
def mock_args(tmp_path):
    """Fixture to mock command line arguments."""
    input_yaml = tmp_path / "input.yaml"
    config_json = tmp_path / "config.json"
    output_yaml = tmp_path / "output.yaml"

    # Create dummy files
    with open(input_yaml, "w") as f:
        yaml.dump({"info": {"title": "Test"}}, f)
    with open(config_json, "w") as f:
        f.write('{"allowedTags": [], "pathFilters": {}}')

    return [
        "filter_openapi/main.py",
        str(input_yaml),
        "--config",
        str(config_json),
        "--output",
        str(output_yaml),
        "--verbose",
    ]


@patch("filter_openapi.main.AppConfig.from_file")
@patch("filter_openapi.main.remove_properties")
@patch("filter_openapi.main.filter_paths_by_tags")
@patch("filter_openapi.main.filter_tags_list")
@patch("filter_openapi.main.filter_endpoint")
@patch("filter_openapi.main.get_referenced_schemas")
@patch("filter_openapi.main.filter_schemas")
def test_main_flow(
    mock_filter_schemas,
    mock_get_referenced_schemas,
    mock_filter_endpoint,
    mock_filter_tags_list,
    mock_filter_paths_by_tags,
    mock_remove_properties,
    mock_from_file,
    mock_args,
    tmp_path,
    capsys,
):
    """Test the main execution flow, mocking all action functions."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.properties_to_remove = ["x-prop"]
    mock_config.allowed_tags = {"tag1"}
    mock_config.path_filters.items.return_value = [("/path", MagicMock())]
    mock_config.options.remove_unreferenced_schemas = True
    mock_from_file.return_value = mock_config

    # Mock return values of actions to be passthrough
    mock_remove_properties.side_effect = lambda d, p: d
    mock_filter_paths_by_tags.side_effect = lambda d, t: d
    mock_filter_tags_list.side_effect = lambda d, t: d
    mock_filter_endpoint.side_effect = lambda d, p, m: d
    mock_get_referenced_schemas.return_value = {"Schema1"}
    mock_filter_schemas.side_effect = lambda d, s: d

    with patch.object(sys, "argv", mock_args):
        main()

    # Assertions
    mock_from_file.assert_called_once_with(mock_args[3])
    mock_remove_properties.assert_called_once()
    mock_filter_paths_by_tags.assert_called_once()
    mock_filter_tags_list.assert_called_once()
    mock_filter_endpoint.assert_called_once()
    mock_get_referenced_schemas.assert_called_once()
    mock_filter_schemas.assert_called_once()

    output_file = tmp_path / "output.yaml"
    assert output_file.exists()


def test_main_integration(tmp_path, capsys):
    """An integration-style test for the main script."""
    config_path = "tests/data/config.json"
    input_path = "tests/data/openapi.yaml"
    output_path = tmp_path / "output.yaml"

    cli_args = [
        "script_name",
        input_path,
        "-c",
        config_path,
        "-o",
        str(output_path),
    ]

    with patch.object(sys, "argv", cli_args):
        main()

    with open(output_path, "r") as f:
        result_data = yaml.safe_load(f)

    # Check filtering results
    assert "UnusedTag" not in [tag["name"] for tag in result_data["tags"]]
    assert "/unused" not in result_data["paths"]
    assert "post" not in result_data["paths"]["/test"]  # Removed by path filter
    assert "x-test" not in result_data["paths"]["/test"]["get"]
    assert "UnusedSchema" not in result_data["components"]["schemas"]
    assert "TestSchema" in result_data["components"]["schemas"]


def test_main_stdout(capsys):
    """Test writing to stdout."""
    config_path = "tests/data/config.json"
    input_path = "tests/data/openapi.yaml"
    cli_args = ["script_name", input_path, "-c", config_path]

    with patch.object(sys, "argv", cli_args):
        main()

    captured = capsys.readouterr()
    assert "Simple API" in captured.out
    result_data = yaml.safe_load(captured.out)
    assert "UnusedTag" not in [tag["name"] for tag in result_data["tags"]]


@patch(
    "filter_openapi.main.AppConfig.from_file", side_effect=Exception("File read error")
)
def test_main_config_load_error(mock_from_file, mock_args, caplog):
    with patch.object(sys, "argv", mock_args):
        with pytest.raises(SystemExit) as e:
            main()
    assert e.value.code == 1
    assert "Error loading configuration" in caplog.text


@patch("builtins.open", side_effect=IOError("Cannot read"))
def test_main_input_file_read_error(mock_open, mock_args, caplog):
    # we need AppConfig to load successfully
    with patch("filter_openapi.main.AppConfig.from_file"):
        with patch.object(sys, "argv", mock_args):
            with pytest.raises(SystemExit) as e:
                main()
    assert e.value.code == 1
    assert "Error reading input file" in caplog.text
