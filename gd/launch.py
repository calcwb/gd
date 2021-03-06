# Copyright (C) 2011  Governo do Estado do Rio Grande do Sul
#
#   Author: Lincoln de Sousa <lincoln@gg.rs.gov.br>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import gettext
import warnings
from sqlalchemy.exc import SAWarning

# This just screws up all the site, so let's handle it this way before
# finding where that damn ascii string is being inserted.
warnings.filterwarnings(
    'ignore',
    '^Unicode type received non-unicode bind param value',
    SAWarning)


# Hardcoded language configuration
for lang in 'LANGUAGE', 'LANG':
    os.environ[lang] = 'pt_BR'


# Installing the translation files
gettext.install('gabinetedigital', os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'po')),
                unicode=True)


# These imports *must* be declared after installing gettext, otherwise,
# the magic `_' function will not be present in the imported modules
from gd import conf
from gd.content import app
