"""demo.py - full runnable showcase of ui_theme.

Run:
    python demo.py
    python demo.py MyApp
    UITHEME_THEME=matrix python demo.py
    UITHEME_ICONS=ascii python demo.py
"""
import sys
import ui_theme


def main():
    app = sys.argv[1] if len(sys.argv) > 1 else "MyProject"

    ui_theme.print_banner(app, "A generic description of my project features")

    ui_theme.print_rule("diagnostics")
    ui_theme.print_check("pass", "Python version", "3.12.3 (Python39\\python.exe)")
    ui_theme.print_check("pass", "Working dir", "E:\\Projects\\MyProject")
    ui_theme.print_check("pass", "Package: PySide6", "import PySide6 OK")
    ui_theme.print_check("pass", "Package: requests", "import requests OK")
    ui_theme.print_check("warn", "Backend port 8080", "already listening")
    ui_theme.print_check("fail", "Package: some_dependency", "pip install some_dependency")
    ui_theme.print_rule()

    ui_theme.print_server_online(
        "http://127.0.0.1:8080",
        "E:\\Projects\\MyProject\\backend\\viewer",
    )

    print()
    ui_theme.panel(
        [
            ui_theme.icon("rocket") + "  " + ui_theme.colorize("Tip", "#ffffff", bold=True)
            + "  use a Nerd Font + Windows Terminal for the full look",
        ],
        title="NOTE",
        border_hex="#00e5ff",
    )


if __name__ == "__main__":
    main()
