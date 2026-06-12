PYTHON ?= python3
PIP := $(PYTHON) -m pip
USER_APPLICATIONS_DIR = $${XDG_DATA_HOME:-$$HOME/.local/share}/applications
SYSTEM_APPLICATIONS_DIR = /usr/local/share/applications

.PHONY: install install-system dist clean

define update_desktop_database
	@if command -v update-desktop-database >/dev/null 2>&1 && [ -d "$(1)" ]; then \
		update-desktop-database "$(1)" >/dev/null 2>&1 || \
			echo "Warning: failed to update desktop database in $(1)." >&2; \
	fi
endef

install:
	$(PIP) install --upgrade --user .
	$(call update_desktop_database,$(USER_APPLICATIONS_DIR))

install-system:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: install-system must be run as root (for example: sudo make install-system)." >&2; \
		exit 1; \
	fi
	$(PIP) install --upgrade .
	$(call update_desktop_database,$(SYSTEM_APPLICATIONS_DIR))

dist: clean
	$(PIP) install --upgrade build
	$(PYTHON) -m build --outdir dist .

clean:
	rm -rf build dist *.egg-info
