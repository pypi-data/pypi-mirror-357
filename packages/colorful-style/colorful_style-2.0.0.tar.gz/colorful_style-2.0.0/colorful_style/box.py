"""
Box module - Various box styles and containers
"""

import random
from typing import List, Union
from .colors import Colors
from .colorate import Colorate

class Box:
    """Various box styles and containers"""
    
    @staticmethod
    def simple(content: str, color: str = Colors.blue) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "┌" + "─" * (max_length + 2) + "┐" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "│ " + padded_line + " │" + Colors.reset)
        
        box.append(color + "└" + "─" * (max_length + 2) + "┘" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def double(content: str, color: str = Colors.green) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "╔" + "═" * (max_length + 2) + "╗" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "║ " + padded_line + " ║" + Colors.reset)
        
        box.append(color + "╚" + "═" * (max_length + 2) + "╝" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def rounded(content: str, color: str = Colors.purple) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "╭" + "─" * (max_length + 2) + "╮" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "│ " + padded_line + " │" + Colors.reset)
        
        box.append(color + "╰" + "─" * (max_length + 2) + "╯" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def gradient(content: str, colors: Union[str, List[str]] = Colors.rainbow()) -> str:
        if isinstance(colors, str):
            colors = [colors]
        
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        top_color = colors[0] if colors else Colors.blue
        box.append(top_color + "┌" + "─" * (max_length + 2) + "┐" + Colors.reset)
        
        for i, line in enumerate(lines):
            color_index = (i + 1) % len(colors) if colors else 0
            color = colors[color_index] if colors else Colors.blue
            padded_line = line.ljust(max_length)
            box.append(color + "│ " + padded_line + " │" + Colors.reset)
        
        bottom_color = colors[-1] if colors else Colors.blue
        box.append(bottom_color + "└" + "─" * (max_length + 2) + "┘" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def neon(content: str, color: str = Colors.magenta) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "╔" + "═" * (max_length + 2) + "╗" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "║ " + padded_line + " ║" + Colors.reset)
        
        box.append(color + "╚" + "═" * (max_length + 2) + "╝" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def fancy(content: str, color: str = Colors.yellow) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "╭" + "─" * (max_length + 2) + "╮" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "│ " + padded_line + " │" + Colors.reset)
        
        box.append(color + "╰" + "─" * (max_length + 2) + "╯" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def minimal(content: str, color: str = Colors.cyan) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "┌" + "─" * (max_length + 2) + "┐" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "│ " + padded_line + " │" + Colors.reset)
        
        box.append(color + "└" + "─" * (max_length + 2) + "┘" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def thick(content: str, color: str = Colors.red) -> str:
        lines = content.split('\n')
        max_length = max(len(line) for line in lines) if lines else 0
        
        box = []
        box.append(color + "█" + "█" * (max_length + 2) + "█" + Colors.reset)
        
        for line in lines:
            padded_line = line.ljust(max_length)
            box.append(color + "█ " + padded_line + " █" + Colors.reset)
        
        box.append(color + "█" + "█" * (max_length + 2) + "█" + Colors.reset)
        
        return '\n'.join(box)
    
    @staticmethod
    def sunset(content: str) -> str:
        colors = Colors.rainbow()
        return Box.gradient(content, colors)
    
    @staticmethod
    def ocean(content: str) -> str:
        colors = Colors.rainbow()
        return Box.gradient(content, colors)
    
    @staticmethod
    def fire(content: str) -> str:
        fire_colors = [Colors.red, Colors.yellow, Colors.orange]
        return Box.gradient(content, fire_colors)
    
    @staticmethod
    def rainbow(content: str) -> str:
        rainbow_colors = Colors.rainbow()
        return Box.gradient(content, rainbow_colors)
    
    @staticmethod
    def custom(content: str, style: str = "simple", **kwargs) -> str:
        if style == "simple":
            return Box.simple(content, **kwargs)
        elif style == "double":
            return Box.double(content, **kwargs)
        elif style == "rounded":
            return Box.rounded(content, **kwargs)
        elif style == "gradient":
            return Box.gradient(content, **kwargs)
        elif style == "neon":
            return Box.neon(content, **kwargs)
        elif style == "fancy":
            return Box.fancy(content, **kwargs)
        elif style == "minimal":
            return Box.minimal(content, **kwargs)
        elif style == "thick":
            return Box.thick(content, **kwargs)
        elif style == "sunset":
            return Box.sunset(content)
        elif style == "ocean":
            return Box.ocean(content)
        elif style == "fire":
            return Box.fire(content)
        elif style == "rainbow":
            return Box.rainbow(content)
        else:
            return Box.simple(content, **kwargs) 