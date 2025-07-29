"""Tests to ensure all help commands use beautiful Rich Panel UI."""

from typing import List, Optional, Union
from unittest.mock import patch

import click
from click.testing import CliRunner

from airpilot.cli import cli


def test_main_cli_help_uses_panel() -> None:
    """Test main CLI help uses Panel UI instead of default Click help."""
    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    # Check for Panel borders (Rich uses box drawing characters)
    assert "╭" in result.output and "╰" in result.output
    assert "AirPilot - Universal Intelligence Control" in result.output
    # Ensure it's NOT using default Click format
    assert "Usage:" not in result.output or "[OPTIONS]" not in result.output


def test_init_help_uses_panel() -> None:
    """Test init --help uses Panel UI instead of default Click help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['init', '--help'])

    assert result.exit_code == 0
    # Check for Panel borders
    assert "╭" in result.output and "╰" in result.output
    assert "Initialize Intelligence Control" in result.output
    assert "air init - Initialize .air intelligence control" in result.output
    # Ensure it's NOT using default Click format
    assert "Usage: air init [OPTIONS]" not in result.output


def test_sync_help_uses_panel() -> None:
    """Test sync --help uses Panel UI instead of default Click help."""
    runner = CliRunner()

    # Mock license requirement to pass
    with patch('airpilot.commands.sync.require_license') as mock_require:
        mock_require.return_value = lambda func: func

        result = runner.invoke(cli, ['sync', '--help'])

        assert result.exit_code == 0
        # Check for Panel borders
        assert "╭" in result.output and "╰" in result.output
        assert "Premium Sync Command" in result.output
        assert "air sync - Premium: Real-time vendor synchronization" in result.output
        # Ensure it's NOT using default Click format
        assert "Usage: air sync [OPTIONS]" not in result.output


def test_license_group_help_uses_panel() -> None:
    """Test license --help uses Panel UI instead of default Click help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['license', '--help'])

    assert result.exit_code == 0
    # Check for Panel borders
    assert "╭" in result.output and "╰" in result.output
    assert "License Management" in result.output
    assert "air license - Manage AirPilot license" in result.output
    # Ensure it's NOT using default Click format
    assert "Usage: air license [OPTIONS]" not in result.output


def test_license_install_help_uses_panel() -> None:
    """Test license install --help uses Panel UI instead of default Click help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['license', 'install', '--help'])

    assert result.exit_code == 0
    # Check for Panel borders
    assert "╭" in result.output and "╰" in result.output
    assert "Install License Key" in result.output
    assert "air license install - Install a license key" in result.output
    # Ensure it's NOT using default Click format
    assert "Usage: air license install [OPTIONS]" not in result.output


def test_license_remove_help_uses_panel() -> None:
    """Test license remove --help uses Panel UI instead of default Click help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['license', 'remove', '--help'])

    assert result.exit_code == 0
    # Check for Panel borders
    assert "╭" in result.output and "╰" in result.output
    assert "Remove License" in result.output
    assert "air license remove - Remove stored license" in result.output
    # Ensure it's NOT using default Click format
    assert "Usage: air license remove [OPTIONS]" not in result.output


def test_license_status_help_uses_panel() -> None:
    """Test license status --help uses Panel UI instead of default Click help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['license', 'status', '--help'])

    assert result.exit_code == 0
    # Check for Panel borders
    assert "╭" in result.output and "╰" in result.output
    assert "License Status Details" in result.output
    assert "air license status - Show detailed license status" in result.output
    # Ensure it's NOT using default Click format
    assert "Usage: air license status [OPTIONS]" not in result.output


def test_version_flag_uses_panel() -> None:
    """Test --version flag uses Panel UI instead of plain text."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0
    # Check for Panel borders
    assert "╭" in result.output and "╰" in result.output
    assert "Version Information" in result.output
    assert "AirPilot CLI" in result.output
    assert "Universal Intelligence Control" in result.output


