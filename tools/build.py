"""Build the nv_updater novelibre plugin package.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the novxlib package.

The novxlib project (see see https://github.com/peter88213/novxlib)
must be located on the same directory level as the nv_updater project. 

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_updater
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys

sys.path.insert(0, f'{os.getcwd()}/../../novxlib/src')
from package_builder import PackageBuilder

VERSION = '4.1.2'


class PluginBuilder(PackageBuilder):

    PRJ_NAME = 'nv_updater'
    LOCAL_LIB = 'nvupdaterlib'
    GERMAN_TRANSLATION = True

    def build_script(self):
        os.makedirs(self.testDir, exist_ok=True)
        self.inline_modules(self.sourceFile, self.testFile)
        self.insert_version_number(self.testFile, version=self.version)


def main():
    pb = PluginBuilder(VERSION)
    pb.run()


if __name__ == '__main__':
    main()
