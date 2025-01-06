"""Provide an update manager service class for novelibre.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import configparser
from urllib.request import urlopen
import webbrowser

from mvclib.controller.service_base import ServiceBase
from nvupdater.nvupdater_locale import _


class CancelCheck(Exception):
    """Exception used for cancelling the update check."""
    pass


class UpdateManager(ServiceBase):

    def __init__(self, model, view, controller):
        super().__init__(model, view, controller)
        self.download = False

    def check_for_updates(self):
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
            self._ui.show_error(_('No online update information for novelibre found.'), title=('Check for updates'))
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
                self._ui.show_info(_('No updates available.'), title=_('Check for updates'))
        except CancelCheck:
            # user pressed the "cancel" button
            pass
        finally:
            if self.download:
                self._ui.show_info(_('Please restart novelibre after installing updates.'), title=_('Check for updates'))

    def _download_update(self, repo, downloadUrl):
        """Start the web browser with downloadUrl on demand.
        
        Positional arguments:
            repo: str -- Repository name of the app or plugin.
            downloadUrl: str -- Download URL of the latest release in the repository.
        
        Exceptions:
            raise CancelCheck, if the update check is to be cancelled.
        """
        text = f'{_("An update is available for")} {repo}.\n{_("Start your web browser for download?")}'
        answer = self._ui.ask_yes_no_cancel(text, title=_('Check for updates'))
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

