"""Provide an update manager service class for novelibre.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvlib.controller.services.service_base import ServiceBase
from nvupdater.update_manager_dialog import UpdateManagerDialog


class UpdateManager(ServiceBase):

    def __init__(self, model, view, controller):
        super().__init__(model, view, controller)

    def check_for_updates(self):
        """Check novelibre and all installed plugins for updates."""
        self.updaterDialog = UpdateManagerDialog(self._mdl, self._ui, self._ctrl)
        self.updaterDialog.check_repos()

