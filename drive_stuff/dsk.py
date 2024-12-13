'''
Drive Space Analyzer

A tool for analyzing and displaying drive space information with visual progress bars
and color-coded warnings.


    Features
    -----------------------
    - Multi-drive analysis
    - CLI interface
    -----------------------


    CLI Arguments
    ---------------------------------------
    -all:        Show all available drives
    -C, -D...:   Specific drive letters
    ---------------------------------------


    Examples
    -----------------------------------
    >>> from dsk import get_drive_info
    >>> drives = get_drive_info(['C'])
    >>> print(drives)
    ['C:']

    # CLI Usage
    $ python dsk.py -all
    $ python dsk.py -C -D
    -----------------------------------
'''

#!global
from typing import List, Optional
from colorama import Fore, Style
from pathlib import Path
import platform
import argparse
import shutil
import sys
import os

sys.path.append(str(Path(__file__).parent.parent)) # parent path access

#!local
from formatting_utils import (
    formatter,
    SUCCESS_COLOR,
    ERROR_COLOR,
    INFO_COLOR,
    WARNING_COLOR,
    ACCENT_COLOR
)


#############################################################################################

# drive configuration
DRIVE_LETTERS: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # all possible Windows drive letters

# usage thresholds (percentage)
CRITICAL_THRESHOLD: float = 90.0                   # red warning level
WARNING_THRESHOLD: float = 70.0                    # yellow warning level

#############################################################################################


def get_drive_info(specific_drives: Optional[List[str]] = None) -> List[str]:
    '''
    Get information about specified drives or current drive

        Parameters
        ----------------------------------------------------------------------
         specific_drives (Optional[List[str]]):
                                               ===============
                                                default: None
                                               ===============
                                             
                                               List of drive letters to check
        ----------------------------------------------------------------------


        Returns
        --------------------------------------
         List[str]: List of valid drive paths
        --------------------------------------
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
        ------------------------------------------
         List[str]: List of all valid drive paths
        ------------------------------------------
    '''

    if platform.system() == "Windows":
        # check every possible drive letter
        return [f"{letter}:" for letter in DRIVE_LETTERS
                if os.path.exists(f"{letter}:")]
    else:
        return ['/']  # unix systems just use root


def bytes_to_gb(bytes_val: int) -> float:
    '''
    Convert bytes to gigabytes

        Parameters
        ---------------------------------------------
         bytes_val (int): Number of bytes to convert
        ---------------------------------------------


        Returns
        ---------------------------------------------
         float: Size in gigabytes (2 decimal places)
        ---------------------------------------------
    '''
    return round(bytes_val / (1024 ** 3), 2)


def format_drive_info(drive: str) -> List[str]:
    '''
    Format drive information with colors and progress bars

        Parameters
        -------------------------------------------------
         drive (str): Drive path to analyze (e.g., "C:")
        -------------------------------------------------


        Returns
        ---------------------------------------
         List[str]: Formatted drive info lines
        ---------------------------------------


        Raises
        -----------------------------------
         OSError: If drive is inaccessible
        -----------------------------------

        
        Examples
        ------------------------------------
         >>> info = format_drive_info("C:")
         >>> for line in info:
         ...     print(line)
         Drive C:
         ├─ Total: 500.00 GB
         ├─ Used:  250.00 GB
         └─ Free:  250.00 GB
         [██████████░░░░░░░░]
        ------------------------------------
    '''
    
    try:
        # grab the drive stats
        total, used, free = shutil.disk_usage(drive)
        
        # figure out how full the drive is
        used_percent = (used / total) * 100
        progress = formatter.get_progress_bar(used_percent)
        
        # pick a color based on how full it is
        if used_percent >= CRITICAL_THRESHOLD:
            color = ERROR_COLOR
        elif used_percent >= WARNING_THRESHOLD:
            color = WARNING_COLOR
        else:
            color = SUCCESS_COLOR
        
        console_width = formatter.get_console_width()

        # build our tree structure with aligned colons
        drive_line = f"{INFO_COLOR}Drive {drive}{Style.RESET_ALL}"
        total_line = formatter.create_tree_line(f"Total:   {ACCENT_COLOR}{formatter.format_size(total)}{Style.RESET_ALL}", "first")
        used_line = formatter.create_tree_line(f"Used:    {WARNING_COLOR}{formatter.format_size(used)}{Style.RESET_ALL}", "middle")
        free_line = formatter.create_tree_line(f"Free:    {SUCCESS_COLOR}{formatter.format_size(free)}{Style.RESET_ALL}", "last")
        
        padding = (console_width - formatter.get_visible_length(total_line)) // 2
        left_padding = " " * padding

        # put it all together
        drive_info = [
            formatter.center_with_ansi(drive_line),
            formatter.center_with_ansi(total_line),
            formatter.center_with_ansi(used_line),
            formatter.center_with_ansi(free_line),
            formatter.center_with_ansi(f" {color}{progress}{Style.RESET_ALL}")
        ]
        
        return drive_info
    except:
        return [formatter.center_with_ansi(f"{ERROR_COLOR}Unable to access drive {drive}{Style.RESET_ALL}")]


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
        ----------------------
        $ python dsk.py -all
        $ python dsk.py -C -D
        ----------------------
    '''

    parser = argparse.ArgumentParser(description='Display drive space information')
    parser.add_argument('-all', action='store_true', 
                       help='Show information for all available drives')
    args, unknown = parser.parse_known_args()
    
    drive_letters = []
    if unknown:
        for arg in unknown:
            if arg.startswith('-') and len(arg) == 2:
                drive_letters.append(arg[1].upper())
    
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
    
    # Create header/footer using formatting utils
    header, footer = formatter.format_header_footer("=== Drive Space Information ===")
    print(f"\n{formatter.center_with_ansi(header)}\n")
    
    # show info for each drive
    for drive in drives:
        drive_info = format_drive_info(drive)
        for line in drive_info:
            print(line)
        print()  
    
    print(f"{formatter.center_with_ansi(footer)}\n")


if __name__ == "__main__":
    main()
