"""An update checker plugin for novelibre.

Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

"""
import configparser
import gettext
import locale
import os
import sys
from tkinter import messagebox
from urllib.request import urlopen
import webbrowser

from nvlib.plugin.plugin_base import PluginBase

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('nv_updater', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):

        return message


class CancelCheck(Exception):
    """Exception used for cancelling the update check."""
    pass


class Plugin(PluginBase):
    """Plugin class for the novelibre update checker."""
    VERSION = '@release'
    API_VERSION = '5.0'
    DESCRIPTION = 'Update checker'
    URL = 'https://github.com/peter88213/nv_updater'
    _HELP_URL = f'{_("https://peter88213.github.io/nvhelp-en")}/nv_updater/'

    def install(self, model, view, controller):
        """Install the plugin and extend the novelibre user interface.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Optional arguments:
            prefs -- deprecated. Please use controller.get_preferences() instead.
        
        Extends the superclass method.
        """
        super().install(model, view, controller)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('Update checker Online help'), command=lambda: webbrowser.open(self._HELP_URL))

        # Add an entry to the Tools menu.
        self._ui.toolsMenu.add_command(label=_('Check for updates'), command=self._check_for_updates)

        self.download = False

    def _check_for_updates(self):
        """Check novelibre and all installed plugins for updates."""
        found = False
        self.download = False
        print('Check for updates')

        # Check novelibre.
        repoName = 'novelibre'
        print(repoName)
        try:
            majorVersion, minorVersion, patchlevel, downloadUrl = self._get_version_info(repoName)
        except:
            messagebox.showerror(_('Check for updates'), _('No online update information for novelibre found.'))
            return

        try:
            latest = (majorVersion, minorVersion, patchlevel)
            print(f'Latest  : {latest}')
            current = (self._ctrl.plugins.majorVersion, self._ctrl.plugins.minorVersion, self._ctrl.plugins.patchlevel)
            print(f'Current : {current}')
            if self._update_available(latest, current):
                self._download_update('novelibre', downloadUrl)
                found = True

            # Check installed plugins.
            for moduleName in self._ctrl.plugins:
                print(moduleName)
                try:
                    repoName = self._ctrl.plugins[moduleName].URL.rsplit('/', maxsplit=1)[1]
                    # Latest version
                    majorVersion, minorVersion, patchlevel, downloadUrl = self._get_version_info(repoName)
                    latest = (majorVersion, minorVersion, patchlevel)
                    print(f'Latest  : {latest}')

                    # Current version
                    majorVersion, minorVersion, patchlevel = self._ctrl.plugins[moduleName].VERSION.split('.')
                    current = (int(majorVersion), int(minorVersion), int(patchlevel))
                    print(f'Current : {current}')
                except:
                    continue
                else:
                    if self._update_available(latest, current):
                        self._download_update(moduleName, downloadUrl)
                        found = True
            if not found:
                messagebox.showinfo(_('Check for updates'), _('No updates available.'))
        except CancelCheck:
            # user pressed the "cancel" button
            pass
        finally:
            if self.download:
                messagebox.showinfo(_('Check for updates'), _('Please restart novelibre after installing updates.'))

    def _download_update(self, repo, downloadUrl):
        """Start the web browser with downloadUrl on demand.
        
        Positional arguments:
            repo: str -- Repository name of the app or plugin.
            downloadUrl: str -- Download URL of the latest release in the repository.
        
        Exceptions:
            raise CancelCheck, if the update check is to be cancelled.
        """
        text = f'{_("An update is available for")} {repo}.\n{_("Start your web browser for download?")}'
        answer = messagebox.askyesnocancel(_('Check for updates'), text)
        if answer:
            # user pressed the "Yes" button
            webbrowser.open(downloadUrl)
            self.download = True
        elif answer is None:
            # user pressed the "Cancel" button
            raise CancelCheck

    def _get_version_info(self, repoName):
        """Return version information and download URL stored in a repository's VERSION file.
        
        Positional arguments:
            repoName: str -- The repository's name.
        
        Return major version number, minor version number, patch level, and download URL.        
        """
        versionUrl = f'https://github.com/peter88213/{repoName}/raw/main/VERSION'
        data = urlopen(versionUrl)
        versionInfo = data.read().decode('utf-8')
        config = configparser.ConfigParser()
        config.read_string(versionInfo)
        downloadUrl = config['LATEST']['download_link']
        version = config['LATEST']['version']
        majorVersion, minorVersion, patchlevel = version.split('.')
        return int(majorVersion), int(minorVersion), int(patchlevel), downloadUrl

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

