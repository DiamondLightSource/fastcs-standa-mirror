from fastcs import launch

from fastcs_standa_mirror import __version__
from fastcs_standa_mirror.mirror_controller import MirrorController
from fastcs_standa_mirror.utils import patch_move_flags

# Work around libximc highlevel API bug: real hardware returns undocumented
# MoveFlags bits (e.g. 0xCC) that the MoveFlags enum rejects. This must run
# before any call to get_move_settings()
patch_move_flags()

launch(controller_classes=MirrorController, version=__version__)
