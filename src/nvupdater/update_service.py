"""Provide an update service class for novelibre.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import socket
from nvlib.controller.services.service_base import ServiceBase
from nvlib.gui.set_icon_tk import set_icon
from nvupdater.update_manager import UpdateManager
from nvupdater.nvupdater_locale import _


class UpdateService(ServiceBase):

    HOST = 'www.github.com'

    def __init__(self, model, view, controller):
        super().__init__(model, view, controller)

    def check_for_updates(self):
        """Check novelibre and all installed plugins for updates."""

        def is_connected():
            try:
                # connect to the host -- tells us if the host is actually
                # reachable
                sock = socket.create_connection((self.HOST, 80))
                if sock is not None:
                    sock.close
                return True

            except OSError:
                return False

        if not is_connected():
            self._ui.show_error(
                title=_('Check for updates'),
                message=f"{_('Cannot connect via the internet')}:",
                detail=self.HOST,
            )
            return

        self.updaterDialog = UpdateManager(self._mdl, self._ui, self._ctrl)
        set_icon(self.updaterDialog, icon='update', default=False)
        self.updaterDialog.check_repos()

