"""Provide a class for an updater dialog.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk

from nvlib.gui.platform.platform_settings import KEYS
from nvlib.gui.widgets.modal_dialog import ModalDialog
from nvupdater.update_manager_ctrl import UpdateManagerCtrl
from nvupdater.nvupdater_locale import _


class UpdateManagerDialog(ModalDialog, UpdateManagerCtrl):

    def __init__(self, model, view, controller, **kw):
        super().__init__(view, **kw)
        self.initialize_controller(model, view, controller)

        self.title(f'{_("Check for updates")} - novelibre @release')

        columns = 'Module', 'Installed version', 'Latest version'
        self.moduleCollection = ttk.Treeview(self, columns=columns, show='headings', selectmode='browse')

        # scrollY = ttk.Scrollbar(self.moduleCollection, orient='vertical', command=self.moduleCollection.yview)
        # self.moduleCollection.configure(yscrollcommand=scrollY.set)
        # scrollY.pack(side='right', fill='y')
        #--- unsolved problem: adding a scollbar makes the window shrink to minimum

        self.moduleCollection.pack(fill='both', expand=True)
        self.moduleCollection.bind('<<TreeviewSelect>>', self.on_select_module)
        self.moduleCollection.tag_configure('rejected', foreground='red')
        self.moduleCollection.tag_configure('inactive', foreground='gray')

        self.moduleCollection.column('Module', width=150, minwidth=120, stretch=False)
        self.moduleCollection.heading('Module', text=_('Module'), anchor='w')
        self.moduleCollection.column('Installed version', width=100, minwidth=100, stretch=False)
        self.moduleCollection.heading('Installed version', text=_('Installed version'), anchor='w')
        self.moduleCollection.column('Latest version', width=100, minwidth=100, stretch=False)
        self.moduleCollection.heading('Latest version', text=_('Latest version'), anchor='w')

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

        self._footer = ttk.Frame(self)
        self._footer.pack(fill='both', expand=False)

        # "Home page" button.
        self.homeButton = ttk.Button(
            self._footer,
            text=_('Home page'),
            command=self.open_homepage,
            state='disabled'
            )
        self.homeButton.pack(padx=5, pady=5, side='left')

        # "Update" button.
        self.updateButton = ttk.Button(
            self._footer,
            text=_('Update'),
            command=self.update_module,
            state='disabled'
            )
        self.updateButton.pack(padx=5, pady=5, side='left')

        # "Close" button.
        ttk.Button(
            self._footer,
            text=_('Close'),
            command=self.destroy
            ).pack(padx=5, pady=5, side='right')

        # "Help" button.
        ttk.Button(
            self._footer,
            text=_('Online help'),
            command=self.open_help
            ).pack(padx=5, pady=5, side='right')

        # Set Key bindings.
        self.bind(KEYS.OPEN_HELP[0], self.open_help)

    def output(self, text):
        print(text)

