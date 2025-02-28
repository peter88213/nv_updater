"""Provide a mixin class for an update dialog controller.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import webbrowser

from nvlib.controller.services.nv_help import NvHelp
from nvlib.controller.sub_controller import SubController
from nvupdater.nvupdater_locale import _


class UpdateManagerCtrl(SubController):

    def update_module(self, event=None):
        moduleName = self.moduleCollection.selection()[0]
        if moduleName:
            # if self._ctrl.plugins.delete_file(moduleName):
            if True:
                self.updateButton.configure(state='disabled')
                if self._ctrl.plugins[moduleName].isActive:
                    self._ui.show_info(F"{_('The update takes effect on next start')}.", title=f'{moduleName} {_("updated")}')
                else:
                    self.moduleCollection.delete(moduleName)

    def on_select_module(self, event):
        moduleName = self.moduleCollection.selection()[0]
        homeButtonState = 'disabled'
        updateButtonState = 'disabled'
        if moduleName:
            try:
                if self._ctrl.plugins[moduleName].URL:
                    homeButtonState = 'normal'
            except:
                pass
            try:
                if self._ctrl.plugins[moduleName].filePath:
                    updateButtonState = 'normal'
            except:
                pass
        self.homeButton.configure(state=homeButtonState)
        self.updateButton.configure(state=updateButtonState)

    def open_help(self, event=None):
        NvHelp.open_help_page(f'tools_menu.html#{_("plugin-manager").lower()}')

    def open_homepage(self, event=None):
        moduleName = self.moduleCollection.selection()[0]
        if moduleName:
            try:
                url = self._ctrl.plugins[moduleName].URL
                if url:
                    webbrowser.open(url)
            except:
                pass

