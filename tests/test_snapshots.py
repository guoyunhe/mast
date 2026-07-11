"""Unit tests for snapper snapshot helpers."""

import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from yast3.core.snapshots import (
    build_snapshot_create_command,
    build_snapshot_delete_command,
    list_snapshots,
)


class TestSnapshots(unittest.TestCase):
    @patch("yast3.core.snapshots.snapshots.subprocess.run")
    def test_list_snapshots_sorted_desc(self, mock_run: MagicMock) -> None:
        payload = [
            {
                "number": 10,
                "type": "single",
                "date": "2026-07-10 10:00:00",
                "user": "root",
                "description": "Before update",
                "cleanup": "number",
            },
            {
                "number": 12,
                "type": "single",
                "date": "2026-07-11 09:00:00",
                "user": "root",
                "description": "After update",
                "cleanup": "number",
            },
        ]
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload))

        snapshots = list_snapshots()

        self.assertEqual([item.number for item in snapshots], [12, 10])
        self.assertEqual(snapshots[0].description, "After update")

    @patch("yast3.core.snapshots.snapshots.subprocess.run")
    def test_list_snapshots_supports_dict_payload(self, mock_run: MagicMock) -> None:
        payload = {
            "snapshots": [
                {
                    "id": "5",
                    "type": "single",
                    "timestamp": "2026-07-11 10:00:00",
                    "user": "root",
                    "description": "Test",
                    "cleanup": "timeline",
                }
            ]
        }
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload))

        snapshots = list_snapshots(config="home")

        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].number, 5)
        self.assertEqual(snapshots[0].date, "2026-07-11 10:00:00")
        mock_run.assert_called_once_with(
            ["snapper", "-c", "home", "--jsonout", "list"],
            capture_output=True,
            text=True,
            check=True,
        )

    def test_build_create_command(self) -> None:
        command = build_snapshot_create_command("Before migration")
        self.assertEqual(
            command,
            ["pkexec", "snapper", "-c", "root", "create", "--description", "Before migration"],
        )

    def test_build_delete_command(self) -> None:
        command = build_snapshot_delete_command(42)
        self.assertEqual(command, ["pkexec", "snapper", "-c", "root", "delete", "42"])

    def test_build_create_command_rejects_empty_description(self) -> None:
        with self.assertRaises(ValueError):
            build_snapshot_create_command("   ")

    def test_build_delete_command_rejects_non_positive(self) -> None:
        with self.assertRaises(ValueError):
            build_snapshot_delete_command(0)


if __name__ == "__main__":
    unittest.main()
