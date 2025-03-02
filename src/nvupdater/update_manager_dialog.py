"""Provide a class for an updater dialog.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk

from nvlib.gui.platform.platform_settings import KEYS
from nvlib.gui.widgets.modal_dialog import ModalDialog
from nvupdater.nvupdater_help import NvupdaterHelp
from nvupdater.nvupdater_locale import _
from nvupdater.update_manager_ctrl import UpdateManagerCtrl
import tkinter as tk


class UpdateManagerDialog(ModalDialog, UpdateManagerCtrl):

    MIN_HEIGHT = 450

    def __init__(self, model, view, controller, **kw):
        super().__init__(view, **kw)
        self.minsize(1, self.MIN_HEIGHT)
        self.initialize_controller(model, view, controller)

        self.title(f'{_("Check for updates")} - novelibre @release')

        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        columns = 'Module', 'Installed version', 'Latest version'
        self.repoList = ttk.Treeview(self, columns=columns, show='headings', selectmode='browse')

        # scrollY = ttk.Scrollbar(self.moduleCollection, orient='vertical', command=self.moduleCollection.yview)
        # self.moduleCollection.configure(yscrollcommand=scrollY.set)
        # scrollY.pack(side='right', fill='y')
        #--- unsolved problem: adding a scollbar makes the window shrink to minimum

        self.repoList.pack(fill='both', expand=True)
        self.repoList.bind('<<TreeviewSelect>>', self.on_select_module)
        self.repoList.tag_configure('outdated', foreground='red')
        self.repoList.tag_configure('updated', foreground='green')
        self.repoList.tag_configure('inactive', foreground='gray')

        self.repoList.column('Module', width=150, minwidth=120, stretch=False)
        self.repoList.heading('Module', text=_('Module'), anchor='w')
        self.repoList.column('Installed version', width=100, minwidth=100, stretch=False)
        self.repoList.heading('Installed version', text=_('Installed version'), anchor='w')
        self.repoList.column('Latest version', width=100, minwidth=100, stretch=False)
        self.repoList.heading('Latest version', text=_('Latest version'), anchor='w')

        self.messagingArea = tk.Label(self, fg='white', bg='green')
        self.messagingArea.pack(fill='x')

        self._footer = ttk.Frame(self)
        self._footer.pack(fill='both', expand=False)

        # "Update" button.
        self.updateButton = ttk.Button(
            self._footer,
            text=_('Update'),
            command=self.update_module,
            state='disabled'
            )
        self.updateButton.pack(padx=5, pady=5, side='left')

        # "Home page" button.
        self.homeButton = ttk.Button(
            self._footer,
            text=_('Home page'),
            command=self.open_homepage,
            state='disabled'
            )
        self.homeButton.pack(padx=5, pady=5, side='left')

        # "Close" button.
        ttk.Button(
            self._footer,
            text=_('Close'),
            command=self.on_quit
            ).pack(padx=5, pady=5, side='right')

        # "Help" button.
        ttk.Button(
            self._footer,
            text=_('Online help'),
            command=NvupdaterHelp.open_help_page
            ).pack(padx=5, pady=5, side='right')

        # Set Key bindings.
        self.bind(KEYS.OPEN_HELP[0], NvupdaterHelp.open_help_page)
        self.repoList.bind('<Double-1>', self.update_module)

        # Populate the list.
        self.build_module_list()

    def output(self, text):
        try:
            self.messagingArea.configure(text=text)
        except:
            pass

