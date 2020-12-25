# The GUI-o-Matic Protocol

[SPDX-FileCopyrightText: © 2016-2018 Bjarni Rúnar Einarsson <bre@godthaab.is>]::
[SPDX-FileCopyrightText: 🄯 2020 Peter J. Mello <admin@petermello.net>]::

[SPDX-License-Identifier: LGPL-3.0-only]::

[SPDX-FileType: DOCUMENTATION]::

GUI-o-Matic implements a relatively simple protocol for communicating between the
main application and the GUI tool.

There are three main stages to the protocol:
 1. Configuration
 1. Handing Over Control
 1. Ongoing GUI Updates

The protocol is a one-way stream of text (ASCII/JSON), and is line-based and
case-sensitive at all stages.

The initial stream should be read from standard input, a file, or by capturing
the output of another tool.

Conceptually, stages 2 and 3 are separate because they accomplish very different
things, but in practice they overlap; the source of the protocol stream may
change at any time after stage 1.

**Note:** There's no strong reason stages 1, 2 and 3 use different syntax; mostly I
think it looks nicer this way and makes it easy to read and write raw command
transcripts. Similar things look similar, different things look different!

---

## Configuration

The first stage uses the simplest protocol, but communicates the richest set of
data: at this stage the GUI-o-Matic tool simply reads a JSON-formatted
dictionary. The dictionary defines the main characteristics of our user
interface.

GUI-o-Matic should read until it sees a line starting with the words `OK GO` or
`OK LISTEN`, at which point it should attempt to parse the JSON structure and
then proceed to stage two.

When the configuration dictionary is parsed, it should be treated in the
forgiving spirit of JSON in general: most missing fields should be replaced with
reasonable defaults and unrecognized fields should be ignored.

The following is an example of a complete configuration dictionary, along with
descriptions of how it is interpreted.

**Note:** Lines beginning with a `#` are comments explaining what each section
means. They should be omitted from any actual implementation (comments are,
sadly, not allowed in JSON).

```json
{
    # Basics
    "app_name": "Your App Name",
    "app_icon": "/reference/or/absolute/path/to/icon.png",

    # i18n hint to GUI: ltr, rtl, ...?
    "text_direction": "ltr",

    # These are for testing only; implementations may ignore them.
    "_require_gui": ["unity", "macosx", "gtk"],
    "_prefer_gui": ["unity", "macosx", "gtk"],

    # HTTP Cookie { key: value, ... } pairs, by domain.
    # These get sent as cookies along with get_url/post_url HTTP requests.
    "http_cookies": {
        "localhost:33411": {
            "session": "abacabadonk"
        }
    },
...
```

### Sections

#### images

The `images` section defines a dictionary of named icons/images. The names can be
used directly by the `set_status` method, or anywhere an icon path can be
provided by using the syntax `image:NAME` instead. Note that all paths should be
absolute, as we don't want to make assumptions about the working directory of the
GUI app itself.

The only required entry is `normal`.

There is also preliminary support for light/dark/... themes, by embedding the
magic marker `%(theme)s` in the name. The idea is that if the backend somehow
detects that a dark theme is more appropriate, it will replace `%(theme)s` with
the word `dark`. The current draft OS X backend requests an `osx` theme because
at some point Mac OS X needed slightly different icons from the others.

```json
...
    "images": {
        "normal": "/absolute/path/to/%(theme)s/normal.svg",
        "flipper": "/absolute/path/to/unthemed/flipper.png",
        "flopper": "/absolute/path/to/flop-%(theme)s.png"
        "background": "/absolute/path/to/a/nice/background.jpg"
    },
...
```

#### font_styles

In `font_styles`, we define font styles used in different parts of the app.

```json
...
    "font_styles": {
        # Style used by status display titles in the main window
        "title": {
            "family": "normal",
            "points": 18,
            "bold": True
        },

        # Style used by status display details in the main window
        "details": {
            "points": 10,
            "italic": True
        },

        # Title and detail styles can be scoped to only apply to
        # a single status display, by prepending the ID.
        "id_title": { ... },
        "id_details": { ... },

        # The main-window may have a standalone notification element,
        # for messages that don't go anywhere else.
        "notification": { ... },

        # Labels on buttons in the main window
        "buttons": { ... }

        # The progress reporting label on the splash screen
        "splash": { ... }
    },
...
```

#### main_window

The `main_window` section defines the main app window. The main app window has
the following elements:
 - Status displays (an icon and some text: title + details)
 - Actions (buttons or menu items)
 - A notification display element (text label)
 - A background image

How these are actually laid out is up to the GUI backend. Desktop platforms
should largely behave the same way, but we could envision a mobile (Android?)
implementation that for example ignored the width/height parameters and moved
some of the actions to a hamburger "overflow" menu.

