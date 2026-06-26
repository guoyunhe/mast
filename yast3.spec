#
# spec file for package yast3
#
# Copyright (c) 2026 SUSE LLC and contributors
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           yast3
Version:        0.0.1
Release:        0
Summary:        GUI & TUI system settings tool


License:        GPL-3.0-or-later
URL:            https://github.com/yast3/yast3
Source0:        https://github.com/yast3/yast3/archive/refs/tags/%{version}.tar.gz

BuildRequires:  make
BuildRequires:  python-rpm-macros
BuildRequires:  python3
BuildRequires:  python3-Babel
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Recommends:     %{name}-qt6

BuildArch:      noarch

%python_subpackages

%description
YaST3 is a modern desktop settings shell built with Python 3,
providing Qt6, GTK4 GUI and Textual TUI interfaces for system
configuration management.

This is a metapackage that recommends the Qt6 GUI interface.
Install %{name}-qt6, %{name}-gtk4, or %{name}-tui for specific interfaces.

%package core
Summary:        YaST3 core functionality shared by all interfaces
Requires:       %python_module python-crontab

%description core
Core modules and utilities shared by YaST3 Qt6, GTK4 and TUI interfaces.

%package gtk4
Summary:        YaST3 GTK4 GUI interface
Requires:       %{name}-core = %{version}-%{release}
Requires:       %python_module python-gobject

%description gtk4
GTK4 GUI interface for YaST3 desktop settings shell.

%package qt6
Summary:        YaST3 Qt6 GUI interface
Requires:       %{name}-core = %{version}-%{release}
Requires:       %python_module python-PySide6

%description qt6
Qt6 GUI interface for YaST3 desktop settings shell.

%package tui
Summary:        YaST3 Textual TUI interface
Requires:       %{name}-core = %{version}-%{release}
Requires:       %python_module python-textual

%description tui
Textual TUI interface for YaST3 desktop settings shell.

%prep
%autosetup

%build
%make_build mo
%pyproject_wheel

%install
%pyproject_install
%python_clone %{_bindir}/yast3-gtk4
%python_clone %{_bindir}/yast3-qt6
%python_clone %{_bindir}/yast3-tui

%files core
%license LICENSE
%doc README.md
%{python_sitelib}/yast3/core/
%{python_sitelib}/yast3-%{version}*.dist-info/
%{_datadir}/icons/hicolor/64x64/apps/%{name}.svg
%{_datadir}/locale/

%files gtk4
%{python_sitelib}/yast3/gtk4/
%{_bindir}/yast3-gtk4
%{_bindir}/yast3-gtk4-%{python_version}
%{_datadir}/applications/%{name}-gtk4.desktop

%files qt6
%{python_sitelib}/yast3/qt6/
%{_bindir}/yast3-qt6
%{_bindir}/yast3-qt6-%{python_version}
%{_datadir}/applications/%{name}-qt6.desktop

%files tui
%{python_sitelib}/yast3/tui/
%{_bindir}/yast3-tui
%{_bindir}/yast3-tui-%{python_version}

%changelog
