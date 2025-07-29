import time
import random
import math
import sys
import threading
from typing import List, Union, Optional, Callable
from .colors import Colors
from .colorate import Colorate

class Animate:
    """Advanced text animations and effects"""
    
    @staticmethod
    def typing(text: str, color: Union[str, List[str]] = Colors.white, speed: float = 0.05, 
               hide_cursor: bool = True, end: str = "\n") -> str:
        """Animate text typing effect"""
        if hide_cursor:
            print("\033[?25l", end="")  
        
        result = ""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
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
        
        if hide_cursor:
            print("\033[?25h", end="")  
        
        print(end, end="")
        return result
    
    @staticmethod
    def fade_in(text: str, color: Union[str, List[str]] = Colors.white, duration: float = 2.0,
                steps: int = 20) -> str:
        """Animate text fade in effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        step_duration = duration / steps
        
        for step in range(steps):
            alpha = step / steps
            current_colors = []
            
            for color in colors:
                faded_color = Colors.blend(color, Colors.black, alpha)
                current_colors.append(faded_color)
            
            print("\r", end="")
            colored_text = Colorate.Horizontal(current_colors, text)
            print(colored_text, end="", flush=True)
            
            time.sleep(step_duration)
        
        print()  # New line at end
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def fade_out(text: str, color: Union[str, List[str]] = Colors.white, duration: float = 2.0,
                 steps: int = 20) -> str:
        """Animate text fade out effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        step_duration = duration / steps
        
        for step in range(steps):
            alpha = 1 - (step / steps)
            current_colors = []
            
            for color in colors:
                faded_color = Colors.blend(color, Colors.black, alpha)
                current_colors.append(faded_color)
            
            print("\r", end="")
            colored_text = Colorate.Horizontal(current_colors, text)
            print(colored_text, end="", flush=True)
            
            time.sleep(step_duration)
        
        print()  # New line at end
        return ""
    
    @staticmethod
    def blink(text: str, color: Union[str, List[str]] = Colors.white, times: int = 5,
              duration: float = 0.5) -> str:
        """Animate text blink effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        colored_text = Colorate.Horizontal(colors, text)
        
        for _ in range(times):
            print(colored_text, end="\r", flush=True)
            time.sleep(duration)
            print(" " * len(text), end="\r", flush=True)
            time.sleep(duration)
        
        print(colored_text)  # Final display
        return colored_text
    
    @staticmethod
    def rainbow(text: str, duration: float = 3.0, speed: float = 0.1) -> str:
        """Animate rainbow effect on text"""
        rainbow_colors = Colors.rainbow()
        result = ""
        
        start_time = time.time()
        while time.time() - start_time < duration:
            shifted_colors = rainbow_colors[1:] + rainbow_colors[:1]
            rainbow_colors = shifted_colors
            
            colored_text = Colorate.Horizontal(rainbow_colors, text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(speed)
        
        print()  # New line at end
        return Colorate.Horizontal(rainbow_colors, text)
    
    @staticmethod
    def matrix(text: str, duration: float = 5.0, speed: float = 0.05) -> str:
        """Animate Matrix-style effect"""
        matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        result = ""
        
        start_time = time.time()
        while time.time() - start_time < duration:
            matrix_text = ""
            for char in text:
                if char == " ":
                    matrix_text += " "
                else:
                    matrix_text += random.choice(matrix_chars)
            
            colored_text = Colorate.Color(Colors.green, matrix_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(speed)
        
        final_text = Colorate.Color(Colors.green, text)
        print(f"\r{final_text}")
        return final_text
    
    @staticmethod
    def glitch(text: str, duration: float = 3.0, intensity: float = 0.3) -> str:
        """Animate glitch effect on text"""
        glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = ""
        
        start_time = time.time()
        while time.time() - start_time < duration:
            glitch_text = ""
            for char in text:
                if char == " ":
                    glitch_text += " "
                elif random.random() < intensity:
                    glitch_text += random.choice(glitch_chars)
                else:
                    glitch_text += char
            
            colored_text = Colorate.Color(Colors.cyan, glitch_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(0.1)
        
        final_text = Colorate.Color(Colors.cyan, text)
        print(f"\r{final_text}")
        return final_text
    
    @staticmethod
    def bounce(text: str, duration: float = 3.0, height: int = 3) -> str:
        """Animate bouncing text effect"""
        result = ""
        
        start_time = time.time()
        frame = 0
        while time.time() - start_time < duration:
            bounce_pos = int(height * abs(math.sin(frame * 0.5)))
            
            print("\r" + " " * bounce_pos + text, end="", flush=True)
            time.sleep(0.1)
            frame += 1
        
        print()  # New line at end
        return text
    
    @staticmethod
    def wave(text: str, duration: float = 3.0, amplitude: float = 2.0, frequency: float = 1.0) -> str:
        """Animate wave effect on text"""
        result = ""
        
        start_time = time.time()
        frame = 0
        while time.time() - start_time < duration:          
            wave_text = ""
            for i, char in enumerate(text):
                if char == " ":
                    wave_text += " "
                else:
                    wave_offset = int(amplitude * math.sin(frame * frequency + i * 0.5))
                    wave_text += " " * abs(wave_offset) + char
            
            print(f"\r{wave_text}", end="", flush=True)
            time.sleep(0.1)
            frame += 1
        
        print()  # New line at end
        return text
    
    @staticmethod
    def pulse(text: str, duration: float = 3.0, min_size: float = 0.8, max_size: float = 1.2) -> str:
        """Animate pulse effect on text"""
        result = ""
        
        start_time = time.time()
        frame = 0
        while time.time() - start_time < duration:
            pulse_size = min_size + (max_size - min_size) * (math.sin(frame * 0.5) + 1) / 2
            
            scaled_text = " " * int(len(text) * (pulse_size - 1) / 2) + text
            print(f"\r{scaled_text}", end="", flush=True)
            time.sleep(0.1)
            frame += 1
        
        print()  # New line at end
        return text
    
    @staticmethod
    def slide_in(text: str, direction: str = "left", duration: float = 2.0, 
                 color: Union[str, List[str]] = Colors.white) -> str:
        """Animate slide in effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        steps = 50
        step_duration = duration / steps
        
        for step in range(steps):
            progress = step / steps
            
            if direction == "left":
                offset = int((1 - progress) * len(text))
                display_text = " " * offset + text
            elif direction == "right":
                offset = int(progress * len(text))
                display_text = text + " " * offset
            elif direction == "up":
                display_text = text
            elif direction == "down":
                display_text = text
            
            colored_text = Colorate.Horizontal(colors, display_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(step_duration)
        
        print()  # New line at end
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def typewriter(text: str, color: Union[str, List[str]] = Colors.white, speed: float = 0.05,
                   sound: bool = False) -> str:
        """Classic typewriter effect"""
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
            
            if sound:
                print("\a", end="", flush=True)
            
            time.sleep(speed)
        
        print()  # New line at end
        return result
    
    @staticmethod
    def loading(text: str = "Loading", color: Union[str, List[str]] = Colors.blue,
                duration: float = 3.0, dots: int = 3) -> str:
        """Animate loading effect"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        start_time = time.time()
        frame = 0
        
        while time.time() - start_time < duration:
            dot_count = (frame % (dots + 1))
            loading_text = text + "." * dot_count
            
            colored_text = Colorate.Horizontal(colors, loading_text)
            print(f"\r{colored_text}", end="", flush=True)
            time.sleep(0.3)
            frame += 1
        
        print()  # New line at end
        return Colorate.Horizontal(colors, text + "." * dots)
    
    @staticmethod
    def progress_bar(text: str, total: int = 100, current: int = 0,
                    color: Union[str, List[str]] = Colors.green, width: int = 50) -> str:
        """Animate progress bar"""
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
        """Animate spinner effect"""
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
    def fade(text: str, color: Union[str, List[str]] = Colors.white, duration: float = 2.0,
             steps: int = 20) -> str:
        """Animate text fade effect (fade in then out)"""
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        result = ""
        step_duration = duration / (steps * 2)  # Half for fade in, half for fade out
        
        # Fade in
        for step in range(steps):
            alpha = step / steps
            current_colors = []
            
            for color in colors:
                faded_color = Colors.blend(color, Colors.black, alpha)
                current_colors.append(faded_color)
            
            print("\r", end="")
            colored_text = Colorate.Horizontal(current_colors, text)
            print(colored_text, end="", flush=True)
            
            time.sleep(step_duration)
        
        # Fade out
        for step in range(steps):
            alpha = 1 - (step / steps)
            current_colors = []
            
            for color in colors:
                faded_color = Colors.blend(color, Colors.black, alpha)
                current_colors.append(faded_color)
            
            print("\r", end="")
            colored_text = Colorate.Horizontal(current_colors, text)
            print(colored_text, end="", flush=True)
            
            time.sleep(step_duration)
        
        print()  # New line at end
        return Colorate.Horizontal(colors, text) 