```json
...
    "main_window": {
        # Is the main window displayed immediately on startup? This
        # will be set to False when we are using a splash-screen.
        "show": False,

        # If True, closing the main window exits the app. If False,
        # it just hides the main window, and we rely on the indicator
        # or other mechanisms to bring it back as necessary.
        "close_quits": False,

        # Recommended height/width. May be ignored on some platforms.
        "width": 550,
        "height": 330,

        # Background image.  May be ignored on some platforms.
        "background": "image:background",

        # Default notification label text
        "initial_notification": "",
...
```

##### status_displays

The `status_displays` in the main window are used to communicate both visual and
textual clues about different things. Each consists of an icon, a main label and
a hint. The values provided are defaults, all are likely to change later on. The
GUI backend has a fair bit of freedom in how it renders these, but order should
be preserved and labels should be made more prominent than hints.

```json
...
        "status_displays": [
            {
                "id": "internal-identifying-name",
                "icon": "image:something",
                "title": "Hello world!",
                "details": "Greetings and salutations to all!"
            },{
                "id": "id2",
                "icon": "/absolute/path/to/some/icon.png",
                "title": "Launching Frobnicator",
                "details": "The beginning and end of all things"
            }
        ],
...
```

##### action_items

The main window `action_items` are generally implemented as buttons in desktop
environments. Actions are to be allocated space in the GUI, in the order they are
specified - if we run out of space, latter actions may be moved to some sort of
overflow or "hamburger".

##### position

The `position` field gives a clue about ordering on the display itself, but does
not influence priority. As an example, in a typical left-to-right row of buttons,
the first action to request `last` should be rendered furthest to the right, and
the first action to request `first` furthest to the left. Later buttons get
rendered progressively closer to the middle, until we run out of space. Adjust
accordingly if the buttons are rendered top-to-bottom (portrait mode on mobile?).

##### op/arg

The `op` and `args` fields together define what happens if the user clicks the
button. The operation can be any of the Stage 3 operations defined below, in
which case "args" should be a dictionary of arguments, or it can be one of:
 - `show_url`
 - `get_url`
 - `post_url`
 - `shell`

