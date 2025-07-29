import random
import string
import time
import math
import re
from typing import List, Union, Optional, Callable
from .colors import Colors
from .colorate import Colorate

class Utils:
    
    @staticmethod
    def random_string(length: int = 10, include_special: bool = False) -> str:
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def random_color() -> str:
        return Colors.random_color()
    
    @staticmethod
    def random_gradient(steps: int = 100) -> List[str]:
        return Colors.random_gradient(steps)
    
    @staticmethod
    def random_effect() -> str:
        effects = ["rainbow", "neon", "glitch", "fire", "water", "sparkle", "metallic", "crystal"]
        return random.choice(effects)
    
    @staticmethod
    def random_animation() -> str:
        animations = ["typing", "fade", "blink", "bounce", "wave", "pulse", "slide", "matrix"]
        return random.choice(animations)
    
    @staticmethod
    def random_gradient_type() -> str:
        gradients = ["rainbow", "sunset", "ocean", "fire", "neon", "gold", "silver", "purple", "pink"]
        return random.choice(gradients)
    
    @staticmethod
    def random_box_style() -> str:
        styles = ["simple", "double", "rounded", "gradient", "neon", "fancy", "minimal", "thick"]
        return random.choice(styles)
    
    @staticmethod
    def random_banner_style() -> str:
        styles = ["ascii_art", "emoji", "particle", "neon", "rainbow", "gradient", "glitch", "hologram"]
        return random.choice(styles)
    
    @staticmethod
    def generate_lorem_ipsum(paragraphs: int = 1, sentences_per_paragraph: int = 5) -> str:
        lorem_words = [
            "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
            "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
            "magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
            "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea",
            "commodo", "consequat", "duis", "aute", "irure", "dolor", "in", "reprehenderit",
            "voluptate", "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla",
            "pariatur", "excepteur", "sint", "occaecat", "cupidatat", "non", "proident",
            "sunt", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est",
            "laborum", "et", "dolore", "magna", "aliqua", "ut", "enim", "ad", "minim"
        ]
        
        result = []
        for _ in range(paragraphs):
            paragraph = []
            for _ in range(sentences_per_paragraph):
                sentence_length = random.randint(5, 15)
                sentence_words = random.sample(lorem_words, min(sentence_length, len(lorem_words)))
                sentence = ' '.join(sentence_words).capitalize() + '.'
                paragraph.append(sentence)
            result.append(' '.join(paragraph))
        
        return '\n\n'.join(result)
    
    @staticmethod
    def text_to_ascii_art(text: str, font: str = "big") -> str:
        try:
            import pyfiglet
            fig = pyfiglet.Figlet(font=font)
            return fig.renderText(text)
        except:
            return text
    
    @staticmethod
    def text_to_emoji(text: str) -> str:
        emoji_map = {
            'a': '🍎', 'b': '🍌', 'c': '🍊', 'd': '🍇', 'e': '🍓', 'f': '🍑', 'g': '🍒',
            'h': '🍍', 'i': '🥝', 'j': '🥭', 'k': '🥥', 'l': '🍋', 'm': '🍈', 'n': '🍉',
            'o': '🍊', 'p': '🍐', 'q': '🍎', 'r': '🍌', 's': '🍊', 't': '🍇', 'u': '🍓',
            'v': '🍑', 'w': '🍒', 'x': '🍍', 'y': '🥝', 'z': '🥭',
            '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
            '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣',
            ' ': ' ', '!': '❗', '?': '❓', '.': '💎', ',': '💫'
        }
        
        result = ""
        for char in text.lower():
            result += emoji_map.get(char, char)
        return result
    
    @staticmethod
    def text_to_particles(text: str) -> str:
        particles = ["✨", "💫", "⭐", "🌟", "💎", "✨", "💫", "⭐"]
        result = ""
        for char in text:
            if char == " ":
                result += char
            else:
                result += random.choice(particles)
        return result
    
    @staticmethod
    def text_to_matrix(text: str) -> str:
        matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        result = ""
        for char in text:
            if char == " ":
                result += " "
            else:
                result += random.choice(matrix_chars)
        return result
    
    @staticmethod
    def text_to_glitch(text: str, intensity: float = 0.3) -> str:
        glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = ""
        for char in text:
            if char == " ":
                result += char
            elif random.random() < intensity:
                result += random.choice(glitch_chars)
            else:
                result += char
        return result
    
    @staticmethod
    def text_to_binary(text: str) -> str:
        binary_map = {
            'a': '01100001', 'b': '01100010', 'c': '01100011', 'd': '01100100',
            'e': '01100101', 'f': '01100110', 'g': '01100111', 'h': '01101000',
            'i': '01101001', 'j': '01101010', 'k': '01101011', 'l': '01101100',
            'm': '01101101', 'n': '01101110', 'o': '01101111', 'p': '01110000',
            'q': '01110001', 'r': '01110010', 's': '01110011', 't': '01110100',
            'u': '01110101', 'v': '01110110', 'w': '01110111', 'x': '01111000',
            'y': '01111001', 'z': '01111010', ' ': ' '
        }
        
        result = ""
        for char in text.lower():
            result += binary_map.get(char, char) + " "
        return result.strip()
    
    @staticmethod
    def text_to_hex(text: str) -> str:
        result = ""
        for char in text:
            if char == " ":
                result += " "
            else:
                result += hex(ord(char))[2:] + " "
        return result.strip()
    
    @staticmethod
    def text_to_morse(text: str) -> str:
        morse_map = {
            'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.',
            'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
            'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.',
            's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
            'y': '-.--', 'z': '--..', ' ': ' '
        }
        
        result = ""
        for char in text.lower():
            result += morse_map.get(char, char) + " "
        return result.strip()
    
    @staticmethod
    def reverse_text(text: str) -> str:
        return text[::-1]
    
    @staticmethod
    def alternate_case(text: str) -> str:
        result = ""
        for i, char in enumerate(text):
            if i % 2 == 0:
                result += char.upper()
            else:
                result += char.lower()
        return result
    
    @staticmethod
    def sponge_case(text: str) -> str:
        result = ""
        for char in text:
            if random.random() < 0.5:
                result += char.upper()
            else:
                result += char.lower()
        return result
    
    @staticmethod
    def leet_speak(text: str) -> str:
        leet_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7',
            'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7'
        }
        
        result = ""
        for char in text:
            result += leet_map.get(char, char)
        return result
    
    @staticmethod
    def word_count(text: str) -> int:
        return len(text.split())
    
    @staticmethod
    def character_count(text: str, include_spaces: bool = True) -> int:
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(" ", ""))
    
    @staticmethod
    def line_count(text: str) -> int:
        return len(text.split('\n'))
    
    @staticmethod
    def average_word_length(text: str) -> float:
        words = text.split()
        if not words:
            return 0
        total_length = sum(len(word) for word in words)
        return total_length / len(words)
    
    @staticmethod
    def reading_time(text: str, words_per_minute: int = 200) -> float:
        words = Utils.word_count(text)
        return words / words_per_minute
    
    @staticmethod
    def speaking_time(text: str, words_per_minute: int = 150) -> float:
        words = Utils.word_count(text)
        return words / words_per_minute
    
    @staticmethod
    def extract_words(text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        return re.split(r'[.!?]+', text)
    
    @staticmethod
    def extract_paragraphs(text: str) -> List[str]:
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    @staticmethod
    def remove_duplicates(text: str) -> str:
        words = text.split()
        seen = set()
        result = []
        for word in words:
            if word not in seen:
                seen.add(word)
                result.append(word)
        return ' '.join(result)
    
    @staticmethod
    def remove_punctuation(text: str) -> str:
        return re.sub(r'[^\w\s]', '', text)
    
    @staticmethod
    def remove_numbers(text: str) -> str:
        return re.sub(r'\d+', '', text)
    
    @staticmethod
    def remove_spaces(text: str) -> str:
        return text.replace(" ", "")
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def capitalize_words(text: str) -> str:
        return ' '.join(word.capitalize() for word in text.split())
    
    @staticmethod
    def title_case(text: str) -> str:
        return text.title()
    
    @staticmethod
    def sentence_case(text: str) -> str:
        sentences = re.split(r'([.!?]+)', text)
        result = []
        for i, part in enumerate(sentences):
            if i % 2 == 0:
                result.append(part.capitalize())
            else:
                result.append(part)
        return ''.join(result)
    
    @staticmethod
    def wrap_text(text: str, width: int = 80) -> str:
        import textwrap
        return textwrap.fill(text, width=width)
    
    @staticmethod
    def justify_text(text: str, width: int = 80) -> str:
        import textwrap
        return textwrap.fill(text, width=width, replace_whitespace=False)
    
    @staticmethod
    def truncate_text(text: str, length: int = 100, suffix: str = "...") -> str:
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix
    
    @staticmethod
    def pad_text(text: str, width: int, align: str = "left", char: str = " ") -> str:
        if align == "left":
            return text.ljust(width, char)
        elif align == "right":
            return text.rjust(width, char)
        elif align == "center":
            return text.center(width, char)
        else:
            return text
    
    @staticmethod
    def format_number(number: Union[int, float], format_type: str = "default") -> str:
        if format_type == "comma":
            return f"{number:,}"
        elif format_type == "currency":
            return f"${number:,.2f}"
        elif format_type == "percentage":
            return f"{number:.2%}"
        elif format_type == "scientific":
            return f"{number:.2e}"
        else:
            return str(number)
    
    @staticmethod
    def format_time(seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}PB"
    
    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 50, 
                           filled_char: str = "█", empty_char: str = "░") -> str:
        progress = current / total
        filled_width = int(width * progress)
        bar = filled_char * filled_width + empty_char * (width - filled_width)
        return f"[{bar}] {progress*100:.1f}%"
    
    @staticmethod
    def create_spinner(frames: List[str] = None) -> str:
        if frames is None:
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return frames[int(time.time() * 10) % len(frames)]
    
    @staticmethod
    def create_loading_dots(dots: int = 3) -> str:
        return "." * (int(time.time() * 2) % (dots + 1))
    
    @staticmethod
    def create_loading_bar(width: int = 30) -> str:
        progress = (time.time() % 2) / 2
        filled_width = int(width * progress)
        bar = "█" * filled_width + "░" * (width - filled_width)
        return f"[{bar}]"
    
    @staticmethod
    def create_marquee(text: str, width: int = 50) -> str:
        offset = int(time.time() * 2) % (len(text) + width)
        if offset < len(text):
            return text[offset:offset + width].ljust(width)
        else:
            return " " * (offset - len(text)) + text[:width - (offset - len(text))]
    
    @staticmethod
    def create_wave_text(text: str, amplitude: float = 2.0, frequency: float = 1.0) -> str:
        result = ""
        for i, char in enumerate(text):
            if char == " ":
                result += char
            else:
                wave_offset = int(amplitude * math.sin(time.time() * frequency + i * 0.5))
                result += " " * abs(wave_offset) + char
        return result
    
    @staticmethod
    def create_bouncing_text(text: str, height: int = 3) -> str:
        bounce_pos = int(height * abs(math.sin(time.time() * 2)))
        return " " * bounce_pos + text
    
    @staticmethod
    def create_rotating_text(text: str, rotation_speed: float = 1.0) -> str:
        rotation = int(time.time() * rotation_speed) % len(text)
        return text[rotation:] + text[:rotation] 