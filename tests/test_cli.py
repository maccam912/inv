"""Tests for the CLI."""

from unittest.mock import patch

from click.testing import CliRunner

from inv.cli import inv


def test_run_tui() -> None:
    """Test that the TUI runs when no subcommand is given."""
    runner = CliRunner()
    with patch("inv.cli.InventoryApp") as mock_app:
        result = runner.invoke(inv)
        assert result.exit_code == 0
        mock_app.assert_called_once()
        mock_app.return_value.run.assert_called_once()
