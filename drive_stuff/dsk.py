'''
    Drive Space Analyzer

    A tool for analyzing and displaying drive space information with visual progress bars
    and color-coded warnings.


    Features
    -----------------------------
    - Multi-drive analysis
    - CLI interface
    -----------------------------


    CLI Arguments
    ---------------------------------------
    -all:        Show all available drives
    -C, -D...:   Specific drive letters
    ---------------------------------------


    Examples
    -------------------------------------------
    >>> from dsk import get_drive_info
    >>> drives = get_drive_info(['C'])
    >>> print(drives)
    ['C:']

    # CLI Usage
    $ python dsk.py -all
    $ python dsk.py -C -D
    -------------------------------------------
'''

import shutil
import os
from colorama import init, Fore, Style
import platform
import argparse
import re
from typing import List, Tuple, Optional

# these are the visual elements we use to make things pretty
PROGRESS_BAR_FILLED: str = '█'  
PROGRESS_BAR_EMPTY: str = '░'   

# all the possible letters a windows drive could have
DRIVE_LETTERS: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  

# if we can't figure out how wide the terminal is, we'll use this
DEFAULT_CONSOLE_WIDTH: int = 80  

# when to start tweaking out about drive space
CRITICAL_THRESHOLD: float = 90.0  
WARNING_THRESHOLD: float = 70.0   


def get_drive_info(specific_drives: Optional[List[str]] = None) -> List[str]:
    '''
        Get information about specified drives or current drive

        Parameters
        ---------------------------------------------------------------------
        specific_drives (Optional[List[str]]):
                                            ===============
                                            default: None
                                            ===============
                                            
                                            List of drive letters to check
        ---------------------------------------------------------------------


        Returns
        -------------------------------------
        List[str]: List of valid drive paths
        -------------------------------------


        Features
        ------------------------------------------
        - Windows/Unix compatible
        - Validates drive existence
        - Returns current drive if none specified
        ------------------------------------------
    '''
    if platform.system() == "Windows":
        if specific_drives:
            # check if the drives actually exist before we try to use them
            drives = [f"{letter.upper()}:" for letter in specific_drives 
                     if os.path.exists(f"{letter.upper()}:")]
        else:
            # just use whatever drive we're currently on
            drives = [os.getcwd()[:2]]
        return drives
    else:
        return ['/']  # unix systems just use root


def get_all_drives() -> List[str]:
    '''
        Get all available drives on the system

        Returns
        -----------------------------------------
        List[str]: List of all valid drive paths
        -----------------------------------------


        Features
        --------------------------
        - Windows/Unix compatible
        - Checks drive existence
        - Returns root for Unix
        --------------------------
    '''
    if platform.system() == "Windows":
        # check every possible drive letter
        return [f"{letter}:" for letter in DRIVE_LETTERS
                if os.path.exists(f"{letter}:")]
    else:
        return ['/']


def bytes_to_gb(bytes_val: int) -> float:
    '''
        Convert bytes to gigabytes

        Parameters
        --------------------------------------------
        bytes_val (int): Number of bytes to convert
        --------------------------------------------


        Returns
        --------------------------------------------
        float: Size in gigabytes (2 decimal places)
        --------------------------------------------
    '''
    return round(bytes_val / (1024 ** 3), 2)


def get_progress_bar(percentage: float, width: int = 20) -> str:
    '''
        Generate a visual progress bar

        Parameters
        --------------------------------------------------
        percentage (float): Percentage to display (0-100)
        width (int):    
                    ================
                    default: 20
                    ================
                        
                    Width of progress bar in characters
        --------------------------------------------------


        Returns
        ------------------------------------------------
        str: Visual progress bar using block characters
        ------------------------------------------------
    '''
    filled = int(width * percentage / 100)
    return PROGRESS_BAR_FILLED * filled + PROGRESS_BAR_EMPTY * (width - filled)


