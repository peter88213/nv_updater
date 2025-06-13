"""Provide a class for an updater dialog.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import configparser
from tkinter import ttk
from urllib.request import urlopen
import webbrowser

from nvlib.controller.sub_controller import SubController
from nvlib.gui.platform.platform_settings import KEYS
from nvlib.gui.widgets.modal_dialog import ModalDialog
from nvupdater.nvupdater_help import NvupdaterHelp
from nvupdater.nvupdater_locale import _
import tkinter as tk


class UpdateManager(ModalDialog, SubController):

    MIN_HEIGHT = 450

    def __init__(self, model, view, controller, **kw):
        super().__init__(view, **kw)
        self._mdl = model
        self._ui = view
        self._ctrl = controller
        self.minsize(1, self.MIN_HEIGHT)
        self._downloadUrls = {}
        self._download = False
        self._stopSearching = False

        self.title(f'{_("Check for updates")} - novelibre @release')

        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        columns = 'Plugin', 'Installed version', 'Latest version'
        self._repoList = ttk.Treeview(
            self, columns=columns,
            show='headings',
            selectmode='browse',
        )

        # scrollY = ttk.Scrollbar(
        #    self.moduleCollection, orient='vertical',
        #    command=self.moduleCollection.yview,
        # )
        # self.moduleCollection.configure(yscrollcommand=scrollY.set)
        # scrollY.pack(side='right', fill='y')
        #--- unsolved problem: adding a scollbar makes the window shrink to minimum

        self._repoList.pack(fill='both', expand=True)
        self._repoList.bind('<<TreeviewSelect>>', self._on_select_plugin)
        self._repoList.tag_configure('outdated', foreground='red')
        self._repoList.tag_configure('updated', foreground='blue')
        self._repoList.tag_configure('inactive', foreground='gray')

        self._repoList.column(
            'Plugin',
            width=150,
            minwidth=120,
            stretch=False,
        )
        self._repoList.heading(
            'Plugin',
            text=_('Plugin'),
            anchor='w',
        )
        self._repoList.column(
            'Installed version',
            width=100,
            minwidth=100,
            stretch=False,
        )
        self._repoList.heading(
            'Installed version',
            text=_('Installed version'),
            anchor='w',
        )
        self._repoList.column(
            'Latest version',
            width=100,
            minwidth=100,
            stretch=False,
        )
        self._repoList.heading(
            'Latest version',
            text=_('Latest version'),
            anchor='w',
        )

        self._messagingArea = tk.Label(self, fg='white', bg='green')
        self._messagingArea.pack(fill='x')

        self._footer = ttk.Frame(self)
        self._footer.pack(fill='both', expand=False)

        # "Update" button.
        self._updateButton = ttk.Button(
            self._footer,
            text=_('Update'),
            command=self._update_module,
            state='disabled',
        )
        self._updateButton.pack(padx=5, pady=5, side='left')

        # "Home page" button.
        self._homeButton = ttk.Button(
            self._footer,
            text=_('Home page'),
            command=self._open_homepage,
            state='disabled',
        )
        self._homeButton.pack(padx=5, pady=5, side='left')

        # "Close" button.
        ttk.Button(
            self._footer,
            text=_('Close'),
            command=self.on_quit,
        ).pack(padx=5, pady=5, side='right')

        # "Help" button.
        ttk.Button(
            self._footer,
            text=_('Online help'),
            command=NvupdaterHelp.open_help_page,
        ).pack(padx=5, pady=5, side='right')

        # Set Key bindings.
        self.bind(KEYS.OPEN_HELP[0], NvupdaterHelp.open_help_page)
        self._repoList.bind('<Double-1>', self._update_module)

        # Populate the list.
        self._build_module_list()

    def check_repos(self):
        """Check the repositories and update the view.
        
        Add the URLs to download from to the downloadUrls dictionary.
        """
        self._output(f"{_('Looking for updates')}...")
        found = False

        # Check novelibre.
        repoName = 'novelibre'
        current = (
            self._ctrl.plugins.majorVersion,
            self._ctrl.plugins.minorVersion,
            self._ctrl.plugins.patchlevel,
        )
        currentStr = (
            f'{self._ctrl.plugins.majorVersion}.'
            f'{self._ctrl.plugins.minorVersion}.'
            f'{self._ctrl.plugins.patchlevel}'
        )
        try:
            (majorVersion,
             minorVersion,
             patchlevel,
             downloadUrl) = self._get_remote_data(repoName)
        except:
            latestStr = _('unknown')
            tags = ()
        else:
            latest = (majorVersion, minorVersion, patchlevel)
            latestStr = f'{majorVersion}.{minorVersion}.{patchlevel}'
            if self._update_available(latest, current):
                self._downloadUrls[repoName] = downloadUrl
                tags = ('outdated')
                found = True
            else:
                tags = ()
        self._refresh_display(
            repoName,
            [repoName, currentStr, latestStr],
            tags=tags,
        )

        # Check installed plugins.
        for repoName in self._ctrl.plugins:
            if self._stopSearching:
                return

            if self._ctrl.plugins[repoName].isRejected:
                continue

            try:
                (majorVersion,
                 minorVersion,
                 patchlevel) = self._ctrl.plugins[repoName].VERSION.split('.')
                current = (
                    int(majorVersion),
                    int(minorVersion),
                    int(patchlevel),
                )
                currentStr = f'{majorVersion}.{minorVersion}.{patchlevel}'
            except:
                current = (0, 0, 0)
                currentStr = _('unknown')
            try:
                (majorVersion,
                 minorVersion,
                 patchlevel,
                 downloadUrl) = self._get_remote_data(repoName)
                latest = (majorVersion, minorVersion, patchlevel)
                latestStr = f'{majorVersion}.{minorVersion}.{patchlevel}'
            except:
                latestStr = _('unknown')
                tags = ()
            else:
                if self._update_available(latest, current):
                    self._downloadUrls[repoName] = downloadUrl
                    tags = ('outdated')
                    found = True
                else:
                    tags = ()
            self._refresh_display(
                repoName,
                [repoName, currentStr, latestStr],
                tags=tags,
                )
        if not found:
            self._output(f"{_('No updates available')}.")
        else:
            self._output(f"{_('Finished')}.")

    def on_quit(self):
        """Display a warning if something might have been updated."""
        self._stopSearching = True
        if self._download:
            self._ui.show_info(
                message=_('Please restart novelibre after installing updates'),
                detail=f"{_('Outdated components remain active until next start')}.",
                title=_('Check for updates'),
                parent=self,
            )
        self.destroy()

    def _build_module_list(self):
        # Populate _repoList with repository entries.
        # Prepare the downloadUrls dictionary for repositories to update from.
        repoName = 'novelibre'
        self._downloadUrls[repoName] = None
        appValues = [
            repoName,
            (
                f'{self._ctrl.plugins.majorVersion}.'
                f'{self._ctrl.plugins.minorVersion}.'
                f'{self._ctrl.plugins.patchlevel}'
            ),
            f"{_('wait')} ...",
            ]
        self._repoList.insert('', 'end', 'novelibre', values=appValues)

        for repoName in self._ctrl.plugins:
            if self._ctrl.plugins[repoName].isRejected:
                continue

            self._downloadUrls[repoName] = None
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
            self._repoList.insert(
                '', 'end',
                repoName,
                values=columns,
                tags=tuple(nodeTags),
            )
        self.update()
        # enforcing the display before returning
        # to the time-consuming internet lookup

    def _get_remote_data(self, repoName):
        # Return a tuple with the version number components and the download URL.
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

    def _on_select_plugin(self, event):
        # Enable or disable the selected repo's "Update" and "Home" buttons.
        repoName = self._repoList.selection()[0]
        homeButtonState = 'disabled'
        updateButtonState = 'disabled'
        if repoName:
            if  repoName == 'novelibre':
                homeButtonState = 'normal'
                updateButtonState = 'normal'
            else:
                try:
                    if self._ctrl.plugins[repoName].URL:
                        # there is a repository URL defined
                        # for the selected module
                        homeButtonState = 'normal'
                except:
                    pass
                try:
                    if self._downloadUrls[repoName] is not None:
                        # the selected module is outdated
                        updateButtonState = 'normal'
                except:
                    pass
        self._homeButton.configure(state=homeButtonState)
        self._updateButton.configure(state=updateButtonState)

    def _open_homepage(self, event=None):
        # Start the web browser with the selected module's home page.
        repoName = self._repoList.selection()[0]
        if repoName:
            if repoName == 'novelibre':
                webbrowser.open(self._mdl.nvService.get_novelibre_home_url())
                return

            try:
                url = self._ctrl.plugins[repoName].URL
                if url:
                    webbrowser.open(url)
            except:
                pass

    def _output(self, text):
        try:
            self._messagingArea.configure(text=text)
        except:
            pass

    def _refresh_display(self, repoName, values, tags=()):
        # Update the version numbers and colors of an entry in the _repoList.
        try:
            self._repoList.item(repoName, values=values, tags=tags)
            self.update()
        except:
            pass
            # preventing an error due to pending checks
            # while the window is already closed

    def _update_available(self, latest, current):
        # Return True, if the latest version number is greater
        # than the current one.
        if latest[0] > current[0]:
            return True

        if latest[0] == current[0]:
            if latest[1] > current[1]:
                return True

            if latest[1] == current[1]:
                if latest[2] > current[2]:
                    return True

        return False

    def _update_module(self, event=None):
        # Start the web browser with the selected module's update URL.
        repoName = self._repoList.selection()[0]
        if self._downloadUrls[repoName] is None:
            return

        webbrowser.open(self._downloadUrls[repoName])
        self._repoList.item(repoName, tags=('updated'))
        self._download = True

