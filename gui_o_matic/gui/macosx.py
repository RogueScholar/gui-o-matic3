# SPDX-FileCopyrightText: © 2016-2018 Mailpile ehf. <team@mailpile.is>
# SPDX-FileCopyrightText: © 2016-2018 Bjarni Rúnar Einarsson <bre@godthaab.is>
# SPDX-FileCopyrightText: 🄯 2020 Peter J. Mello <admin@petermello.net>
#
# SPDX-License-Identifier: LGPL-3.0-only

import objc
import traceback

from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

from gui_o_matic.gui.base import BaseGUI


class MacOSXThing(NSObject):
    indicator = None

    def applicationDidFinishLaunching_(self, notification):
        self.indicator._menu_setup()
        self.indicator._ind_setup()
        self.indicator.ready = True

    def activate_(self, notification):
        for i, v in self.indicator.items.items():
            if notification == v:
                if i in self.indicator.callbacks:
                    self.indicator.callbacks[i]()
                return
        print(('activated an unknown item: %s' % notification))


class MacOSXGUI(BaseGUI):

    ICON_THEME = 'osx'  # OS X has its own theme because it is too
                        # dumb to auto-resize menu bar icons.

    def _menu_setup(self):
        # Build a very simple menu
        self.menu = NSMenu.alloc().init()
        self.menu.setAutoenablesItems_(objc.NO)
        self.items = {}
        self.callbacks = {}
        self._create_menu_from_config()

    def _add_menu_item(self, id='item', label='Menu item',
                             sensitive=False,
                             op=None, args=None,
                             **ignored_kwarg):
        # For now, bind everything to the notify method
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            label, 'activate:', '')
        menuitem.setEnabled_(sensitive)
        self.menu.addItem_(menuitem)
        self.items[id] = menuitem
        if op:
            def activate(o, a):
                return lambda: self._do(o, a)
            self.callbacks[id] = activate(op, args or [])

    def _ind_setup(self):
        # Create the statusbar item
        self.ind = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength)

        # Load all images, set initial
        self.images = {}
        images = self.config.get('indicator', {}).get('images', {})
        for s, p in images.items():
            p = self._theme_image(p)
            self.images[s] = NSImage.alloc().initByReferencingFile_(p)
        if self.images:
            self.ind.setImage_(self.images['normal'])

        self.ind.setHighlightMode_(1)
        #self.ind.setToolTip_('Sync Trigger')
        self.ind.setMenu_(self.menu)
        self.set_status()

    def set_status(self, status='startup', badge=None):
        # FIXME: Can we support badges?
        self.ind.setImage_(self.images.get(status, self.images['normal']))

    def set_item(self, id=None, label=None, sensitive=None):
        if label is not None and id and id in self.items:
            self.items[id].setTitle_(label)
        if sensitive is not None and id and id in self.items:
            self.items[id].setEnabled_(sensitive)

    def notify_user(self,
            message=None, popup=False, alert=False, actions=None):
        pass  # FIXME

    def run(self):
        app = NSApplication.sharedApplication()
        osxthing = MacOSXThing.alloc().init()
        osxthing.indicator = self
        app.setDelegate_(osxthing)
        try:
            AppHelper.runEventLoop()
        except:
            traceback.print_exc()


GUI = MacOSXGUI
