"""
Interactive module - Interactive UI components
"""

import random
import time
import sys
import threading
from typing import List, Union, Optional, Callable
from .colors import Colors
from .colorate import Colorate

class Interactive:
    """Interactive UI components"""
    
    @staticmethod
    def progress_bar(text: str, total: int = 100, current: int = 0,
                    color: Union[str, List[str]] = Colors.blue, width: int = 50) -> str:
        """Create animated progress bar"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        progress = current / total
        filled_width = int(width * progress)
        bar = "█" * filled_width + "░" * (width - filled_width)
        
        colored_bar = Colorate.Horizontal(colors, bar)
        result = f"{text}: [{colored_bar}] {current}/{total} ({progress*100:.1f}%)"
        
        print(f"\r{result}", end="", flush=True)
        return result
    
    @staticmethod
    def spinner(text: str = "Processing", color: Union[str, List[str]] = Colors.cyan,
                duration: float = 3.0) -> str:
        """Create animated spinner"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        start_time = time.time()
        frame = 0
        
        while time.time() - start_time < duration:
            spinner = spinner_chars[frame % len(spinner_chars)]
            spinner_text = f"{spinner} {text}"
            
            colored_text = Colorate.Horizontal(colors, spinner_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(0.1)
            frame += 1
        
        print()  # New line at end
        return Colorate.Horizontal(colors, f"✓ {text}")
    
    @staticmethod
    def menu(title: str, options: List[str], color: Union[str, List[str]] = Colors.cyan) -> int:
        """Create interactive menu"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        print(Colorate.Horizontal(colors, title))
        print()
        
        for i, option in enumerate(options):
            print(Colorate.Horizontal(colors, f"{i+1}. {option}"))
        
        print()
        
        while True:
            try:
                choice = int(input(Colorate.Horizontal(colors, "Chọn tùy chọn: ")))
                if 1 <= choice <= len(options):
                    return choice - 1
                else:
                    print(Colorate.Error("Tùy chọn không hợp lệ!"))
            except ValueError:
                print(Colorate.Error("Vui lòng nhập số!"))
    
    @staticmethod
    def input(prompt: str, color: Union[str, List[str]] = Colors.cyan) -> str:
        """Create colored input prompt"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        colored_prompt = Colorate.Horizontal(colors, prompt)
        return input(colored_prompt)
    
    @staticmethod
    def confirm(message: str, color: Union[str, List[str]] = Colors.yellow) -> bool:
        """Create confirmation dialog"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        colored_message = Colorate.Horizontal(colors, f"{message} (y/N): ")
        response = input(colored_message).lower().strip()
        return response in ['y', 'yes', '1', 'true']
    
    @staticmethod
    def loading_bar(text: str, duration: float = 3.0, color: Union[str, List[str]] = Colors.green) -> str:
        """Create loading bar animation"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        start_time = time.time()
        bar_width = 30
        
        while time.time() - start_time < duration:
            progress = (time.time() - start_time) / duration
            filled_width = int(bar_width * progress)
            bar = "█" * filled_width + "░" * (bar_width - filled_width)
            
            colored_bar = Colorate.Horizontal(colors, bar)
            result = f"{text}: [{colored_bar}] {progress*100:.1f}%"
            
            print(f"\r{result}", end="", flush=True)
            time.sleep(0.1)
        
        print()  # New line at end
        return Colorate.Horizontal(colors, f"{text}: Hoàn thành!")
    
    @staticmethod
    def countdown(seconds: int, text: str = "Countdown", color: Union[str, List[str]] = Colors.red) -> str:
        """Create countdown timer"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        for i in range(seconds, 0, -1):
            countdown_text = f"{text}: {i:02d}"
            colored_text = Colorate.Horizontal(colors, countdown_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(1)
        
        print()  # New line at end
        return Colorate.Horizontal(colors, f"{text}: Hoàn thành!")
    
    @staticmethod
    def typing_effect(text: str, color: Union[str, List[str]] = Colors.white, speed: float = 0.05) -> str:
        """Create typing effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
                print(char, end="", flush=True)
                continue
            
            color_index = i % len(colors)
            colored_char = colors[color_index] + char + Colors.reset
            result += colored_char
            print(colored_char, end="", flush=True)
            time.sleep(speed)
        
        print()  # New line at end
        return result
    
    @staticmethod
    def blink_text(text: str, color: Union[str, List[str]] = Colors.white, times: int = 5) -> str:
        """Create blinking text effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        colored_text = Colorate.Horizontal(colors, text)
        
        for _ in range(times):
            print(colored_text, end="\r", flush=True)
            time.sleep(0.5)
            print(" " * len(text), end="\r", flush=True)
            time.sleep(0.5)
        
        print(colored_text)  # Final display
        return colored_text
    
    @staticmethod
    def pulse_text(text: str, color: Union[str, List[str]] = Colors.white, duration: float = 3.0) -> str:
        """Create pulsing text effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        start_time = time.time()
        frame = 0
        
        while time.time() - start_time < duration:
            # Create pulse effect
            pulse_intensity = abs((frame % 20) - 10) / 10
            pulse_colors = []
            
            for color in colors:
                # Blend with black for pulse effect
                pulse_color = Colors.blend(color, Colors.black, pulse_intensity)
                pulse_colors.append(pulse_color)
            
            colored_text = Colorate.Horizontal(pulse_colors, text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(0.1)
            frame += 1
        
        print()  # New line at end
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def rainbow_text(text: str, duration: float = 3.0) -> str:
        """Create rainbow text animation"""
        rainbow_colors = Colors.rainbow()
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Shift colors
            shifted_colors = rainbow_colors[1:] + rainbow_colors[:1]
            rainbow_colors = shifted_colors
            
            colored_text = Colorate.Horizontal(rainbow_colors, text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(0.1)
        
        print()  # New line at end
        return Colorate.Horizontal(rainbow_colors, text)
    
    @staticmethod
    def matrix_effect(text: str, duration: float = 5.0) -> str:
        """Create Matrix-style effect"""
        matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Create matrix effect
            matrix_text = ""
            for char in text:
                if char == " ":
                    matrix_text += " "
                else:
                    matrix_text += random.choice(matrix_chars)
            
            colored_text = Colorate.Color(Colors.green, matrix_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(0.1)
        
        # Final display with original text
        final_text = Colorate.Color(Colors.green, text)
        print(f"\r{final_text}")
        return final_text 