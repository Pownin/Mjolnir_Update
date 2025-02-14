import sys
import os
from importlib import reload
from ctypes import *
import bpy
#os.system('cls')
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
   sys.path.append(dir)

import mjolnir.mjolnir_ui as mui
import mjolnir.bridge
import mjolnir.duplicate_hotkey
reload(mui)
reload(mjolnir.bridge)
reload(mjolnir.duplicate_hotkey)

from mjolnir.forge_types import *
from mjolnir.halo3 import *
from mjolnir.bridge import *
from mjolnir.duplicate_hotkey import *

def register():
    mui.register_menus()
    mjolnir.duplicate_hotkey.register()
    bridgeMain()
try: 
    mui.unregister_menus()
except: 
    pass
register()
