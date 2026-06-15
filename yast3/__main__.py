from .app import MainWindow
from .i18n import init_i18n


def main() -> int:
    # Initialize internationalization
    init_i18n()

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("YaST3")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
