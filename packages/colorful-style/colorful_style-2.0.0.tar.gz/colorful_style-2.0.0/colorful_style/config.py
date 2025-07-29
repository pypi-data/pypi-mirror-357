import json
import os
from typing import Any, Dict, Optional
from .colors import Colors
from .colorate import Colorate

class Config:
    
    _config_file = "colorful_style_config.json"
    _default_config = {
        "animations_enabled": True,
        "sound_enabled": False,
        "default_speed": 0.05,
        "default_duration": 2.0,
        "default_color": "blue",
        "terminal_width": 80,
        "terminal_height": 24,
        "auto_center": True,
        "auto_wrap": True,
        "show_cursor": True,
        "color_mode": "auto",
        "gradient_steps": 100,
        "glow_intensity": 0.8,
        "neon_intensity": 0.8,
        "sparkle_density": 0.3,
        "star_density": 0.2,
        "particle_count": 50,
        "fire_height": 10,
        "water_ripple_speed": 0.1,
        "matrix_speed": 0.05,
        "typing_speed": 0.05,
        "fade_steps": 20,
        "blink_times": 5,
        "bounce_height": 3,
        "wave_amplitude": 2.0,
        "wave_frequency": 1.0,
        "pulse_min_size": 0.8,
        "pulse_max_size": 1.2,
        "slide_duration": 2.0,
        "progress_bar_width": 50,
        "spinner_duration": 3.0,
        "countdown_seconds": 10,
        "menu_color": "cyan",
        "input_color": "cyan",
        "confirm_color": "yellow",
        "error_color": "red",
        "success_color": "green",
        "warning_color": "yellow",
        "info_color": "blue",
        "banner_font": "big",
        "box_style": "simple",
        "align_style": "center",
        "effect_style": "rainbow",
        "gradient_style": "rainbow",
        "animation_style": "typing",
        "theme": "default"
    }
    
    _config = _default_config.copy()
    
    @staticmethod
    def load_config():
        try:
            if os.path.exists(Config._config_file):
                with open(Config._config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    Config._config.update(loaded_config)
        except Exception as e:
            print(Colorate.Error(f"Lỗi tải cấu hình: {e}"))
    
    @staticmethod
    def save_config():
        try:
            with open(Config._config_file, 'w', encoding='utf-8') as f:
                json.dump(Config._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(Colorate.Error(f"Lỗi lưu cấu hình: {e}"))
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        return Config._config.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        Config._config[key] = value
        Config.save_config()
    
    @staticmethod
    def reset():
        Config._config = Config._default_config.copy()
        Config.save_config()
    
    @staticmethod
    def get_all() -> Dict[str, Any]:
        return Config._config.copy()
    
    @staticmethod
    def update(config_dict: Dict[str, Any]):
        Config._config.update(config_dict)
        Config.save_config()
    
    @staticmethod
    def enable_animations(enabled: bool = True):
        Config.set("animations_enabled", enabled)
    
    @staticmethod
    def disable_animations():
        Config.set("animations_enabled", False)
    
    @staticmethod
    def enable_sound(enabled: bool = True):
        Config.set("sound_enabled", enabled)
    
    @staticmethod
    def disable_sound():
        Config.set("sound_enabled", False)
    
    @staticmethod
    def set_default_speed(speed: float):
        Config.set("default_speed", speed)
    
    @staticmethod
    def set_default_duration(duration: float):
        Config.set("default_duration", duration)
    
    @staticmethod
    def set_default_color(color: str):
        Config.set("default_color", color)
    
    @staticmethod
    def set_terminal_size(width: int, height: int):
        Config.set("terminal_width", width)
        Config.set("terminal_height", height)
    
    @staticmethod
    def set_auto_center(enabled: bool):
        Config.set("auto_center", enabled)
    
    @staticmethod
    def set_auto_wrap(enabled: bool):
        Config.set("auto_wrap", enabled)
    
    @staticmethod
    def set_show_cursor(enabled: bool):
        Config.set("show_cursor", enabled)
    
    @staticmethod
    def set_color_mode(mode: str):
        if mode in ["auto", "always", "never"]:
            Config.set("color_mode", mode)
    
    @staticmethod
    def set_gradient_steps(steps: int):
        Config.set("gradient_steps", steps)
    
    @staticmethod
    def set_glow_intensity(intensity: float):
        Config.set("glow_intensity", intensity)
    
    @staticmethod
    def set_neon_intensity(intensity: float):
        Config.set("neon_intensity", intensity)
    
    @staticmethod
    def set_sparkle_density(density: float):
        Config.set("sparkle_density", density)
    
    @staticmethod
    def set_star_density(density: float):
        Config.set("star_density", density)
    
    @staticmethod
    def set_particle_count(count: int):
        Config.set("particle_count", count)
    
    @staticmethod
    def set_fire_height(height: int):
        Config.set("fire_height", height)
    
    @staticmethod
    def set_water_ripple_speed(speed: float):
        Config.set("water_ripple_speed", speed)
    
    @staticmethod
    def set_matrix_speed(speed: float):
        Config.set("matrix_speed", speed)
    
    @staticmethod
    def set_typing_speed(speed: float):
        Config.set("typing_speed", speed)
    
    @staticmethod
    def set_fade_steps(steps: int):
        Config.set("fade_steps", steps)
    
    @staticmethod
    def set_blink_times(times: int):
        Config.set("blink_times", times)
    
    @staticmethod
    def set_bounce_height(height: int):
        Config.set("bounce_height", height)
    
    @staticmethod
    def set_wave_amplitude(amplitude: float):
        Config.set("wave_amplitude", amplitude)
    
    @staticmethod
    def set_wave_frequency(frequency: float):
        Config.set("wave_frequency", frequency)
    
    @staticmethod
    def set_pulse_sizes(min_size: float, max_size: float):
        Config.set("pulse_min_size", min_size)
        Config.set("pulse_max_size", max_size)
    
    @staticmethod
    def set_slide_duration(duration: float):
        Config.set("slide_duration", duration)
    
    @staticmethod
    def set_progress_bar_width(width: int):
        Config.set("progress_bar_width", width)
    
    @staticmethod
    def set_spinner_duration(duration: float):
        Config.set("spinner_duration", duration)
    
    @staticmethod
    def set_countdown_seconds(seconds: int):
        Config.set("countdown_seconds", seconds)
    
    @staticmethod
    def set_menu_color(color: str):
        Config.set("menu_color", color)
    
    @staticmethod
    def set_input_color(color: str):
        Config.set("input_color", color)
    
    @staticmethod
    def set_confirm_color(color: str):
        Config.set("confirm_color", color)
    
    @staticmethod
    def set_error_color(color: str):
        Config.set("error_color", color)
    
    @staticmethod
    def set_success_color(color: str):
        Config.set("success_color", color)
    
    @staticmethod
    def set_warning_color(color: str):
        Config.set("warning_color", color)
    
    @staticmethod
    def set_info_color(color: str):
        Config.set("info_color", color)
    
    @staticmethod
    def set_banner_font(font: str):
        Config.set("banner_font", font)
    
    @staticmethod
    def set_box_style(style: str):
        Config.set("box_style", style)
    
    @staticmethod
    def set_align_style(style: str):
        Config.set("align_style", style)
    
    @staticmethod
    def set_effect_style(style: str):
        Config.set("effect_style", style)
    
    @staticmethod
    def set_gradient_style(style: str):
        Config.set("gradient_style", style)
    
    @staticmethod
    def set_animation_style(style: str):
        Config.set("animation_style", style)
    
    @staticmethod
    def set_theme(theme: str):
        Config.set("theme", theme)
    
    @staticmethod
    def get_theme_config(theme: str) -> Dict[str, Any]:
        themes = {
            "default": {
                "default_color": "blue",
                "menu_color": "cyan",
                "error_color": "red",
                "success_color": "green",
                "warning_color": "yellow",
                "info_color": "blue"
            },
            "dark": {
                "default_color": "white",
                "menu_color": "cyan",
                "error_color": "red",
                "success_color": "green",
                "warning_color": "yellow",
                "info_color": "blue"
            },
            "light": {
                "default_color": "black",
                "menu_color": "blue",
                "error_color": "red",
                "success_color": "green",
                "warning_color": "yellow",
                "info_color": "blue"
            },
            "neon": {
                "default_color": "cyan",
                "menu_color": "pink",
                "error_color": "red",
                "success_color": "green",
                "warning_color": "yellow",
                "info_color": "blue"
            },
            "rainbow": {
                "default_color": "rainbow",
                "menu_color": "rainbow",
                "error_color": "red",
                "success_color": "green",
                "warning_color": "yellow",
                "info_color": "blue"
            }
        }
        return themes.get(theme, themes["default"])
    
    @staticmethod
    def apply_theme(theme: str):
        theme_config = Config.get_theme_config(theme)
        Config.update(theme_config)
        Config.set_theme(theme)
    
    @staticmethod
    def print_config(color: str = Colors.cyan):
        print(Colorate.Color(color, "=== CẤU HÌNH COLORFUL STYLE ==="))
        for key, value in Config._config.items():
            print(Colorate.Color(color, f"{key}: {value}"))
    
    @staticmethod
    def export_config(filename: str = "colorful_style_export.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(Config._config, f, indent=2, ensure_ascii=False)
            print(Colorate.Success(f"Cấu hình đã được xuất ra {filename}"))
        except Exception as e:
            print(Colorate.Error(f"Lỗi xuất cấu hình: {e}"))
    
    @staticmethod
    def import_config(filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                Config.update(imported_config)
            print(Colorate.Success(f"Cấu hình đã được nhập từ {filename}"))
        except Exception as e:
            print(Colorate.Error(f"Lỗi nhập cấu hình: {e}"))
    
    @staticmethod
    def validate_config() -> bool:
        required_keys = ["animations_enabled", "sound_enabled", "default_speed"]
        for key in required_keys:
            if key not in Config._config:
                print(Colorate.Error(f"Thiếu cấu hình bắt buộc: {key}"))
                return False
        return True
    
    @staticmethod
    def repair_config():
        missing_keys = set(Config._default_config.keys()) - set(Config._config.keys())
        for key in missing_keys:
            Config._config[key] = Config._default_config[key]
        Config.save_config()
        print(Colorate.Success("Đã sửa chữa cấu hình"))
    
    @staticmethod
    def get_config_file_path() -> str:
        return os.path.abspath(Config._config_file)
    
    @staticmethod
    def backup_config():
        backup_file = f"{Config._config_file}.backup"
        try:
            with open(Config._config_file, 'r', encoding='utf-8') as f:
                config_data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(config_data)
            print(Colorate.Success(f"Đã sao lưu cấu hình vào {backup_file}"))
        except Exception as e:
            print(Colorate.Error(f"Lỗi sao lưu cấu hình: {e}"))
    
    @staticmethod
    def restore_config():
        backup_file = f"{Config._config_file}.backup"
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
                with open(Config._config_file, 'w', encoding='utf-8') as f:
                    f.write(backup_data)
                Config.load_config()
                print(Colorate.Success("Đã khôi phục cấu hình"))
            except Exception as e:
                print(Colorate.Error(f"Lỗi khôi phục cấu hình: {e}"))
        else:
            print(Colorate.Warning("Không tìm thấy file sao lưu"))

Config.load_config() 