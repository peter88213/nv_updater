"""An update checker plugin for novelibre.

Requires Python 3.6+
Copyright (c) 2025 Peter Triesberger
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
import webbrowser

from nvupdater.nvupdater_locale import _
from nvlib.controller.plugin.plugin_base import PluginBase
from nvupdater.update_manager import UpdateManager


class Plugin(PluginBase):
    """Plugin class for the novelibre update checker."""
    VERSION = '@release'
    API_VERSION = '5.0'
    DESCRIPTION = 'Update checker'
    URL = 'https://github.com/peter88213/nv_updater'
    HELP_URL = f'{_("https://peter88213.github.io/nvhelp-en")}/nv_updater/'

    def install(self, model, view, controller):
        """Install the plugin and extend the novelibre user interface.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Extends the superclass method.
        """
        super().install(model, view, controller)
        self.updateManager = UpdateManager(model, view, controller)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('Update checker Online help'), command=self.open_help)

        # Add an entry to the Tools menu.
        self._ui.toolsMenu.add_command(label=_('Check for updates'), command=self.check_for_updates)

    def check_for_updates(self):
        self.updateManager.check_for_updates()

    def open_help(self, event=None):
        webbrowser.open(self.HELP_URL)

