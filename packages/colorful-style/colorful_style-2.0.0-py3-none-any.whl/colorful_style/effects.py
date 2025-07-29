"""
Effects module - Special visual effects and advanced styling
"""

import time
import random
import math
import os
from typing import List, Union, Optional
from .colors import Colors
from .colorate import Colorate

class Effects:
    """Special visual effects and advanced styling"""
    
    @staticmethod
    def glitch(text: str, color: str = Colors.cyan, intensity: float = 0.3, 
               duration: float = 2.0) -> str:
        """Create glitch effect on text"""
        if duration > 0:
            start_time = time.time()
            while time.time() - start_time < duration:
                glitch_text = ""
                for char in text:
                    if char == " ":
                        glitch_text += char
                    elif random.random() < intensity:
                        glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
                        glitch_text += random.choice(glitch_chars)
                    else:
                        glitch_text += char
                
                print(f"\r{Colorate.Color(color, glitch_text)}", end="", flush=True)
                time.sleep(0.1)
            
            final_text = Colorate.Color(Colors.cyan, text)
            print(f"\r{final_text}")
            return final_text
        else:
            # Static glitch effect
            glitch_text = ""
            for char in text:
                if char == " ":
                    glitch_text += char
                elif random.random() < intensity:
                    glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
                    glitch_text += random.choice(glitch_chars)
                else:
                    glitch_text += char
            
            return Colorate.Color(color, glitch_text)
    
    @staticmethod
    def neon(text: str, color: str = Colors.magenta, glow_intensity: float = 0.8) -> str:
        """Create neon glow effect"""
        # Create multiple glow layers
        glow_colors = []
        for i in range(5):
            alpha = glow_intensity * (1 - i * 0.2)
            glow_colors.append(Colors.blend(color, Colors.black, alpha))
        
        neon_text = ""
        for char in text:
            if char == " ":
                neon_text += char
            else:
                for glow_color in glow_colors:
                    neon_text += glow_color + char
                neon_text += color + char
        
        return neon_text + Colors.reset
    
    @staticmethod
    def hologram(text: str, colors: Union[str, List[str]] = Colors.rainbow(), flicker: bool = True) -> str:
        """Create hologram effect"""
        if isinstance(colors, str):
            colors = [colors]
        
        if flicker:
            # Animated hologram
            start_time = time.time()
            while time.time() - start_time < 3.0:
                # Shift colors for flicker effect
                shifted_colors = colors[1:] + colors[:1]
                colors = shifted_colors
                
                colored_text = Colorate.Horizontal(colors, text)
                print(f"\r{colored_text}", end="", flush=True)
                time.sleep(0.1)
            
            print()  # New line at end
            return Colorate.Horizontal(colors, text)
        else:
            # Static hologram
            return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def fire(text: str, height: int = 10, duration: float = 3.0) -> str:
        """Create fire effect"""
        if duration > 0:
            start_time = time.time()
            while time.time() - start_time < duration:
                # Create fire effect
                fire_text = ""
                for char in text:
                    if char == " ":
                        fire_text += " "
                    else:
                        fire_chars = ["🔥", "💥", "🔥", "💥", "🔥"]
                        fire_text += random.choice(fire_chars)
                
                print(f"\r{Colorate.Color(Colors.red, fire_text)}", end="", flush=True)
                time.sleep(0.1)
            
            print()  # New line at end
            return text
        else:
            # Static fire effect
            fire_text = ""
            for char in text:
                if char == " ":
                    fire_text += " "
                else:
                    fire_chars = ["🔥", "💥", "🔥", "💥", "🔥"]
                    fire_text += random.choice(fire_chars)
            
            return Colorate.Color(Colors.red, fire_text)
    
    @staticmethod
    def water(text: str, color: str = Colors.blue, ripple_speed: float = 0.1) -> str:
        """Create water ripple effect"""
        water_chars = ["💧", "🌊", "💧", "🌊", "💧"]
        
        start_time = time.time()
        while time.time() - start_time < 3.0:
            # Create water effect
            water_text = ""
            for char in text:
                if char == " ":
                    water_text += " "
                else:
                    water_char = random.choice(water_chars)
                    water_text += color + water_char + Colors.reset
            
            print(f"\r{water_text}", end="", flush=True)
            time.sleep(ripple_speed)
        
        print()  # New line at end
        return text
    
    @staticmethod
    def smoke(text: str, color: str = Colors.bright_black, density: float = 0.5) -> str:
        """Create smoke effect"""
        smoke_chars = ["💨", "☁️", "🌫️", "💨", "☁️", "🌫️"]
        
        smoke_text = ""
        for char in text:
            if char == " ":
                smoke_text += " "
            elif random.random() < density:
                smoke_char = random.choice(smoke_chars)
                smoke_text += color + smoke_char + Colors.reset
            else:
                smoke_text += char
        
        return smoke_text
    
    @staticmethod
    def lightning(text: str, color: str = Colors.yellow, intensity: float = 0.7) -> str:
        """Create lightning effect"""
        lightning_chars = ["⚡", "💥", "✨", "⚡", "💥", "✨"]
        
        if random.random() < intensity:
            lightning_text = ""
            for char in text:
                if char == " ":
                    lightning_text += " "
                else:
                    lightning_char = random.choice(lightning_chars)
                    lightning_text += color + lightning_char + Colors.reset
            
            return lightning_text
        else:
            return Colorate.Color(color, text)
    
    @staticmethod
    def sparkle(text: str, color: str = Colors.gold, sparkle_density: float = 0.3) -> str:
        """Create sparkle effect"""
        sparkle_chars = ["✨", "💫", "⭐", "🌟", "💎", "✨", "💫", "⭐"]
        
        sparkle_text = ""
        for char in text:
            if char == " ":
                sparkle_text += " "
            elif random.random() < sparkle_density:
                sparkle_char = random.choice(sparkle_chars)
                sparkle_text += color + sparkle_char + Colors.reset
            else:
                sparkle_text += char
        
        return sparkle_text
    
    @staticmethod
    def rainbow_static(text: str) -> str:
        """Create static rainbow effect"""
        rainbow_colors = Colors.rainbow()
        return Colorate.Horizontal(rainbow_colors, text)
    
    @staticmethod
    def gradient_static(text: str, gradient_type: str = "rainbow") -> str:
        """Create static gradient effect"""
        if gradient_type == "rainbow":
            colors = Colors.rainbow()
        elif gradient_type == "sunset":
            colors = Colors.sunset()
        elif gradient_type == "ocean":
            colors = Colors.ocean()
        elif gradient_type == "fire":
            colors = Colors.fire()
        elif gradient_type == "neon":
            colors = Colors.neon()
        else:
            colors = Colors.rainbow()
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def metallic(text: str, metal_type: str = "gold") -> str:
        """Create metallic effect"""
        if metal_type == "gold":
            colors = [Colors.yellow]
        elif metal_type == "silver":
            colors = [Colors.bright_white]
        elif metal_type == "bronze":
            colors = Colors.custom_gradient((205, 127, 50), (139, 69, 19))
        elif metal_type == "platinum":
            colors = Colors.custom_gradient((229, 228, 226), (192, 192, 192))
        else:
            colors = [Colors.yellow]
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def crystal(text: str, crystal_type: str = "diamond") -> str:
        """Create crystal effect"""
        if crystal_type == "diamond":
            colors = Colors.custom_gradient((185, 242, 255), (255, 255, 255))
        elif crystal_type == "ruby":
            colors = Colors.custom_gradient((255, 0, 0), (139, 0, 0))
        elif crystal_type == "emerald":
            colors = Colors.custom_gradient((0, 255, 127), (0, 100, 0))
        elif crystal_type == "sapphire":
            colors = Colors.custom_gradient((0, 191, 255), (0, 0, 139))
        else:
            colors = Colors.custom_gradient((185, 242, 255), (255, 255, 255))
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def galaxy(text: str, star_density: float = 0.2) -> str:
        """Create galaxy effect with stars"""
        star_chars = ["⭐", "🌟", "💫", "✨", "⭐", "🌟", "💫", "✨"]
        galaxy_colors = Colors.custom_gradient((25, 25, 112), (138, 43, 226))
        
        galaxy_text = ""
        for char in text:
            if char == " ":
                galaxy_text += " "
            elif random.random() < star_density:
                star_char = random.choice(star_chars)
                galaxy_text += Colors.yellow + star_char + Colors.reset
            else:
                galaxy_text += char
        
        return Colorate.Horizontal(galaxy_colors, galaxy_text)
    
    @staticmethod
    def aurora(text: str, aurora_type: str = "northern") -> str:
        """Create aurora effect"""
        if aurora_type == "northern":
            colors = Colors.multi_gradient([
                (0, 255, 127),   # Green
                (0, 191, 255),   # Blue
                (138, 43, 226),  # Purple
                (255, 20, 147)   # Pink
            ])
        elif aurora_type == "southern":
            colors = Colors.multi_gradient([
                (255, 0, 0),     # Red
                (255, 165, 0),   # Orange
                (255, 255, 0),   # Yellow
                (0, 255, 0)      # Green
            ])
        else:
            colors = Colors.rainbow()
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def cyberpunk(text: str, neon_intensity: float = 0.8) -> str:
        """Create cyberpunk effect"""
        cyber_colors = Colors.multi_gradient([
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Cyan
            (255, 255, 0),   # Yellow
            (255, 0, 0)      # Red
        ])
        
        cyber_text = Colorate.Horizontal(cyber_colors, text)
        return Effects.neon(cyber_text, Colors.magenta, neon_intensity)
    
    @staticmethod
    def retro(text: str, retro_style: str = "80s") -> str:
        """Create retro effect"""
        if retro_style == "80s":
            colors = Colors.multi_gradient([
                (255, 0, 255),   # Magenta
                (0, 255, 255),   # Cyan
                (255, 255, 0),   # Yellow
                (255, 0, 0)      # Red
            ])
        elif retro_style == "70s":
            colors = Colors.multi_gradient([
                (255, 165, 0),   # Orange
                (255, 255, 0),   # Yellow
                (0, 255, 0),     # Green
                (0, 0, 255)      # Blue
            ])
        else:
            colors = Colors.rainbow()
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def vintage(text: str, vintage_style: str = "sepia") -> str:
        """Create vintage effect"""
        if vintage_style == "sepia":
            colors = Colors.custom_gradient((139, 69, 19), (255, 228, 196))
        elif vintage_style == "black_white":
            colors = Colors.custom_gradient((0, 0, 0), (255, 255, 255))
        elif vintage_style == "faded":
            colors = Colors.custom_gradient((128, 128, 128), (192, 192, 192))
        else:
            colors = Colors.custom_gradient((139, 69, 19), (255, 228, 196))
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def futuristic(text: str, future_style: str = "hologram") -> str:
        """Create futuristic effect"""
        if future_style == "hologram":
            colors = Colors.multi_gradient([
                (0, 255, 255),   # Cyan
                (255, 0, 255),   # Magenta
                (255, 255, 0),   # Yellow
                (0, 255, 0)      # Green
            ])
        elif future_style == "neon":
            colors = Colors.multi_gradient([
                (255, 0, 255),   # Magenta
                (0, 255, 255),   # Cyan
                (255, 255, 0),   # Yellow
                (255, 0, 0)      # Red
            ])
        else:
            colors = Colors.rainbow()
        
        return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def nature(text: str, nature_type: str = "forest") -> str:
        """Create nature effect"""
        if nature_type == "forest":
            colors = Colors.multi_gradient([
                (34, 139, 34),   # Forest Green
                (0, 128, 0),     # Green
                (50, 205, 50),   # Lime Green
                (144, 238, 144)  # Light Green
            ])
        elif nature_type == "ocean":
            colors = Colors.multi_gradient([
                (0, 191, 255),   # Deep Sky Blue
                (0, 0, 255),     # Blue
                (0, 255, 255),   # Cyan
                (173, 216, 230)  # Light Blue
            ])
        elif nature_type == "sunset":
            colors = Colors.multi_gradient([
                (255, 69, 0),    # Red Orange
                (255, 140, 0),   # Dark Orange
                (255, 215, 0),   # Gold
                (255, 255, 0)    # Yellow
            ])
        else:
            colors = Colors.rainbow()
        
        return Colorate.Horizontal(colors, text) 