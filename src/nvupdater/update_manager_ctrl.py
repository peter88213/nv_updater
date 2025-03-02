"""Provide a mixin class for an update dialog controller.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import configparser
import os
from urllib.request import urlopen
import webbrowser

from nvlib.controller.services.nv_help import NvHelp
from nvlib.controller.sub_controller import SubController
from nvlib.nv_globals import HOME_URL
from nvupdater.nvupdater_locale import _


class UpdateManagerCtrl(SubController):

    def initialize_controller(self, model, view, controller):
        super().initialize_controller(model, view, controller)
        self.downloadUrls = {}
        self.download = False

    def build_module_list(self):
        repoName = 'novelibre'
        self.downloadUrls[repoName] = None
        appValues = [
            repoName,
            f'{self._ctrl.plugins.majorVersion}.{self._ctrl.plugins.minorVersion}.{self._ctrl.plugins.patchlevel}',
            f"{_('wait')} ...",
            ]
        self.repoList.insert('', 'end', 'novelibre', values=appValues)

        for repoName in self._ctrl.plugins:
            if self._ctrl.plugins[repoName].isRejected:
                continue

            self.downloadUrls[repoName] = None
            nodeTags = []
            try:
                installedVersion = self._ctrl.plugins[repoName].VERSION
            except AttributeError:
                installedVersion = _('unknown')
            latestVersion = f"{_('wait')} ..."
            columns = [repoName, installedVersion, latestVersion]
            if not self._ctrl.plugins[repoName].isActive:
                nodeTags.append('inactive')
                # Mark loaded yet incompatible downloadUrls.
            self.repoList.insert('', 'end', repoName, values=columns, tags=tuple(nodeTags))
        self.update()
        # enforcing the display before returning to the time-consuming internet lookup

    def check_repos(self):
        self.output(f"{_('Looking for updates')}...")
        found = False

        # Check novelibre.
        repoName = 'novelibre'
        try:
            majorVersion, minorVersion, patchlevel, downloadUrl = self._get_version_info(repoName)
        except:
            latestStr = _('unknown')
        else:
            latest = (majorVersion, minorVersion, patchlevel)
            latestStr = f'{majorVersion}.{minorVersion}.{patchlevel}'
            current = (self._ctrl.plugins.majorVersion, self._ctrl.plugins.minorVersion, self._ctrl.plugins.patchlevel)
            currentStr = f'{self._ctrl.plugins.majorVersion}.{self._ctrl.plugins.minorVersion}.{self._ctrl.plugins.patchlevel}'
            if self._update_available(latest, current):
                self.downloadUrls[repoName] = downloadUrl
                tags = ('outdated')
                found = True
            else:
                tags = ()
        self._refresh_display(repoName, [repoName, currentStr, latestStr], tags=tags)

        # Check installed plugins.
        for repoName in self._ctrl.plugins:
            if self._ctrl.plugins[repoName].isRejected:
                continue

            try:
                majorVersion, minorVersion, patchlevel = self._ctrl.plugins[repoName].VERSION.split('.')
                current = (int(majorVersion), int(minorVersion), int(patchlevel))
                currentStr = f'{majorVersion}.{minorVersion}.{patchlevel}'
            except:
                current = (0, 0, 0)
                currentStr = _('unknown')
            try:
                majorVersion, minorVersion, patchlevel, downloadUrl = self._get_version_info(repoName)
                latest = (majorVersion, minorVersion, patchlevel)
                latestStr = f'{majorVersion}.{minorVersion}.{patchlevel}'
            except:
                latestStr = _('unknown')
                tags = ()
            else:
                if self._update_available(latest, current):
                    self.downloadUrls[repoName] = downloadUrl
                    tags = ('outdated')
                    found = True
                else:
                    tags = ()
            self._refresh_display(repoName, [repoName, currentStr, latestStr], tags=tags)
        if not found:
            self.output(f"{_('No updates available')}.")
        else:
            self.output(f"{_('Finished')}.")
        if False:
            self._ui.show_info(f"{_('Please restart novelibre after installing updates')}.", title=_('Check for updates'))

    def on_select_module(self, event):
        repoName = self.repoList.selection()[0]
        homeButtonState = 'disabled'
        updateButtonState = 'disabled'
        if repoName:
            if  repoName == 'novelibre':
                homeButtonState = 'normal'
                updateButtonState = 'normal'
            else:
                try:
                    if self._ctrl.plugins[repoName].URL:
                        homeButtonState = 'normal'
                except:
                    pass
                try:
                    if self.downloadUrls[repoName] is not None:
                        updateButtonState = 'normal'
                except:
                    pass
        self.homeButton.configure(state=homeButtonState)
        self.updateButton.configure(state=updateButtonState)

    def on_quit(self):
        if self.download:
            self._ui.show_info(f"{_('Please restart novelibre after installing updates')}.", title=_('Check for updates'))
        self.destroy()

    def open_help(self, event=None):
        NvHelp.open_help_page(f"tools_menu.html#{_('Check for updates').lower()}")

    def open_homepage(self, event=None):
        repoName = self.repoList.selection()[0]
        if repoName:
            if repoName == 'novelibre':
                webbrowser.open(HOME_URL)
                return

            try:
                url = self._ctrl.plugins[repoName].URL
                if url:
                    webbrowser.open(url)
            except:
                pass

    def update_module(self, event=None):
        repoName = self.repoList.selection()[0]
        if self.downloadUrls[repoName] is None:
            return

        webbrowser.open(self.downloadUrls[repoName])
        self.repoList.item(repoName, tags=('updated'))
        self.download = True

    def _get_version_info(self, repoName):
        if repoName == 'novelibre':
            repoUrl = 'https://github.com/peter88213/novelibre'
        else:
            repoUrl = self._ctrl.plugins[repoName].URL
        versionUrl = f'{repoUrl}/raw/main/VERSION'
        data = urlopen(versionUrl)
        versionInfo = data.read().decode('utf-8')
        config = configparser.ConfigParser()
        config.read_string(versionInfo)
        downloadUrl = config['LATEST']['download_link']
        version = config['LATEST']['version']
        majorVersion, minorVersion, patchlevel = version.split('.')
        return int(majorVersion), int(minorVersion), int(patchlevel), downloadUrl

    def _refresh_display(self, repoName, values, tags=()):
        self.repoList.item(repoName, values=values, tags=tags)
        self.update()

    def _update_available(self, latest, current):
        """Return True, if the latest version number is greater than the current one."""
        if latest[0] > current[0]:
            return True

        if latest[0] == current[0]:
            if latest[1] > current[1]:
                return True

            if latest[1] == current[1]:
                if latest[2] > current[2]:
                    return True

        return False

