# Run this file :)
# Author: Esmail
import sys

from model import Core
from qt_gui import run
core = Core()  # this might change after load has happened!
status = run(core)
sys.exit(status)