[See below](#Operations-and-arguments) for further clarifications on these
operations and their arguments.

```json
...
        "action_items": [
            {
                "id": "open",
                "type": "button",  # button is the default
                "position": "first",
                "label": "Open",
                "op": "show_url",
                "args": "http://www.google.com/"
            },{
                "id": "evil666",
                "position": "last",
                "label": "Harakiri",
                "op": "shell",
                "args": ["rm -rf /ha/ha/just/kidding",
                         "echo 'That was close'"]
            }
        ]
    # The "main_window" example ends here
    },
...
```

#### indicator

The final section of the configuration is the `indicator`, which ideally is
implemented as a mutable icon and action menu, displayed in the appropriate place
on the Desktop (top-bar on MacOS, system tray on Windows/X.org, etc.). If no such
placement is possible, the indicator may instead show up as an icon in the main
window itself.

The menu items should be rendered in the order specified.

Items in the menu with `sensitive` set to false should be displayed, but not
clickable by the user (marked inactive, shown "greyed out"). Note that the label
text and sensitivity of an item may later be modified by Stage 3 commands.

Menu items may also be separators, which in most environments draws a horizontal
divider. Environments not supporting that may use a blank menu item or omit, as
deemed appropriate.

Within these menus, the `id`, `op` and `args` fields have the same meanings and
function as they do in the main window actions. Configuration writes should take
care to avoid collissions when chosing item IDs.

An menu item with the ID `notification` is special and should receive text
updates from the `notify_user` method.

```json
    "indicator": {
        "initial_status": "startup",  # Should match an icon
        "menu_items": [
            {
                "id": "notification",
                "label": "Starting up!",
                "sensitive": False
            },{
                "separator": True
            },{
                "id": "xkcd",
                "label": "XKCD is great",
                "op": "show_url",
                "args": "https://xkcd.com/"
            }
        ]
    }
}
```

There are more examples in the [scripts](scripts/) folder!

### Operations and arguments

Both main-window actions and indicator menu items specify `op` and `args` to
define what happens when the user clicks on them.

These actions are either GUI-o-Matic Stage 3 operations (in which case `args`
should be a dictionary of arguments), web actions, or a shell command.

In all cases, execution (or network) errors result in a notification being
displayed to the user.

**FIXME:** It should be possible to customize the error messages...

#### Web actions

##### show_url

The most basic web action is `show_url`. This action takes a single argument,
which is the URL to display. The JSON structure may be any of: a string, a list
with a single element (the string) or a dictionary with a `_url`.

No cookies or POST data can be specified with this method. When activated, this
operation should request the given URL be opened in the user's default browser.

**FIXME:** In a new tab? Or reuse a tab we already opened? Make this configurable
by adding args to a dictionary?

##### get_url/post_url

These actions will in the background send an HTTP GET or HTTP POST request to the
URL specified in the argument.

For GET requests, the JSON structure may be any of: a string, a list with a
single element (the string) or a dictionary with a `_url`.

For POST requests, `args` should be a dictionary, where the URL is specified in
an element named `_url`. All other elements in the dictionary will be encoded as
payload/data and sent along with the POST request.

If the response data has the MIME type `application/json`, it parses as a JSON
dictionary, and the JSON has a top-level element named `message`, that result
text will be displayed to the user as a notification.

#### Shell actions

##### shell

Shell actions expect `args` to be a list of strings. Each string is passed to the
operating system shell as a command to execute (so a single click can result in
multiple shell actions). If any fails (returns a non-zero exit code), the
subsequent commands will not run.

The output from the shell commands is discarded.

---

## Handing over control

The GUI-o-Matic protocol has five options for handing over control (changing the
stream of commands) after the configuration has been processed:
 1. **OK GO** - No more input
 1. **OK LISTEN** - No change, keep reading the same source
 1. **OK LISTEN TO: cmd** - Launch cmd and read its standard output
 1. **OK LISTEN TCP: cmd** - Launch cmd and read from a socket
 1. **OK LISTEN HTTP: url** - Fetch and URL and read from a socket

Options 1 and 2 are trivial and will not be discussed further.

In all cases except "OK GO", if GUI-o-Matic reaches EOF (end-of-file) on the
update stream, that should result in shutdown of GUI-o-Matic itself.

### OK LISTEN TO

**Example:** `OK LISTEN TO: cat /tmp/magic.txt`

If the handover command begins with `OK LISTEN TO: `, the rest of the line should
be treated verbatim as standard input to be passed to the operating system shell.

The standard output of the spawned command shall be read and parsed for stage 2
or stage 3 updates.

**Errors:** The GUI-o-Matic should monitor whether the spawned command
crashes/exits with a non-zero exit code and communicate that to the user.

### OK LISTEN TCP

**Example:** `OK LISTEN TCP: mailpile --www= --gui=%PORT% --wait`

In this case, the GUI-o-Matic must open a new listening TCP socket (preferably on
a random OS-assigned localhost-only port).

The rest of the "OK LISTEN TCP: ..." line should have all occurrances of `%PORT%`
replaced with the port number, and the resulting string passed to the operating
system shell to execute.

The spawned command is expected to connect to `localhost:PORT` and send further
stage 2 or stage 3 updates over that channel.

**Errors:** In addition to checking the exit code of the spawned process as
described above, GUI-o-Matic should also monitor whether the spawned command
crashes/exits without ever establishing a connection and treat that and excessive
timeouts as error conditions.

### OK LISTEN HTTP

**Example:** `OK LISTEN HTTP: http://localhost:33411/gui/%PORT%/`

This command behaves identically to `OK LISTEN TCP`, except instead of spawning a
new process the app connects to an HTTP server on localhost and passes
information about the control port in the URL.

Again, HTTP errors (non-200 result codes) and socket errors should be
communicated to the user and treated as fatal. The body of the HTTP reply is
ignored.

**TODO:** _An alternate HTTP method which repeatedly long-polls an URL for
commands would allow GUI-o-Matic to easily play nice over the web! We don't need
this today, but it might be nice for someone else? Food for thought..._ **DANGER!
This could become a huge security hole!**

---

## Ongoing GUI Updates

The third stage (which is processed in parallel to stage 2), is commands which
send updates to the GUI itself.

These updates all use the same syntax:

```json
lowercase_command_with_underscores {"arguments": "as JSON"}
```

Each command will fit on a single line (no newlines are allowed in the JSON
section) and be terminated by a CRLF or LF sequence. If there are no arguments,
an empty JSON dictionary `{}` is expected.

A description of the existing commands follows; see also
[gui_o_matic/gui/base.py](gui_o_matic/gui/base.py) for the Python 3 definitions.

### show_splash_screen

Arguments:
 - background: (string) absolute path to a background image file
 - message: (string) initial status message
 - message_x: (float [0-1]) positioning hint for message in window
 - message_y: (float [0-1]) positioning hint for message in window
 - progress_bar: (bool) display a progress bar?

This displays a splash-screen, to keep the user happy while something slow
happens.

### update_splash_screen

Arguments:
 - progress: (optional float) progress bar size in the range 0 - 1.0
 - message: (optional string) updated status message

### hide_splash_screen

Arguments: none

Hides the splash-screen.

### show_main_window

Arguments: none

Display the main application window.

### hide_main_window

Arguments: none

Hide the main application window.

### set_status

Arguments:
 - status: (optional string) "startup", "normal", "working",...
 - badge: (optional string) A very short snippet of text

If `status` is provided, set the overall "status" of the application. This is
generally displayed by changing an indicator icon somewhere within the app. All
statuses should have an icon defined in the `images: { ... }` section of the
configuration.

The `badge` is a small amount of text to overlay over the app's icon (which may
or may not be the same icon as the status icon, where this goes, if anywhere is
platform dependent), representing unread message counts or other similar data.
Callers should assume only some platforms implement this and should assume the
amount of text is limited to 1-3 characters at most.

