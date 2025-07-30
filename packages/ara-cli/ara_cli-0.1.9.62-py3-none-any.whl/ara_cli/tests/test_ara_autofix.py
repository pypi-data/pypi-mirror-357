import pytest
from unittest.mock import patch, mock_open, MagicMock
from ara_cli.artefact_autofix import (
    read_report_file,
    parse_report,
    apply_autofix,
    read_artefact,
    determine_artefact_type_and_class,
    run_agent,
    write_corrected_artefact
)
from ara_cli.ara_command_action import autofix_action


def test_read_report_file():
    mock_content = "# Artefact Check Report\n\n## classifier\n- `file_path`: reason\n"
    with patch("builtins.open", mock_open(read_data=mock_content)) as m:
        content = read_report_file()
        assert content == mock_content
        m.assert_called_once_with(
            "incompatible_artefacts_report.md", "r", encoding="utf-8")


def test_parse_report():
    content = "# Artefact Check Report\n\n## classifier\n- `file_path`: reason\n"
    expected_issues = {"classifier": [("file_path", "reason")]}
    issues = parse_report(content)
    assert issues == expected_issues


@patch("ara_cli.artefact_autofix.run_agent")
@patch("ara_cli.artefact_autofix.write_corrected_artefact")
def test_apply_autofix(mock_write_corrected_artefact, mock_run_agent):
    mock_run_agent.return_value.serialize.return_value = "corrected content"
    with patch("ara_cli.artefact_autofix.read_artefact", return_value="artefact text"):
        with patch("ara_cli.artefact_autofix.determine_artefact_type_and_class", return_value=("ArtefactType", MagicMock())):
            apply_autofix("file_path", "classifier", "reason")
            mock_run_agent.assert_called_once()
            mock_write_corrected_artefact.assert_called_once_with(
                "file_path", "corrected content")


@patch("ara_cli.artefact_autofix.apply_autofix")
@patch("ara_cli.artefact_autofix.parse_report")
@patch("ara_cli.artefact_autofix.read_report_file")
def test_autofix_action(mock_read_report_file, mock_parse_report, mock_apply_autofix, capsys):
    mock_read_report_file.return_value = "# Artefact Check Report\n\n## classifier\n- `file_path`: reason\n"
    mock_parse_report.return_value = {"classifier": [("file_path", "reason")]}

    args = MagicMock()
    autofix_action(args)

    captured = capsys.readouterr()
    assert "Attempting to fix file_path for reason: reason" in captured.out
    mock_apply_autofix.assert_called_once_with(
        "file_path", "classifier", "reason")


def test_read_artefact():
    mock_content = "artefact content"
    with patch("builtins.open", mock_open(read_data=mock_content)) as m:
        content = read_artefact("file_path")
        assert content == mock_content
        m.assert_called_once_with("file_path", "r")


def test_read_report_file_not_found(capsys):
    with patch("builtins.open", side_effect=OSError("File not found")):
        content = read_report_file()
        captured = capsys.readouterr()
        assert content is None
        assert "Artefact scan results file not found" in captured.out


def test_parse_report_no_issues():
    content = "# Artefact Check Report\n\nNo problems found.\n"
    issues = parse_report(content)
    assert issues == {}


def test_parse_report_invalid_format():
    content = "Invalid Format"
    issues = parse_report(content)
    assert issues == {}


def test_determine_artefact_type_and_class_invalid():
    artefact_type, artefact_class = determine_artefact_type_and_class(
        "invalid_classifier")
    assert artefact_type is None
    assert artefact_class is None


def test_write_corrected_artefact():
    corrected_content = "corrected content"
    with patch("builtins.open", mock_open()) as m:
        write_corrected_artefact("file_path", corrected_content)
        m.assert_called_once_with("file_path", "w")
        handle = m()
        handle.write.assert_called_once_with(corrected_content)


@patch("ara_cli.artefact_autofix.read_artefact", return_value=None)
def test_apply_autofix_file_not_found(mock_read_artefact):
    apply_autofix("file_path", "classifier", "reason")
    mock_read_artefact.assert_called_once_with("file_path")


@patch("pydantic_ai.Agent")
def test_run_agent_exception_handling(mock_agent):
    mock_agent.return_value.run_sync.side_effect = Exception("Agent error")
    with pytest.raises(Exception, match="Agent error"):
        run_agent("prompt", MagicMock())
