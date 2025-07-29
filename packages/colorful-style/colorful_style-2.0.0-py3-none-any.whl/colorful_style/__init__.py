__version__ = "2.0.0"
__author__ = "QuangThangCoder"
__email__ = "quangthangcoder@gmail.com"
__description__ = "A beautiful and advanced Python library for creating stunning TUI designs with enhanced colors and effects"


from .colors import Colors
from .colorate import Colorate
from .animate import Animate
from .effects import Effects
from .box import Box
from .align import Align
from .interactive import Interactive
from .banner import Banner
from .system import System
from .config import Config
from .utils import Utils


__all__ = [
    'Colors',
    'Colorate', 
    'Animate',
    'Effects',
    'Box',
    'Align',
    'Interactive',
    'Banner',
    'System',
    'Config',
    'Utils'
]

        
import colorama
colorama.init(autoreset=True) 