def get_visible_length(string: str) -> int:
    '''
        Calculate visible length of string with ANSI escape codes

        Parameters
        -------------------------------------------------------
        string (str): String potentially containing ANSI codes
        -------------------------------------------------------


        Returns
        ---------------------------------------
        int: Visible length without ANSI codes
        ---------------------------------------


        Features
        --------------------------------
        - Handles ANSI color codes
        - Accurate string length
        - Supports all escape sequences
        --------------------------------
    '''
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return len(ansi_escape.sub('', string))


def center_with_ansi(string: str, width: int) -> str:
    '''
        Center text with ANSI codes in given width

        Parameters
        ------------------------------------------------------
        string (str): Text to center (may contain ANSI codes)
        width (int): Total width to center within
        ------------------------------------------------------


        Returns
        -----------------------------------------
        str: Centered string with proper spacing
        -----------------------------------------


        Features
        ----------------------------
        - Preserves ANSI formatting
        - Accurate visual centering
        - Handles color codes
        ----------------------------


        Examples
        -----------------------------------------------
        >>> text = f"{Fore.RED}Hello{Style.RESET_ALL}"
        >>> print(center_with_ansi(text, 20))
        "       Hello       "
        -----------------------------------------------
    '''
    visible_length = get_visible_length(string)
    padding = (width - visible_length) // 2
    return " " * padding + string