GUI implementors must assume that the `status` and `badge` may be set
independently of each other, as many callers will use different logic to track
and report each one.

### set_status_display

Arguments:
 - id: (string) The ID of the status display section
 - title: (optional string) Updated text for the title label
 - details: (optional string) Updated text for the details label
 - icon: (optional string) FS path or reference to an entry in `images`
 - color: (optional #rgb/#rrggbb string) Color for label text

This will update some or all of the elements of one of the status display
sections in the main window.

### set_item

Arguments:
 - id: (string) The item ID as defined in the configuration
 - label: (optional string) A new label!
 - sensitive: (optional bool) Make item senstive (default) or insensitive

This can be used to change the labels displayed in the indicator menu (the
`indicator: menu: [ ... ]` section of the configuration).

This can also be used to change the sensitivity of one of the entries in the
indicator menu (the `indicator: menu: [ ... ]` section of the config).
Insensitive items are greyed out but should still be displayed, as apps may
choose to use the to communicate low-priority information to the user.

### set_next_error_message

Arguments:
 - message: (optional string) What to say next time something fails

This can be used to override GUI-o-Matic internal error messages (including those
generated by stage 2 commands above). Calling this with no arguments reverts back
to the default behaviour.

This is important to allow apps to give friendlier (albeit less precise) messages
to users, including respecting localization settings in the controlling app.

### notify_user

Arguments:
 - message: (string) Tell the user something
 - popup: (optional bool) Prefer an OSD/growl/popup style notification
 - alert: (optional bool) Try harder to get the user's attention
 - actions: (optional list of dicts) Actions relating to the notification

This method should always try and display a message to the user, no matter which
windows are visible:
 - If popus are requested, be intrusive!
 - If the splash screen is visible, display there
 - If the main window is visible, display there
 - ...?

If a notifications has `"alert": true`, that is a signal to the GUI that it
should flash a light, bounce an icon, vibrate or otherwise try to draw the user's
attention to the app.

If present, `actions` should be a list of dictionaries containing the same
`label`, `op`, `args` and `position` arguments as are used in the main window
`action_items` section.

Since support for notification actions varies a great deal from platform to
platform (and toolkit to toolkit), the caller must assume some or all items in
`actions` will be silently ignored.  The list should be sorted by priority (most
important first) and the caller should assume list processing may be truncated at
any point or individual items skipped due to platform limitations.

The `actions` list is likely to be ignored if `popup` is not set to True.

GUI implementors should carefully consider the user experience of notification
actions on their platform. It may be better to not implement `actions` at all
than to provide confusing or destructive implementations. As an example, if an
URL is to be opened in the browser, but the implementation cannot
raise/focus/display the browser on click, it's probably best not to offer browser
actions at all (confusion). Similarly, implementations that clobber pre-existing
tabs in the user's browser should also be avoided (destructive).

The presence (or absence) of an `actions` list should not alter the priority or
placement of displayed notifications.

### show_url

Arguments:
 - url: (url) The URL to open

Open the named URL in the user's preferred browser.

**FIXME:** _For access control reasons, this method should support POST, and/or
allow the app to configure cookies. However it's unclear whether the methods
available to us for launching the browser actually support that accross
platforms. Needs further research._

### terminal

Arguments:
 - command: (string) The shell command to launch
 - title: (optional string) The preferred terminal window title
 - icon: (optional string) FS path or reference to an entry in `images`

Spawn a command in a visible terminal, so the user can interact with it.

### set_http_cookie

Arguments:
 - domain: (string) The domain of the cookie being updated
 - key: (string) A the cookie key
 - value: (optional string) A new value for the cookie
 - remove: (optional bool) If true, delete the cookie (ignore value)

Modify or remove one of the HTTP cookies.

### quit

Arguments: none

Shut down GUI-o-Matic.

---

*FIN*
