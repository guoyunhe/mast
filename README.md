# YaST3

Save YaST ♥️ with Python 3 & Qt6 Widgets.

## Overview

YaST3 starts as a desktop settings shell inspired by the system settings app on Windows.
The main window shows settings modules in a grid, each with a themed GNU/Linux icon and label.
Selecting a module opens a separate placeholder window for future implementation.

## Requirements

- Python 3.12+
- Qt6 bindings for Python via PySide6

## Run

```bash
python3 -m pip install -r requirements.txt
python3 -m yast3
```

## Install on Linux

Install the app for the current user and register the desktop launcher:

```bash
./scripts/install.sh
```

Install it system-wide instead:

```bash
sudo ./scripts/install.sh --system
```

After installation, you can start the app from the application menu or by running:

```bash
yast3
```

## Package

Build standard Python distribution artifacts for Linux packaging workflows:

```bash
./scripts/package.sh
```

This creates source and wheel packages in `dist/`.
