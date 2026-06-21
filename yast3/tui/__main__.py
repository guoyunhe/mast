"""Entry point for the TUI application."""

from yast3.core.i18n import init_i18n
from yast3.tui.main_window import MainWindow


def main() -> int:
    # Initialize internationalization
    init_i18n()

    app = MainWindow()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())