def align_tree_info(string: str, width: int, tree_indent: int = 20) -> str:
    '''
        Align tree-structured drive information

        Parameters
        ------------------------------------------------------
        string (str): Tree-formatted string to align
        width (int): Total width to align within
        tree_indent (int):
                        ================
                        default: 20
                        ================
                        
                        Base indentation for tree structure
        ------------------------------------------------------


        Returns
        -----------------------------------
        str: Aligned tree-formatted string
        -----------------------------------


        Features
        ---------------------------
        - Handles tree symbols (├, └)
        - Preserves ANSI formatting
        - Smart alignment detection
        ---------------------------
    '''
    # strip out the ansi codes to get true length
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    visible_length = len(ansi_escape.sub('', string))
    
    # find where our tree starts (could be any of these symbols)
    tree_start = string.find('├')
    if tree_start == -1:
        tree_start = string.find('└')
    if tree_start == -1:
        tree_start = string.find('Drive')
    
    # if we found a tree structure, align it properly
    if tree_start != -1:
        before_tree = string[:tree_start]
        tree_part = string[tree_start:]
        
        total_padding = (width - visible_length) // 2
        return " " * total_padding + tree_part
    
    return " " * ((width - visible_length) // 2) + string


def format_drive_info(drive: str) -> List[str]:
    '''
        Format drive information with colors and progress bars

        Parameters
        ------------------------------------------------
        drive (str): Drive path to analyze (e.g., "C:")
        ------------------------------------------------


        Returns
        --------------------------------------
        List[str]: Formatted drive info lines
        --------------------------------------


        Raises
        ----------------------------------
        OSError: If drive is inaccessible
        ----------------------------------


        Features
        -----------------------------
        - Color-coded usage warnings
        - Visual progress bars
        - Tree-structured output
        - Size in gigabytes
        -----------------------------


        Examples
        -----------------------------------
        >>> info = format_drive_info("C:")
        >>> for line in info:
        ...     print(line)
        Drive C:
        ├─ Total: 500.00 GB
        ├─ Used:  250.00 GB
        └─ Free:  250.00 GB
        [██████████░░░░░░░░]
        -----------------------------------
    '''
    try:
        # grab the drive stats
        total, used, free = shutil.disk_usage(drive)
        
        # convert everything to gigabytes (easier to read)
        total_gb = bytes_to_gb(total)
        used_gb = bytes_to_gb(used)
        free_gb = bytes_to_gb(free)
        
        # figure out how full the drive is
        used_percent = (used / total) * 100
        progress = get_progress_bar(used_percent)
        
        # pick a color based on how full it is
        if used_percent >= CRITICAL_THRESHOLD:
            color = Fore.RED  # no space tbh
        elif used_percent >= WARNING_THRESHOLD:
            color = Fore.YELLOW  # getting a bit full
        else:
            color = Fore.GREEN  # plenty of space
        
        # try to make it look nice in the terminal
        try:
            console_width = os.get_terminal_size().columns
        except:
            console_width = DEFAULT_CONSOLE_WIDTH

        # line everything up nicely
        total_str = f"{total_gb:.2f}".rjust(8)
        used_str = f"{used_gb:.2f}".rjust(8)
        free_str = f"{free_gb:.2f}".rjust(8)

        # build our tree structure
        drive_line = f"{Fore.CYAN}Drive {drive}{Style.RESET_ALL}"
        total_line = f"{Fore.LIGHTRED_EX}├─{Fore.RESET}  Total: {Fore.BLUE}{total_str} GB{Style.RESET_ALL}"
        used_line = f"{Fore.LIGHTRED_EX}├─{Fore.RESET}   Used: {Fore.YELLOW}{used_str} GB{Style.RESET_ALL}"
        free_line = f"{Fore.LIGHTRED_EX}└─{Fore.RESET}   Free: {Fore.GREEN}{free_str} GB{Style.RESET_ALL}"
        
        padding = (console_width - get_visible_length(total_line)) // 2
        left_padding = " " * padding

        # put it all together
        drive_info = [
            center_with_ansi(drive_line, console_width),
            f"{left_padding}{total_line}",
            f"{left_padding}{used_line}",
            f"{left_padding}{free_line}",
            center_with_ansi(f"{color}{progress}{Style.RESET_ALL}", console_width)
        ]
        
        return drive_info
    except:
        # something went wrong, let the user know
        return [center_with_ansi(f"{Fore.RED}Unable to access drive {drive}{Style.RESET_ALL}", console_width)]


def main() -> None:
    '''
        Main entry point for the drive space analyzer

        Features
        -------------------------------
        - Parse CLI arguments
        - Display formatted drive info
        - Color-coded output
        - Centered display
        -------------------------------


        CLI Arguments
        --------------------------------------
        -all:       Show all available drives
        -C, -D...:  Check specific drives
        --------------------------------------


        Examples
        ------------------------------
        $ python dsk.py -all
        $ python dsk.py -C -D
        ------------------------------
    '''
    init()
    
    # set up our argument parser for command line use
    parser = argparse.ArgumentParser(description='Display drive space information')
    parser.add_argument('-all', action='store_true', 
                       help='Show information for all available drives')
    args, unknown = parser.parse_known_args()
    
    # handle any drive letters the user specified
    drive_letters = []
    if unknown:
        for arg in unknown:
            if arg.startswith('-') and len(arg) == 2:
                drive_letters.append(arg[1].upper())
    
    # figure out which drives we're gonna look at
    if args.all:
        drives = get_all_drives()
    elif drive_letters:
        drives = [f"{letter}:" for letter in drive_letters 
                 if os.path.exists(f"{letter}:")]
        if not drives:
            print(f"{Fore.YELLOW}No valid drives specified. Use: -C -D -E etc.{Style.RESET_ALL}")
            return
    else:
        drives = get_drive_info()
    
    # try to make things look nice in the terminal
    try:
        console_width = os.get_terminal_size().columns
    except:
        console_width = DEFAULT_CONSOLE_WIDTH  
    
    # more of making it look nice
    header = "=== Drive Space Information ==="
    colored_header = f"{Fore.CYAN}{header}{Style.RESET_ALL}"
    print(f"\n{center_with_ansi(colored_header, console_width)}\n")
    
    # show info for each drive
    for drive in drives:
        drive_info = format_drive_info(drive)
        for line in drive_info:
            print(line)
        print()  
    
    # wrap it up nicely
    footer = "=" * len(header)
    colored_footer = f"{Fore.CYAN}{footer}{Style.RESET_ALL}"
    print(f"\n{center_with_ansi(colored_footer, console_width)}\n")


if __name__ == "__main__":
    main()
