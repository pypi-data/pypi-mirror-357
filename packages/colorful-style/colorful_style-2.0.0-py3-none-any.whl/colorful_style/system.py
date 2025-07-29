import os
import sys
import platform
import shutil
from typing import Tuple, Optional
from .colors import Colors
from .colorate import Colorate

class System:
    
    @staticmethod
    def init():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def title(title: str):
        if os.name == 'nt':
            os.system(f'title {title}')
        else:
            sys.stdout.write(f"\x1b]2;{title}\x07")
    
    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        try:
            return shutil.get_terminal_size()
        except:
            return (80, 24)
    
    @staticmethod
    def get_platform() -> str:
        return platform.system()
    
    @staticmethod
    def get_platform_version() -> str:
        return platform.version()
    
    @staticmethod
    def get_architecture() -> str:
        return platform.machine()
    
    @staticmethod
    def get_python_version() -> str:
        return platform.python_version()
    
    @staticmethod
    def is_windows() -> bool:
        return os.name == 'nt'
    
    @staticmethod
    def is_linux() -> bool:
        return os.name == 'posix' and platform.system() == 'Linux'
    
    @staticmethod
    def is_macos() -> bool:
        return os.name == 'posix' and platform.system() == 'Darwin'
    
    @staticmethod
    def supports_colors() -> bool:
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    @staticmethod
    def supports_unicode() -> bool:
        return sys.stdout.encoding.lower() in ('utf-8', 'utf8')
    
    @staticmethod
    def get_encoding() -> str:
        return sys.stdout.encoding
    
    @staticmethod
    def pause():
        if System.is_windows():
            os.system('pause')
        else:
            input(Colorate.Color(Colors.cyan, "Nhấn Enter để tiếp tục..."))
    
    @staticmethod
    def beep():
        if System.is_windows():
            import winsound
            winsound.Beep(1000, 500)
        else:
            print('\a', end='', flush=True)
    
    @staticmethod
    def bell():
        print('\a', end='', flush=True)
    
    @staticmethod
    def hide_cursor():
        print('\033[?25l', end='', flush=True)
    
    @staticmethod
    def show_cursor():
        print('\033[?25h', end='', flush=True)
    
    @staticmethod
    def save_cursor_position():
        print('\033[s', end='', flush=True)
    
    @staticmethod
    def restore_cursor_position():
        print('\033[u', end='', flush=True)
    
    @staticmethod
    def move_cursor_up(lines: int = 1):
        print(f'\033[{lines}A', end='', flush=True)
    
    @staticmethod
    def move_cursor_down(lines: int = 1):
        print(f'\033[{lines}B', end='', flush=True)
    
    @staticmethod
    def move_cursor_forward(columns: int = 1):
        print(f'\033[{columns}C', end='', flush=True)
    
    @staticmethod
    def move_cursor_backward(columns: int = 1):
        print(f'\033[{columns}D', end='', flush=True)
    
    @staticmethod
    def set_cursor_position(row: int, column: int):
        print(f'\033[{row};{column}H', end='', flush=True)
    
    @staticmethod
    def clear_line():
        print('\033[K', end='', flush=True)
    
    @staticmethod
    def clear_screen():
        print('\033[2J', end='', flush=True)
    
    @staticmethod
    def clear_screen_from_cursor():
        print('\033[J', end='', flush=True)
    
    @staticmethod
    def clear_screen_to_cursor():
        print('\033[1J', end='', flush=True)
    
    @staticmethod
    def get_system_info() -> dict:
        return {
            'platform': System.get_platform(),
            'version': System.get_platform_version(),
            'architecture': System.get_architecture(),
            'python_version': System.get_python_version(),
            'encoding': System.get_encoding(),
            'supports_colors': System.supports_colors(),
            'supports_unicode': System.supports_unicode(),
            'terminal_size': System.get_terminal_size()
        }
    
    @staticmethod
    def print_system_info(color: str = Colors.cyan):
        info = System.get_system_info()
        
        print(Colorate.Color(color, "=== THÔNG TIN HỆ THỐNG ==="))
        print(Colorate.Color(color, f"Hệ điều hành: {info['platform']} {info['version']}"))
        print(Colorate.Color(color, f"Kiến trúc: {info['architecture']}"))
        print(Colorate.Color(color, f"Python: {info['python_version']}"))
        print(Colorate.Color(color, f"Encoding: {info['encoding']}"))
        print(Colorate.Color(color, f"Hỗ trợ màu sắc: {'Có' if info['supports_colors'] else 'Không'}"))
        print(Colorate.Color(color, f"Hỗ trợ Unicode: {'Có' if info['supports_unicode'] else 'Không'}"))
        print(Colorate.Color(color, f"Kích thước terminal: {info['terminal_size'][0]}x{info['terminal_size'][1]}"))
    
    @staticmethod
    def check_dependencies() -> dict:
        dependencies = {
            'colorama': False,
            'termcolor': False,
            'rich': False,
            'pyfiglet': False,
            'art': False,
            'blessed': False,
            'cursor': False
        }
        
        try:
            import colorama
            dependencies['colorama'] = True
        except ImportError:
            pass
        
        try:
            import termcolor
            dependencies['termcolor'] = True
        except ImportError:
            pass
        
        try:
            import rich
            dependencies['rich'] = True
        except ImportError:
            pass
        
        try:
            import pyfiglet
            dependencies['pyfiglet'] = True
        except ImportError:
            pass
        
        try:
            import art
            dependencies['art'] = True
        except ImportError:
            pass
        
        try:
            import blessed
            dependencies['blessed'] = True
        except ImportError:
            pass
        
        try:
            import cursor
            dependencies['cursor'] = True
        except ImportError:
            pass
        
        return dependencies
    
    @staticmethod
    def print_dependencies_status(color: str = Colors.cyan):
        deps = System.check_dependencies()
        
        print(Colorate.Color(color, "=== TRẠNG THÁI DEPENDENCIES ==="))
        for dep, status in deps.items():
            status_text = "✓ Cài đặt" if status else "✗ Chưa cài đặt"
            status_color = Colors.green if status else Colors.red
            print(Colorate.Color(status_color, f"{dep}: {status_text}"))
    
    @staticmethod
    def install_missing_dependencies():
        deps = System.check_dependencies()
        missing = [dep for dep, status in deps.items() if not status]
        
        if not missing:
            print(Colorate.Success("Tất cả dependencies đã được cài đặt!"))
            return
        
        print(Colorate.Warning(f"Cần cài đặt: {', '.join(missing)}"))
        
        if System.confirm("Bạn có muốn cài đặt các dependencies còn thiếu không?"):
            try:
                import subprocess
                for dep in missing:
                    print(Colorate.Info(f"Đang cài đặt {dep}..."))
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(Colorate.Success("Cài đặt hoàn tất!"))
            except Exception as e:
                print(Colorate.Error(f"Lỗi cài đặt: {e}"))
    
    @staticmethod
    def confirm(message: str) -> bool:
        response = input(Colorate.Color(Colors.yellow, f"{message} (y/N): ")).lower().strip()
        return response in ['y', 'yes', '1', 'true']
    
    @staticmethod
    def get_input(prompt: str, color: str = Colors.cyan) -> str:
        return input(Colorate.Color(color, prompt))
    
    @staticmethod
    def print_separator(char: str = "=", length: int = 50, color: str = Colors.cyan):
        separator = char * length
        print(Colorate.Color(color, separator))
    
    @staticmethod
    def print_header(title: str, color: str = Colors.yellow):
        System.print_separator("=", len(title) + 4, color)
        print(Colorate.Color(color, f"  {title}  "))
        System.print_separator("=", len(title) + 4, color)
    
    @staticmethod
    def print_footer(color: str = Colors.cyan):
        System.print_separator("-", 50, color)
    
    @staticmethod
    def wait(seconds: float):
        import time
        time.sleep(seconds)
    
    @staticmethod
    def exit_with_message(message: str, color: str = Colors.red):
        print(Colorate.Color(color, message))
        System.pause()
        sys.exit(0)
    
    @staticmethod
    def safe_exit():
        System.show_cursor()
        sys.exit(0) 