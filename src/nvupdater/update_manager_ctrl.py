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

    def build_module_list(self):
        appValues = [
            'novelibre',
            f'{self._ctrl.plugins.majorVersion}.{self._ctrl.plugins.minorVersion}.{self._ctrl.plugins.patchlevel}',
            f"{_('wait')} ...",
            ]
        self.moduleCollection.insert('', 'end', 'novelibre', values=appValues)

        for moduleName in self._ctrl.plugins:
            nodeTags = []
            try:
                installedVersion = self._ctrl.plugins[moduleName].VERSION
            except AttributeError:
                installedVersion = _('unknown')
            latestVersion = f"{_('wait')} ..."
            columns = [moduleName, installedVersion, latestVersion]
            if self._ctrl.plugins[moduleName].isRejected:
                nodeTags.append('rejected')
                # Mark rejected modules, represented by a dummy.
            elif not self._ctrl.plugins[moduleName].isActive:
                nodeTags.append('inactive')
                # Mark loaded yet incompatible modules.
            self.moduleCollection.insert('', 'end', moduleName, values=columns, tags=tuple(nodeTags))
        self.update()
        # enforcing the display before returning to the time-consuming internet lookup

    def refresh_display(self, moduleName, values):
        self.moduleCollection.item(moduleName, values=values)
        self.update()

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

