# -*- coding: utf-8 -*-

"""Tests for command line interface"""

from click.testing import CliRunner

from ipgetter2.__main__ import main


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()

    result = runner.invoke(main, ["show-servers"])
    assert result.exit_code == 0

    help_result = runner.invoke(main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
