"""Provide an update service class for novelibre.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvlib.controller.services.service_base import ServiceBase
from nvlib.gui.set_icon_tk import set_icon
from nvupdater.nvupdater_help import NvupdaterHelp
from nvupdater.update_manager import UpdateManager


class UpdateService(ServiceBase):

    def __init__(self, model, view, controller):
        super().__init__(model, view, controller)

    def check_for_updates(self):
        """Check novelibre and all installed plugins for updates."""
        self.updaterDialog = UpdateManager(self._mdl, self._ui, self._ctrl)
        set_icon(self.updaterDialog, icon='update', default=False)
        self.updaterDialog.check_repos()

    def open_help(self):
        """Show the nv_updater online help page."""
        NvupdaterHelp.open_help_page()
