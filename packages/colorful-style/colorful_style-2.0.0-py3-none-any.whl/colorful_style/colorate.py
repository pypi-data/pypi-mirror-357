"""
Colorate module - Advanced text coloring with gradients and effects
"""

import math
import random
from typing import List, Union, Optional
from .colors import Colors

class Colorate:
    """Advanced text coloring with gradients and effects"""
    
    @staticmethod
    def Color(color: str, text: str, end: bool = True) -> str:
        """Color text with specified color"""
        result = color + text
        if end:
            result += Colors.reset
        return result
    
    @staticmethod
    def Error(text: str, end: bool = True) -> str:
        """Create error effect text"""
        result = Colors.red + Colors.bold + text
        if end:
            result += Colors.reset
        return result
    
    @staticmethod
    def Success(text: str, end: bool = True) -> str:
        """Create success effect text"""
        result = Colors.green + Colors.bold + text
        if end:
            result += Colors.reset
        return result
    
    @staticmethod
    def Warning(text: str, end: bool = True) -> str:
        """Create warning effect text"""
        result = Colors.yellow + Colors.bold + text
        if end:
            result += Colors.reset
        return result
    
    @staticmethod
    def Info(text: str, end: bool = True) -> str:
        """Create info effect text"""
        result = Colors.blue + Colors.bold + text
        if end:
            result += Colors.reset
        return result
    
    @staticmethod
    def Horizontal(colors: Union[List[str], str], text: str, intensity: int = 1) -> str:
        """Apply horizontal gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
                continue
            
            color_index = int((i / len(text)) * (len(colors) - 1))
            color_index = min(color_index, len(colors) - 1)
            result += colors[color_index] + char
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Vertical(colors: Union[List[str], str], text: str, intensity: int = 1) -> str:
        """Apply vertical gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            if not line.strip():
                result_lines.append(line)
                continue
            
            result_line = ""
            for i, char in enumerate(line):
                if char == " ":
                    result_line += char
                    continue
                
                color_index = int((i / max(len(line), 1)) * (len(colors) - 1))
                color_index = min(color_index, len(colors) - 1)
                result_line += colors[color_index] + char
            
            result_lines.append(result_line)
        
        result = '\n'.join(result_lines) + Colors.reset
        return result
    
    @staticmethod
    def Diagonal(colors: Union[List[str], str], text: str, intensity: int = 1) -> str:
        """Apply diagonal gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        result_lines = []
        for line_idx, line in enumerate(lines):
            if not line.strip():
                result_lines.append(line)
                continue
            
            result_line = ""
            for char_idx, char in enumerate(line):
                if char == " ":
                    result_line += char
                    continue
                
                # Calculate diagonal position
                diagonal_pos = (line_idx + char_idx) / (len(lines) + max_line_length - 1)
                color_index = int(diagonal_pos * (len(colors) - 1))
                color_index = min(color_index, len(colors) - 1)
                result_line += colors[color_index] + char
            
            result_lines.append(result_line)
        
        result = '\n'.join(result_lines) + Colors.reset
        return result
    
    @staticmethod
    def DiagonalBackwards(colors: Union[List[str], str], text: str, intensity: int = 1) -> str:
        """Apply backwards diagonal gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        result_lines = []
        for line_idx, line in enumerate(lines):
            if not line.strip():
                result_lines.append(line)
                continue
            
            result_line = ""
            for char_idx, char in enumerate(line):
                if char == " ":
                    result_line += char
                    continue
                
                # Calculate backwards diagonal position
                diagonal_pos = (line_idx + (max_line_length - char_idx)) / (len(lines) + max_line_length - 1)
                color_index = int(diagonal_pos * (len(colors) - 1))
                color_index = min(color_index, len(colors) - 1)
                result_line += colors[color_index] + char
            
            result_lines.append(result_line)
        
        result = '\n'.join(result_lines) + Colors.reset
        return result
    
    @staticmethod
    def Rotating(colors: Union[List[str], str], text: str, intensity: int = 1) -> str:
        """Apply rotating gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
                continue
            
            # Rotate through colors
            color_index = i % len(colors)
            result += colors[color_index] + char
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Wave(colors: Union[List[str], str], text: str, frequency: float = 1.0, amplitude: float = 1.0) -> str:
        """Apply wave gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
                continue
            
            # Create wave effect
            wave_pos = math.sin(i * frequency * 0.1) * amplitude
            color_index = int(((wave_pos + 1) / 2) * (len(colors) - 1))
            color_index = max(0, min(color_index, len(colors) - 1))
            result += colors[color_index] + char
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Pulse(colors: Union[List[str], str], text: str, speed: float = 1.0) -> str:
        """Apply pulse gradient to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) == 1:
            return Colorate.Color(colors[0], text)
        
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
                continue
            
            # Create pulse effect
            pulse_pos = math.sin(i * speed * 0.1)
            color_index = int(((pulse_pos + 1) / 2) * (len(colors) - 1))
            color_index = max(0, min(color_index, len(colors) - 1))
            result += colors[color_index] + char
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Random(colors: Union[List[str], str], text: str, seed: Optional[int] = None) -> str:
        """Apply random colors to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if seed is not None:
            random.seed(seed)
        
        result = ""
        for char in text:
            if char == " ":
                result += char
                continue
            
            color = random.choice(colors)
            result += color + char
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Alternating(colors: Union[List[str], str], text: str, pattern: str = "word") -> str:
        """Apply alternating colors to text"""
        if isinstance(colors, str):
            colors = [colors]
        
        if len(colors) < 2:
            return Colorate.Color(colors[0], text)
        
        result = ""
        color_index = 0
        
        if pattern == "word":
            words = text.split()
            for i, word in enumerate(words):
                color = colors[i % len(colors)]
                result += color + word
                if i < len(words) - 1:
                    result += " "
        elif pattern == "char":
            for char in text:
                if char == " ":
                    result += char
                    continue
                
                color = colors[color_index % len(colors)]
                result += color + char
                color_index += 1
        elif pattern == "line":
            lines = text.split('\n')
            for i, line in enumerate(lines):
                color = colors[i % len(colors)]
                result += color + line
                if i < len(lines) - 1:
                    result += '\n'
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Glow(text: str, color: str, intensity: float = 0.5) -> str:
        """Create glowing text effect"""
        # Create multiple layers for glow effect
        glow_colors = []
        for i in range(5):
            alpha = intensity * (1 - i * 0.2)
            glow_colors.append(Colors.blend(color, Colors.black, alpha))
        
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
                continue
            
            # Add glow layers
            for glow_color in glow_colors:
                result += glow_color + char
            result += color + char
        
        result += Colors.reset
        return result
    
    @staticmethod
    def Shadow(text: str, color: str, shadow_color: str = None, offset: int = 1) -> str:
        """Create shadow text effect"""
        if shadow_color is None:
            shadow_color = Colors.black
        
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            if not line.strip():
                result_lines.append(line)
                continue
            
            # Create shadow
            shadow_line = " " * offset + shadow_color + line + Colors.reset
            # Create main text
            main_line = color + line + Colors.reset
            
            result_lines.append(shadow_line)
            result_lines.append(main_line)
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def Outline(text: str, color: str, outline_color: str = None, thickness: int = 1) -> str:
        """Create outlined text effect"""
        if outline_color is None:
            outline_color = Colors.black
        
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            if not line.strip():
                result_lines.append(line)
                continue
            
            # Create outline by surrounding with outline color
            outlined_line = ""
            for char in line:
                if char == " ":
                    outlined_line += char
                    continue
                
                # Add outline
                for _ in range(thickness):
                    outlined_line += outline_color + char
                # Add main color
                outlined_line += color + char
            
            result_lines.append(outlined_line + Colors.reset)
        
        return '\n'.join(result_lines) 