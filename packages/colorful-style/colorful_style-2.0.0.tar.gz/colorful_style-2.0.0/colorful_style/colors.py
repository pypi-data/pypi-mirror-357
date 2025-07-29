"""
Colors module - Advanced color system with RGB, hex, and gradient support
"""

import colorsys
import math
from typing import List, Tuple, Union
from colorama import Fore, Back, Style
from termcolor import colored

class Colors:
    """Advanced color system with 256 colors, RGB, hex, and gradient support"""
    
    # Basic ANSI colors
    black = Fore.BLACK
    red = Fore.RED
    green = Fore.GREEN
    yellow = Fore.YELLOW
    blue = Fore.BLUE
    magenta = Fore.MAGENTA
    cyan = Fore.CYAN
    white = Fore.WHITE
    
    # Bright colors
    bright_black = Fore.LIGHTBLACK_EX
    bright_red = Fore.LIGHTRED_EX
    bright_green = Fore.LIGHTGREEN_EX
    bright_yellow = Fore.LIGHTYELLOW_EX
    bright_blue = Fore.LIGHTBLUE_EX
    bright_magenta = Fore.LIGHTMAGENTA_EX
    bright_cyan = Fore.LIGHTCYAN_EX
    bright_white = Fore.LIGHTWHITE_EX
    
    # Background colors
    bg_black = Back.BLACK
    bg_red = Back.RED
    bg_green = Back.GREEN
    bg_yellow = Back.YELLOW
    bg_blue = Back.BLUE
    bg_magenta = Back.MAGENTA
    bg_cyan = Back.CYAN
    bg_white = Back.WHITE
    
    # Styles
    bold = Style.BRIGHT
    dim = Style.DIM
    normal = Style.NORMAL
    reset = Style.RESET_ALL
    
    # Custom colors
    gold = "\033[38;5;220m"
    silver = "\033[38;5;248m"
    purple = "\033[38;5;99m"
    pink = "\033[38;5;213m"
    orange = "\033[38;5;208m"
    brown = "\033[38;5;130m"
    lime = "\033[38;5;154m"
    teal = "\033[38;5;30m"
    indigo = "\033[38;5;57m"
    violet = "\033[38;5;147m"
    
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Create RGB color escape sequence"""
        return f"\033[38;2;{r};{g};{b}m"
    
    @staticmethod
    def hex(hex_color: str) -> str:
        """Convert hex color to RGB escape sequence"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return Colors.rgb(r, g, b)
    
    @staticmethod
    def hsl(h: float, s: float, l: float) -> str:
        """Convert HSL to RGB escape sequence"""
        r, g, b = colorsys.hls_to_rgb(h/360, l, s)
        return Colors.rgb(int(r*255), int(g*255), int(b*255))
    
    @staticmethod
    def hsv(h: float, s: float, v: float) -> str:
        """Convert HSV to RGB escape sequence"""
        r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
        return Colors.rgb(int(r*255), int(g*255), int(b*255))
    
    @staticmethod
    def ansi256(color_code: int) -> str:
        """Create 256-color ANSI escape sequence"""
        return f"\033[38;5;{color_code}m"
    
    # Predefined gradients
    @staticmethod
    def rainbow() -> List[str]:
        """Generate rainbow gradient colors"""
        colors = []
        for i in range(360):
            r, g, b = colorsys.hsv_to_rgb(i/360, 1, 1)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def sunset() -> List[str]:
        """Generate sunset gradient colors"""
        colors = []
        for i in range(100):
            # Orange to pink to purple
            if i < 33:
                r, g, b = colorsys.hsv_to_rgb(30/360, 1, 1 - i/100)
            elif i < 66:
                r, g, b = colorsys.hsv_to_rgb(330/360, 1, 0.5 + i/200)
            else:
                r, g, b = colorsys.hsv_to_rgb(270/360, 1, 0.3 + i/300)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def ocean() -> List[str]:
        """Generate ocean gradient colors"""
        colors = []
        for i in range(100):
            # Blue to cyan to light blue
            r, g, b = colorsys.hsv_to_rgb(200/360, 0.8, 0.3 + i/150)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def forest() -> List[str]:
        """Generate forest gradient colors"""
        colors = []
        for i in range(100):
            # Dark green to light green
            r, g, b = colorsys.hsv_to_rgb(120/360, 0.8, 0.2 + i/120)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def fire() -> List[str]:
        """Generate fire gradient colors"""
        colors = []
        for i in range(100):
            # Red to orange to yellow
            if i < 50:
                r, g, b = colorsys.hsv_to_rgb(0/360, 1, 0.5 + i/100)
            else:
                r, g, b = colorsys.hsv_to_rgb(60/360, 1, 0.5 + (i-50)/100)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def neon() -> List[str]:
        """Generate neon gradient colors"""
        colors = []
        for i in range(100):
            # Bright cyan to bright pink
            r, g, b = colorsys.hsv_to_rgb((180 + i*1.8)/360, 1, 1)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def gold() -> List[str]:
        """Generate gold gradient colors"""
        colors = []
        for i in range(100):
            # Dark gold to bright gold
            r, g, b = colorsys.hsv_to_rgb(45/360, 0.8, 0.3 + i/120)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def silver() -> List[str]:
        """Generate silver gradient colors"""
        colors = []
        for i in range(100):
            # Dark gray to light gray
            gray = 50 + i*2
            colors.append(Colors.rgb(gray, gray, gray))
        return colors
    
    @staticmethod
    def purple() -> List[str]:
        """Generate purple gradient colors"""
        colors = []
        for i in range(100):
            # Dark purple to light purple
            r, g, b = colorsys.hsv_to_rgb(270/360, 0.8, 0.2 + i/120)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def pink() -> List[str]:
        """Generate pink gradient colors"""
        colors = []
        for i in range(100):
            # Dark pink to light pink
            r, g, b = colorsys.hsv_to_rgb(330/360, 0.8, 0.3 + i/120)
            colors.append(Colors.rgb(int(r*255), int(g*255), int(b*255)))
        return colors
    
    @staticmethod
    def custom_gradient(color1: Tuple[int, int, int], color2: Tuple[int, int, int], steps: int = 100) -> List[str]:
        """Create custom gradient between two RGB colors"""
        colors = []
        for i in range(steps):
            ratio = i / (steps - 1)
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            colors.append(Colors.rgb(r, g, b))
        return colors
    
    @staticmethod
    def multi_gradient(colors: List[Tuple[int, int, int]], steps_per_segment: int = 50) -> List[str]:
        """Create gradient with multiple color stops"""
        result = []
        for i in range(len(colors) - 1):
            segment = Colors.custom_gradient(colors[i], colors[i+1], steps_per_segment)
            result.extend(segment)
        return result
    
    @staticmethod
    def random_color() -> str:
        """Generate random color"""
        import random
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return Colors.rgb(r, g, b)
    
    @staticmethod
    def random_gradient(steps: int = 100) -> List[str]:
        """Generate random gradient"""
        import random
        colors = []
        for _ in range(steps):
            colors.append(Colors.random_color())
        return colors
    
    @staticmethod
    def get_color_by_name(name: str) -> str:
        """Get color by name (case insensitive)"""
        color_map = {
            'black': Colors.black,
            'red': Colors.red,
            'green': Colors.green,
            'yellow': Colors.yellow,
            'blue': Colors.blue,
            'magenta': Colors.magenta,
            'cyan': Colors.cyan,
            'white': Colors.white,
            'gold': Colors.gold,
            'silver': Colors.silver,
            'purple': Colors.purple,
            'pink': Colors.pink,
            'orange': Colors.orange,
            'brown': Colors.brown,
            'lime': Colors.lime,
            'teal': Colors.teal,
            'indigo': Colors.indigo,
            'violet': Colors.violet,
        }
        return color_map.get(name.lower(), Colors.white)
    
    @staticmethod
    def blend(color1: str, color2: str, ratio: float = 0.5) -> str:
        """Blend two colors with given ratio"""
        # Extract RGB values from escape sequences
        def extract_rgb(color_str):
            if color_str.startswith('\033[38;2;'):
                parts = color_str[7:-1].split(';')
                return (int(parts[0]), int(parts[1]), int(parts[2]))
            return (255, 255, 255)  # Default to white
        
        rgb1 = extract_rgb(color1)
        rgb2 = extract_rgb(color2)
        
        r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio)
        g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio)
        b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio)
        
        return Colors.rgb(r, g, b) 