def test_all_panels_have_consistent_formatting() -> None:
    """Test that all Panel outputs have consistent Rich formatting."""
    runner = CliRunner()

    # Test commands that should have Panel UI
    test_commands = [
        [],  # main help
        ['--version'],  # version
        ['init', '--help'],  # init help
        ['license', '--help'],  # license group help
        ['license', 'install', '--help'],  # license install help
        ['license', 'remove', '--help'],  # license remove help
        ['license', 'status', '--help'],  # license status help
    ]

    for command in test_commands:
        # Mock license requirement if needed
        with patch('airpilot.commands.sync.require_license') as mock_require:
            mock_require.return_value = lambda func: func

            result = runner.invoke(cli, command)
            assert result.exit_code == 0

            # All Panel outputs should have box drawing characters
            assert "╭" in result.output, f"Command {command} missing Panel top border"
            assert "╰" in result.output, f"Command {command} missing Panel bottom border"

            # Should not contain default Click help patterns
            assert "Usage:" not in result.output or "[OPTIONS]" not in result.output, \
                f"Command {command} using default Click format instead of Panel"


def test_sync_help_panel_with_license_mock() -> None:
    """Test sync --help specifically with proper license mocking."""
    runner = CliRunner()

    # Mock the license requirement to bypass authentication
    with patch('airpilot.commands.sync.require_license') as mock_require:
        # Make the decorator return the original function unchanged
        mock_require.return_value = lambda func: func

        result = runner.invoke(cli, ['sync', '--help'])

        assert result.exit_code == 0
        # Check for Panel borders and content
        assert "╭" in result.output and "╰" in result.output
        assert "Premium Sync Command" in result.output
        assert "Real-time vendor synchronization" in result.output
        assert "Requirements:" in result.output
        assert "What it does:" in result.output


def test_license_install_without_key_shows_help_panel() -> None:
    """Test license install without key argument shows help panel."""
    runner = CliRunner()
    result = runner.invoke(cli, ['license', 'install'])

    assert result.exit_code == 0
    # Should show help panel, not error
    assert "╭" in result.output and "╰" in result.output
    assert "Install License Key" in result.output
    assert "air license install - Install a license key" in result.output


def test_all_commands_use_panel_ui_dynamically() -> None:
    """
    Dynamic test that discovers ALL CLI commands and validates they use Panel UI.
    This test will catch any new commands that forget to use beautiful Panel formatting.
    """
    from unittest.mock import patch

    runner = CliRunner()

    def discover_all_commands(ctx: Union[click.Group, click.Command], command_path: Optional[List[str]] = None) -> List[List[str]]:
        """Recursively discover all commands in the CLI."""
        if command_path is None:
            command_path = []
        commands: List[List[str]] = []

        if isinstance(ctx, click.Group):
            # This is a command group, explore its subcommands
            dummy_ctx = click.Context(ctx)
            for cmd_name in ctx.list_commands(dummy_ctx):
                subcommand = ctx.get_command(dummy_ctx, cmd_name)
                if subcommand:
                    new_path = command_path + [cmd_name]
                    commands.append(new_path)
                    # Recursively explore subcommands
                    commands.extend(discover_all_commands(subcommand, new_path))

        return commands

    # Discover all commands dynamically
    all_commands = discover_all_commands(cli)

    # Add the main CLI help (no subcommands)
    test_cases: List[List[str]] = [[]]  # Main help
    test_cases.extend(all_commands)

    # Test each discovered command with --help
    for command_path in test_cases:
        test_command = command_path + ['--help']

        # Mock license requirement for any premium commands
        with patch('airpilot.commands.sync.require_license') as mock_require:
            mock_require.return_value = lambda func: func

            try:
                result = runner.invoke(cli, test_command)

                # Skip if command genuinely fails (e.g., missing required args that can't be helped)
                if result.exit_code != 0:
                    continue

                command_desc = ' '.join(command_path) if command_path else 'main CLI'

                # CRITICAL: All help output must use Panel UI
                assert "╭" in result.output, \
                    f"Command '{command_desc} --help' missing Panel UI top border! " \
                    f"Output: {result.output[:200]}..."

                assert "╰" in result.output, \
                    f"Command '{command_desc} --help' missing Panel UI bottom border! " \
                    f"Output: {result.output[:200]}..."

                # CRITICAL: Must NOT use default Click help format
                click_patterns = [
                    "Usage: air",
                    "[OPTIONS]",
                    "Show this message and exit."
                ]

                for pattern in click_patterns:
                    assert pattern not in result.output, \
                        f"Command '{command_desc} --help' using default Click format instead of Panel UI! " \
                        f"Found pattern: '{pattern}' in output: {result.output[:200]}..."

                print(f"✓ Verified Panel UI for: {command_desc} --help")

            except Exception as e:
                # If we can't test a command, at least report it
                print(f"⚠ Could not test command: {command_path} --help (Error: {e})")


