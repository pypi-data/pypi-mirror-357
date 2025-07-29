import pyfiglet
import art
import random
import time
from typing import List, Union
from .colors import Colors
from .colorate import Colorate
from .effects import Effects

class Banner:
    
    @staticmethod
    def ascii_art(text: str, color: Union[str, List[str]] = Colors.rainbow(), font: str = "big") -> str:
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        try:
            fig = pyfiglet.Figlet(font=font)
            ascii_text = fig.renderText(text)
            return Colorate.Horizontal(colors, ascii_text)
        except:
            return Colorate.Horizontal(colors, text)
    
    @staticmethod
    def emoji(text: str, color: Union[str, List[str]] = Colors.yellow) -> str:
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        emoji_text = f"🎨 {text} 🎨"
        return Colorate.Horizontal(colors, emoji_text)
    
    @staticmethod
    def particle(text: str, color: Union[str, List[str]] = Colors.cyan, particle_count: int = 50) -> str:
        if isinstance(color, str):
            colors = [color]
        else:
            colors = color
        
        particles = ["✨", "💫", "⭐", "🌟", "💎", "✨", "💫", "⭐"]
        particle_text = ""
        
        for char in text:
            if char == " ":
                particle_text += char
            else:
                particle = random.choice(particles)
                particle_text += particle
        
        return Colorate.Horizontal(colors, particle_text)
    
    @staticmethod
    def neon_banner(text: str, color: str = Colors.pink, glow_intensity: float = 0.8) -> str:
        ascii_text = Banner.ascii_art(text, color)
        return Effects.neon(ascii_text, color, glow_intensity)
    
    @staticmethod
    def rainbow_banner(text: str, font: str = "big") -> str:
        rainbow_colors = Colors.rainbow()
        return Banner.ascii_art(text, rainbow_colors, font)
    
    @staticmethod
    def gradient_banner(text: str, gradient_type: str = "sunset", font: str = "big") -> str:
        if gradient_type == "sunset":
            colors = Colors.sunset()
        elif gradient_type == "ocean":
            colors = Colors.ocean()
        elif gradient_type == "fire":
            colors = Colors.fire()
        elif gradient_type == "neon":
            colors = Colors.neon()
        else:
            colors = Colors.rainbow()
        
        return Banner.ascii_art(text, colors, font)
    
    @staticmethod
    def glitch_banner(text: str, color: str = Colors.cyan, intensity: float = 0.3) -> str:
        ascii_text = Banner.ascii_art(text, color)
        return Effects.glitch(ascii_text, color, intensity, 0)
    
    @staticmethod
    def hologram_banner(text: str, flicker: bool = True) -> str:
        rainbow_colors = Colors.rainbow()
        ascii_text = Banner.ascii_art(text, rainbow_colors)
        return Effects.hologram(ascii_text, rainbow_colors, flicker)
    
    @staticmethod
    def fire_banner(text: str, height: int = 10) -> str:
        fire_colors = Colors.fire()
        ascii_text = Banner.ascii_art(text, fire_colors)
        return Effects.fire(ascii_text, height, 0)
    
    @staticmethod
    def water_banner(text: str, color: str = Colors.blue) -> str:
        ascii_text = Banner.ascii_art(text, color)
        return Effects.water(ascii_text, color, 0.1)
    
    @staticmethod
    def sparkle_banner(text: str, color: str = Colors.yellow, sparkle_density: float = 0.3) -> str:
        ascii_text = Banner.ascii_art(text, color)
        return Effects.sparkle(ascii_text, color, sparkle_density)
    
    @staticmethod
    def metallic_banner(text: str, metal_type: str = "gold", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.yellow, font)
        return Effects.metallic(ascii_text, metal_type)
    
    @staticmethod
    def crystal_banner(text: str, crystal_type: str = "diamond", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.cyan, font)
        return Effects.crystal(ascii_text, crystal_type)
    
    @staticmethod
    def galaxy_banner(text: str, star_density: float = 0.2, font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.blue, font)
        return Effects.galaxy(ascii_text, star_density)
    
    @staticmethod
    def aurora_banner(text: str, aurora_type: str = "northern", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.green, font)
        return Effects.aurora(ascii_text, aurora_type)
    
    @staticmethod
    def cyberpunk_banner(text: str, neon_intensity: float = 0.8, font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.magenta, font)
        return Effects.cyberpunk(ascii_text, neon_intensity)
    
    @staticmethod
    def retro_banner(text: str, retro_style: str = "80s", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.magenta, font)
        return Effects.retro(ascii_text, retro_style)
    
    @staticmethod
    def vintage_banner(text: str, vintage_style: str = "sepia", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.yellow, font)
        return Effects.vintage(ascii_text, vintage_style)
    
    @staticmethod
    def futuristic_banner(text: str, future_style: str = "hologram", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.cyan, font)
        return Effects.futuristic(ascii_text, future_style)
    
    @staticmethod
    def nature_banner(text: str, nature_type: str = "forest", font: str = "big") -> str:
        ascii_text = Banner.ascii_art(text, Colors.green, font)
        return Effects.nature(ascii_text, nature_type)
    
    @staticmethod
    def animated_banner(text: str, animation_type: str = "rainbow", duration: float = 3.0, font: str = "big") -> str:
        if animation_type == "rainbow":
            rainbow_colors = Colors.rainbow()
            start_time = time.time()
            while time.time() - start_time < duration:
                shifted_colors = rainbow_colors[1:] + rainbow_colors[:1]
                rainbow_colors = shifted_colors
                
                ascii_text = Banner.ascii_art(text, rainbow_colors, font)
                print(f"\r{ascii_text}", end="", flush=True)
                time.sleep(0.1)
            
            print()
            return ascii_text
        elif animation_type == "glitch":
            ascii_text = Banner.ascii_art(text, Colors.cyan, font)
            return Effects.glitch(ascii_text, Colors.cyan, 0.3, duration)
        elif animation_type == "matrix":
            ascii_text = Banner.ascii_art(text, Colors.green, font)
            return Effects.glitch(ascii_text, Colors.green, 0.3, duration)
        else:
            return Banner.ascii_art(text, Colors.rainbow(), font)
    
    @staticmethod
    def custom_banner(text: str, style: str = "default", **kwargs) -> str:
        if style == "neon":
            return Banner.neon_banner(text, **kwargs)
        elif style == "rainbow":
            return Banner.rainbow_banner(text, **kwargs)
        elif style == "gradient":
            return Banner.gradient_banner(text, **kwargs)
        elif style == "glitch":
            return Banner.glitch_banner(text, **kwargs)
        elif style == "hologram":
            return Banner.hologram_banner(text, **kwargs)
        elif style == "fire":
            return Banner.fire_banner(text, **kwargs)
        elif style == "water":
            return Banner.water_banner(text, **kwargs)
        elif style == "sparkle":
            return Banner.sparkle_banner(text, **kwargs)
        elif style == "metallic":
            return Banner.metallic_banner(text, **kwargs)
        elif style == "crystal":
            return Banner.crystal_banner(text, **kwargs)
        elif style == "galaxy":
            return Banner.galaxy_banner(text, **kwargs)
        elif style == "aurora":
            return Banner.aurora_banner(text, **kwargs)
        elif style == "cyberpunk":
            return Banner.cyberpunk_banner(text, **kwargs)
        elif style == "retro":
            return Banner.retro_banner(text, **kwargs)
        elif style == "vintage":
            return Banner.vintage_banner(text, **kwargs)
        elif style == "futuristic":
            return Banner.futuristic_banner(text, **kwargs)
        elif style == "nature":
            return Banner.nature_banner(text, **kwargs)
        else:
            return Banner.ascii_art(text, Colors.rainbow()) 