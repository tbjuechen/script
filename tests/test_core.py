from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import cv2
import numpy as np

from main import build_parser
from gui_app import validate_settings
from runner.base import FindListRunner
from runner.player import CVPlayer


class ExampleRunner(FindListRunner):
    name = "example"
    targets = ("first.jpg", "second.jpg")


class RunnerTests(unittest.TestCase):
    def test_one_screenshot_and_first_match_only(self) -> None:
        runner = ExampleRunner(connection_class=Mock, player=Mock())
        runner.connection = Mock()
        runner.connection.screen_shot.return_value = "screen.png"
        runner.wanted_path = Path("wanted")
        runner.player.locate.side_effect = [None, (100, 200)]

        with patch.object(runner, "randomize_position", return_value=(101, 202)):
            runner.work()

        runner.connection.screen_shot.assert_called_once_with()
        self.assertEqual(runner.player.locate.call_count, 2)
        runner.connection.touch.assert_called_once_with(101, 202)

    def test_stops_searching_after_first_match(self) -> None:
        runner = ExampleRunner(connection_class=Mock, player=Mock())
        runner.connection = Mock()
        runner.connection.screen_shot.return_value = "screen.png"
        runner.wanted_path = Path("wanted")
        runner.player.locate.return_value = (10, 20)
        runner.connection.touch.return_value = True

        with patch.object(runner, "randomize_position", return_value=(10, 20)):
            runner.work()

        runner.player.locate.assert_called_once()


class PlayerTests(unittest.TestCase):
    def test_locates_template_center(self) -> None:
        rng = np.random.default_rng(42)
        target = rng.integers(0, 256, size=(20, 30, 3), dtype=np.uint8)
        screenshot = np.zeros((120, 180, 3), dtype=np.uint8)
        screenshot[40:60, 70:100] = target

        with TemporaryDirectory() as directory:
            target_path = Path(directory) / "target.png"
            screenshot_path = Path(directory) / "screen.png"
            cv2.imwrite(str(target_path), target)
            cv2.imwrite(str(screenshot_path), screenshot)
            location = CVPlayer(acc=0.9, reference_size=(180, 120)).locate(
                str(target_path), str(screenshot_path)
            )

        self.assertEqual(location, (85, 50))

    def test_missing_image_has_clear_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            CVPlayer().load("does-not-exist.png")

    def test_scales_reference_template_for_device_resolution(self) -> None:
        rng = np.random.default_rng(7)
        target = rng.integers(0, 256, size=(24, 36, 3), dtype=np.uint8)
        scaled = cv2.resize(target, None, fx=5 / 6, fy=5 / 6, interpolation=cv2.INTER_AREA)
        screenshot = np.zeros((900, 1600, 3), dtype=np.uint8)
        height, width = scaled.shape[:2]
        screenshot[100 : 100 + height, 200 : 200 + width] = scaled

        with TemporaryDirectory() as directory:
            target_path = Path(directory) / "target.png"
            screenshot_path = Path(directory) / "screen.png"
            cv2.imwrite(str(target_path), target)
            cv2.imwrite(str(screenshot_path), screenshot)
            location = CVPlayer(acc=0.9).locate(str(target_path), str(screenshot_path))

        self.assertEqual(location, (200 + width // 2, 100 + height // 2))

    def test_locates_template_in_normalized_region(self) -> None:
        rng = np.random.default_rng(11)
        target = rng.integers(0, 256, size=(20, 30, 3), dtype=np.uint8)
        screenshot = np.zeros((100, 200, 3), dtype=np.uint8)
        screenshot[70:90, 150:180] = target

        with TemporaryDirectory() as directory:
            target_path = Path(directory) / "target.png"
            screenshot_path = Path(directory) / "screen.png"
            cv2.imwrite(str(target_path), target)
            cv2.imwrite(str(screenshot_path), screenshot)
            player = CVPlayer(acc=0.9, reference_size=(200, 100))
            location = player.locate(
                str(target_path),
                str(screenshot_path),
                region=(0.5, 0.5, 1.0, 1.0),
            )

        self.assertEqual(location, (165, 80))


class CliTests(unittest.TestCase):
    def test_defaults(self) -> None:
        args = build_parser().parse_args([])
        self.assertEqual(args.task, "active")
        self.assertEqual(args.port, 16384)


class GuiSettingsTests(unittest.TestCase):
    def test_valid_settings(self) -> None:
        settings = validate_settings("active", "127.0.0.1", "16384", "0.8", "1")
        self.assertEqual(settings.port, 16384)
        self.assertEqual(settings.threshold, 0.8)

    def test_rejects_invalid_port(self) -> None:
        with self.assertRaisesRegex(ValueError, "端口"):
            validate_settings("active", "127.0.0.1", "70000", "0.8", "1")

    def test_rejects_invalid_threshold(self) -> None:
        with self.assertRaisesRegex(ValueError, "阈值"):
            validate_settings("active", "127.0.0.1", "16384", "1.5", "1")


if __name__ == "__main__":
    unittest.main()
