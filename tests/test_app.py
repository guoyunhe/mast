import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QToolButton

from yast3.qt6.main_window import MainWindow


class MainWindowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_window_has_button_for_each_module(self) -> None:
        window = MainWindow()

        buttons = window.findChildren(QToolButton)

        self.assertEqual(len(buttons), len(window.modules))
        window.close()


if __name__ == "__main__":
    unittest.main()