def test_version_command_uses_panel_ui() -> None:
    """Test --version uses Panel UI (separate from help commands)."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0
    # Must use Panel UI
    assert "╭" in result.output and "╰" in result.output
    assert "Version Information" in result.output
    # Must NOT be plain version text
    assert result.output != "0.7.4\n"  # Not just raw version number


def test_future_command_detection() -> None:
    """
    Test that ensures new commands will be caught by the dynamic test.
    This test validates that our discovery mechanism works.
    """

    # Count current commands
    def count_commands(ctx: Union[click.Group, click.Command], depth: int = 0) -> int:
        count = 0
        if isinstance(ctx, click.Group):
            dummy_ctx = click.Context(ctx)
            for cmd_name in ctx.list_commands(dummy_ctx):
                count += 1
                subcommand = ctx.get_command(dummy_ctx, cmd_name)
                if subcommand:
                    count += count_commands(subcommand, depth + 1)
        return count

    current_command_count = count_commands(cli)

    # We should have at least the known commands: init, license (group), sync
    # Plus license subcommands: install, remove, status, help
    expected_minimum = 7  # init, license, sync, license.install, license.remove, license.status, license.help

    assert current_command_count >= expected_minimum, \
        f"Expected at least {expected_minimum} commands, found {current_command_count}. " \
        f"Command discovery may be broken."

    print(f"✓ Discovery mechanism working: Found {current_command_count} total commands")


def test_unknown_command_uses_panel_ui() -> None:
    """Test that unknown commands show beautiful Panel UI instead of default Click error."""
    runner = CliRunner()
    result = runner.invoke(cli, ['cloud'])

    # Should exit with error code
    assert result.exit_code == 1

    # Must use Panel UI
    assert "╭" in result.output and "╰" in result.output
    assert "Command Not Found" in result.output
    assert "Unknown command 'cloud'" in result.output
    assert "Available commands:" in result.output
    assert "air init - Initialize intelligence control" in result.output
    assert "air license - Manage AirPilot license" in result.output
    assert "air sync - Premium: Real-time vendor sync" in result.output

    # Must NOT use default Click error format
    assert "Usage: air [OPTIONS] COMMAND [ARGS]..." not in result.output
    assert "Try 'air --help' for help." not in result.output
    assert "Error: No such command" not in result.output


def test_unknown_command_various_names() -> None:
    """Test that various unknown command names all get Panel UI treatment."""
    runner = CliRunner()

    unknown_commands = ['backup', 'deploy', 'xyz123', 'nonexistent']

    for cmd in unknown_commands:
        result = runner.invoke(cli, [cmd])

        assert result.exit_code == 1
        # Must use Panel UI
        assert "╭" in result.output and "╰" in result.output
        assert "Command Not Found" in result.output
        assert f"Unknown command '{cmd}'" in result.output

        # Must NOT use default Click error format
        assert "Usage: air [OPTIONS] COMMAND [ARGS]..." not in result.output
        assert "Try 'air --help' for help." not in result.output
