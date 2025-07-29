"""
Align module - Text alignment and centering functions
"""

import os
import shutil
from typing import Union, List
from .colors import Colors
from .colorate import Colorate

class Align:
    """Text alignment and centering functions"""
    
    @staticmethod
    def Center(text: str, color: Union[str, List[str]] = Colors.white) -> str:
        """Center text on both X and Y axes"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal size
        try:
            terminal_width, terminal_height = shutil.get_terminal_size()
        except:
            terminal_width, terminal_height = 80, 24
        
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        # Calculate centering
        x_padding = max(0, (terminal_width - max_line_length) // 2)
        y_padding = max(0, (terminal_height - len(lines)) // 2)
        
        # Add vertical padding
        result = ['\n' * y_padding]
        
        # Center each line
        for line in lines:
            centered_line = ' ' * x_padding + line
            colored_line = Colorate.Horizontal(colors, centered_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def XCenter(text: str, color: Union[str, List[str]] = Colors.white) -> str:
        """Center text on X axis only"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal width
        try:
            terminal_width, _ = shutil.get_terminal_size()
        except:
            terminal_width = 80
        
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        # Calculate centering
        x_padding = max(0, (terminal_width - max_line_length) // 2)
        
        # Center each line
        result = []
        for line in lines:
            centered_line = ' ' * x_padding + line
            colored_line = Colorate.Horizontal(colors, centered_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def YCenter(text: str, color: Union[str, List[str]] = Colors.white) -> str:
        """Center text on Y axis only"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal height
        try:
            _, terminal_height = shutil.get_terminal_size()
        except:
            terminal_height = 24
        
        lines = text.split('\n')
        
        # Calculate centering
        y_padding = max(0, (terminal_height - len(lines)) // 2)
        
        # Add vertical padding
        result = ['\n' * y_padding]
        
        # Color each line
        for line in lines:
            colored_line = Colorate.Horizontal(colors, line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Left(text: str, color: Union[str, List[str]] = Colors.white, padding: int = 0) -> str:
        """Align text to the left with optional padding"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        lines = text.split('\n')
        
        # Add padding and color each line
        result = []
        for line in lines:
            padded_line = ' ' * padding + line
            colored_line = Colorate.Horizontal(colors, padded_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Right(text: str, color: Union[str, List[str]] = Colors.white) -> str:
        """Align text to the right"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal width
        try:
            terminal_width, _ = shutil.get_terminal_size()
        except:
            terminal_width = 80
        
        lines = text.split('\n')
        
        # Right align each line
        result = []
        for line in lines:
            padding = max(0, terminal_width - len(line))
            aligned_line = ' ' * padding + line
            colored_line = Colorate.Horizontal(colors, aligned_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Justify(text: str, color: Union[str, List[str]] = Colors.white, width: int = None) -> str:
        """Justify text to fill the width"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal width if not specified
        if width is None:
            try:
                width, _ = shutil.get_terminal_size()
            except:
                width = 80
        
        lines = text.split('\n')
        
        # Justify each line
        result = []
        for line in lines:
            if len(line) >= width:
                # Line is already long enough
                colored_line = Colorate.Horizontal(colors, line)
                result.append(colored_line)
                continue
            
            words = line.split()
            if len(words) <= 1:
                # Single word or empty line
                colored_line = Colorate.Horizontal(colors, line)
                result.append(colored_line)
                continue
            
            # Calculate spacing
            total_spaces = width - len(line.replace(' ', ''))
            gaps = len(words) - 1
            if gaps == 0:
                colored_line = Colorate.Horizontal(colors, line)
                result.append(colored_line)
                continue
            
            base_spaces = total_spaces // gaps
            extra_spaces = total_spaces % gaps
            
            # Build justified line
            justified_line = words[0]
            for i, word in enumerate(words[1:], 1):
                spaces = base_spaces + (1 if i <= extra_spaces else 0)
                justified_line += ' ' * spaces + word
            
            colored_line = Colorate.Horizontal(colors, justified_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Wrap(text: str, color: Union[str, List[str]] = Colors.white, width: int = None) -> str:
        """Wrap text to specified width"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal width if not specified
        if width is None:
            try:
                width, _ = shutil.get_terminal_size()
            except:
                width = 80
        
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= width:
                wrapped_lines.append(line)
                continue
            
            # Wrap long lines
            words = line.split()
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 <= width:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            
            if current_line:
                wrapped_lines.append(current_line)
        
        # Color all lines
        result = []
        for line in wrapped_lines:
            colored_line = Colorate.Horizontal(colors, line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Indent(text: str, color: Union[str, List[str]] = Colors.white, indent: int = 4) -> str:
        """Indent text with specified number of spaces"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        lines = text.split('\n')
        
        # Indent each line
        result = []
        for line in lines:
            indented_line = ' ' * indent + line
            colored_line = Colorate.Horizontal(colors, indented_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Outdent(text: str, color: Union[str, List[str]] = Colors.white, indent: int = 4) -> str:
        """Remove specified number of spaces from the beginning of each line"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        lines = text.split('\n')
        
        # Outdent each line
        result = []
        for line in lines:
            if line.startswith(' ' * indent):
                outdented_line = line[indent:]
            else:
                outdented_line = line
            colored_line = Colorate.Horizontal(colors, outdented_line)
            result.append(colored_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def Block(text: str, color: Union[str, List[str]] = Colors.white, 
              width: int = None, height: int = None) -> str:
        """Create a text block with specified dimensions"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        # Get terminal size if not specified
        if width is None or height is None:
            try:
                term_width, term_height = shutil.get_terminal_size()
                if width is None:
                    width = term_width
                if height is None:
                    height = term_height
            except:
                if width is None:
                    width = 80
                if height is None:
                    height = 24
        
        lines = text.split('\n')
        
        # Truncate or pad lines to fit width
        formatted_lines = []
        for line in lines:
            if len(line) > width:
                formatted_lines.append(line[:width])
            else:
                formatted_lines.append(line.ljust(width))
        
        # Truncate or pad to fit height
        while len(formatted_lines) < height:
            formatted_lines.append(' ' * width)
        
        if len(formatted_lines) > height:
            formatted_lines = formatted_lines[:height]
        
        # Color all lines
        result = []
        for line in formatted_lines:
            colored_line = Colorate.Horizontal(colors, line)
            result.append(colored_line)
        
        return '\n'.join(result) 