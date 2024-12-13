'''
Formatting Utilities

A collection of formatting utilities for consistent CLI display across components.
Provides color coding, progress bars, and text alignment functionality.

Features
--------------------------
- ANSI color constants
- Text centering
- Progress bars
- Headers/footers
- Console width detection
--------------------------
'''

#!globals
from colorama import init, Fore, Style
import shutil
import os


##############################################################
init(autoreset=True)                # autoreset on \n

# colorama console colors
SUCCESS_COLOR = Fore.LIGHTGREEN_EX
ERROR_COLOR = Fore.LIGHTRED_EX
INFO_COLOR = Fore.LIGHTCYAN_EX
WARNING_COLOR = Fore.LIGHTYELLOW_EX
ACCENT_COLOR = Fore.LIGHTBLUE_EX
##############################################################




class ConsoleFormatter:
    '''Handles console formatting operations and styling'''
    
    @staticmethod
    def get_console_width() -> int:
        '''Get the current console width, fallback to 80 if unable to detect'''
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80

    @staticmethod
    def get_visible_length(text: str) -> int:
        '''Get the visible length of a string (excluding ANSI escape codes)'''
        # remove all ANSI escape sequences
        ansi_escape = '\033\\[(?:[0-9;]+)*[mGK]'
        import re
        clean_text = re.sub(ansi_escape, '', text)
        return len(clean_text)

    @staticmethod
    def center_with_ansi(text: str, width: int = None) -> str:
        '''Center text while properly handling ANSI color codes'''
        if width is None:
            width = ConsoleFormatter.get_console_width()
        visible_length = ConsoleFormatter.get_visible_length(text)
        padding = (width - visible_length) // 2
        return " " * padding + text

    @staticmethod
    def get_progress_bar(percentage: float, width: int = 20, fill: str = '█', empty: str = '░') -> str:
        '''
        Create a progress bar with the given percentage
            
            Parameters
               ------------------------------------------------------
                percentage (float): Percentage to display (0-100)

                width (int): 
                             =============
                              default: 20
                             =============

                             Width of the progress bar in characters 
                                                                    
                fill (str):
                             ============
                              default: █
                             ============
                           
                             Character for filled portion

                empty (str):
                             ============
                              default: ░
                             ============

                             Character for empty portion
               -------------------------------------------------------

        
            Returns
            -------------------
             int: Progress Bar
            -------------------
        '''

        filled = int(width * percentage / 100)
        bar = fill * filled + empty * (width - filled)
        return bar

    @staticmethod
    def format_header_footer(title: str, border_char: str = "=") -> tuple[str, str]:
        '''
        Create matching header and footer with title
        
            Parameters
            ------------------------------------------------
             title (str): Title text to display in header

             border_char (str):
                               ==============
                                default: "="
                               ==============

                               Character to use for borders  
            -------------------------------------------------


            Returns
            --------------------------------------------
             tuple[str, str]: Header and footer strings
            --------------------------------------------
        '''

        width = ConsoleFormatter.get_console_width()
        border = border_char * width
        header = f"{border}\n{ConsoleFormatter.center_with_ansi(title)}\n{border}"
        footer = border
        return header, footer

    @staticmethod
    def format_size(size_bytes: float, precision: int = 2) -> str:
        '''
        Format byte sizes into human readable format
        
            Parameters
            ------------------------------------------
             size_bytes (float): Size in bytes

             precision (int):
                             ============
                              default: 2
                             ============

                             Number of decimal places
            -------------------------------------------


            Returns
            -----------------------
             str: byte size format
            -----------------------
        '''
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.{precision}f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.{precision}f} PB"

    @staticmethod
    def format_size_simple(size_bytes: float) -> str:
        '''
        Format byte sizes into human readable format with rounded numbers
        
            Parameters
            ------------------------------------------
             size_bytes (float): Size in bytes
            ------------------------------------------


            Returns
            -----------------------
             str: byte size format
            -----------------------
        '''
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{int(round(size_bytes))} {unit}"
            size_bytes /= 1024.0
        return f"{int(round(size_bytes))} PB"

    @staticmethod
    def create_tree_line(text: str, line_type: str = "middle") -> str:
        '''
        Create a tree-style line with proper formatting
        
            Parameters
            -------------------------------------------------------------
             text (str): Text to display

             line_type (str): Type of line ('first' | 'middle' | 'last')
            -------------------------------------------------------------
            
            
            Returns
            ---------------------------
            str: The associated symbol
            ---------------------------
        '''

        symbols = {
            "first": "├─",
            "middle": "├─",
            "last": "└─"
        }
        symbol = symbols.get(line_type, "├─")
        return f"{ERROR_COLOR}{symbol}{Style.RESET_ALL} {text}"

# Create a global formatter instance for easy access
formatter = ConsoleFormatter()

# For backwards compatibility
get_console_width = formatter.get_console_width
get_visible_length = formatter.get_visible_length
center_with_ansi = formatter.center_with_ansi
get_progress_bar = formatter.get_progress_bar
format_header_footer = formatter.format_header_footer