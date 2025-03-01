"""Provide a service class for the help function.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import webbrowser

from nvupdater.nvupdater_locale import _


class NvupdaterHelp:

    HELP_URL = f'{_("https://peter88213.github.io/nvhelp-en")}/nv_updater/'

    @classmethod
    def open_help_page(cls, event=None):
        """Show the online help page."""
        webbrowser.open(cls.HELP_URL)

