# GUI-o-Matic!

[SPDX-FileCopyrightText: © 2016-2018 Mailpile ehf. <team@mailpile.is>]::
[SPDX-FileCopyrightText: © 2016-2018 Bjarni Rúnar Einarsson <bre@godthaab.is>]::

[SPDX-License-Identifier: LGPL-3.0-only]::

[SPDX-FileContributor: 🄯 2020 Peter J. Mello <admin@petermello.net>]::
[SPDX-FileType: DOCUMENTATION]::

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![REUSE status](https://api.reuse.software/badge/github.com/RogueScholar/gui-o-matic3)](https://api.reuse.software/info/github.com/RogueScholar/gui-o-matic3)

This is a tool for creating minimal graphical user interfaces; maybe just a
splash screen and an indicator icon with a drop-down menu.

The tool is inspired by `dialog` and other similar command-line utilities which
provide drop-in user interfaces for shell scripts.

GUI-o-Matic is also a drop-in UI, but it differs from these tools in that it is
meant to be used as long-running process, either communicating with a background
process (a worker) or providing access to URLs or shell commands.

Background worker processes can mutate GUI-o-Matic's state using a simple
JSON-based protocol, and the GUI can communicate back or perform actions based on
user input in numerous ways. Background workers that need richer user interfaces
than are provided by GUI-o-Matic itself are expected to expose web or terminal
interfaces which GUI-o-Matic can launch as necessary.

When used without a worker, GUI-o-Matic can provide easy point-and-click access
to shell commands or URLs (see [example scripts](scripts/)).

Initally written as part of [Mailpile](https://www.mailpile.is/), this app is
released separately so other projects can make use of it.

## Project Status and License

This project is **a work in progress**. Please feel free to help out!

The license is the GNU Lesser General Public License, version 3.0, which means it
can be used and distributed along with proprietary applications, but changes to
GUI-o-Matic itself must be shared with the community.

## Supported Platforms

GUI-o-Matic currently supports the following desktop environments:
 - MacOS X (partial)
 - Standard X.org server (partial via libappindicator3)

Ideally, future versions will add complete support for:
 - Microsoft Windows
 - GNOME (GTK+)
 - KDE Plasma 5 (Qt 5)

If you have experience developing user interface code on any of these platforms,
please consider helping out!

## User Interface

GUI-o-Matic currently allows creation of the following UI elements:
 - Splash screen with progress bar and status
 - Simple main window with graphics, buttons and status messages
 - Indicator with mutable icon and drop-down menu

When the user interacts with the GUI (clicks a button or a menu item), the
following actions can be triggered:
 - Open URLs in the user's default web browser
 - Launch apps in terminal windows
 - Make HTTP GET/POST requests in the background (REST API calls?)
 - Run shell commands in the background

Planned features:
 - Dock icon with mutable icon and custom menu
 - System notifications (growl-style)

The UI feature-set is deliberately meant to stay small, to increase the odds that
the full functionality can be made available on all platforms.

## Configuration and Communication

When used as a command-line tool, the `gui-o-matic` tool will read a
JSON-formatted configuration from standard-input, until it encounters the words
`OK GO` or `OK LISTEN` on a line by themselves.

In GO mode, the app will continue running until killed.

In LISTEN mode, the app will then continue reading standard input, expecting one
command per line. On reaching the EOF (end-of-file) the app will terminate. The
command format is very simple; a command-name followed by a space and a single
JSON structure for arguments. Examples:
 - `update_splash_screen {"progress": 0.2, "message": "Yaaay"}`
 - `set_item {"id": "frobnicator", "label": "FROB IT"}`
 - `notify_user {"message": "Hello World!"}`

Consult the file [PROTOCOL.md](PROTOCOL.md) for a full specification of the
program and a full list of available commands. The [scripts](scripts/) folder
contains working examples illustrating these concepts.

## Credits and license

Copyright 2016-2018, Mailpile ehf. and Bjarni Rúnar Einarsson.

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free Software
Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.
