'''
Recycle Bin Manager

A tool for managing and emptying the recycle bin/trash across different operating systems
with safety checks and progress feedback.

    Features
    -----------------------------
    - Cross-platform support
    - Safe deletion verification
    - Progress feedback
    - Error handling
    -----------------------------


    CLI Arguments
    ------------------------------------------
    - e:         Empty the recycle bin
    - i:         Show recycle bin information
    ------------------------------------------


    Examples
    ------------------------------------------------
     >>> from recycle import empty_recycle_bin
     >>> empty_recycle_bin(skip_confirmation=False)
    
     # CLI Usage
     $ python recycle.py -empty
     $ python recycle.py -info
    -----------------------------------------------
'''

#!global
from typing import Tuple, List
from colorama import Style
from pathlib import Path
import platform
import argparse
import shutil
import ctypes
import sys
import os

sys.path.append(str(Path(__file__).parent.parent))  # parent path access

#!local
from formatting_utils import (
    formatter,
    SUCCESS_COLOR,
    ERROR_COLOR,
    INFO_COLOR,
    ACCENT_COLOR
)


#############################################################################################

# windows recycle bin stuff
RECYCLE_BIN_PATH: str = "$Recycle.Bin"        # where windows keeps the deleted files
EMPTY_FLAGS: int = 0                          # just tells windows to do it normally
EMPTY_SUCCESS: int = 0                        # windows returns this when all good

# trash locations for different systems
MAC_TRASH: str = "~/.Trash"                   # mac keeps it simple
LINUX_TRASH: str = "~/.local/share/Trash"     # linux hides it deep
LINUX_SUBDIRS: List[str] = ['files', 'info']  # linux needs two folders for some reason

# size conversion
BYTES_TO_MB: int = 1024 * 1024                # converting bytes to mb, cause who uses bytes

#############################################################################################


def get_system_type() -> str:
    '''
    Determine the operating system type
    
        Returns
        ----------------------------------
         str: Operating system identifier
        ----------------------------------
    '''

    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def get_recycle_bin_size() -> Tuple[float, int]:
    '''
    Get the size and item count of the recycle bin

        Returns
        --------------------------------------------------------
         Tuple[float, int]: (total size in MB, number of items)
        --------------------------------------------------------


        Raises
        -------------------------------------
         OSError: If access is denied
         RuntimeError: If system unsupported
        -------------------------------------
    '''

    system: str = get_system_type()         # figure out what os we're dealing with
    total_size: float = 0                   # keeps track of how much junk we find
    item_count: int = 0                     # counts how many things are in the bin

    try:
        if system == "windows":
            # grab all the drives that actually exist
            drives: List[str] = [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
                               if os.path.exists(f"{d}:")]
            for drive in drives:
                recycle_path: str = os.path.join(drive, RECYCLE_BIN_PATH)
                if os.path.exists(recycle_path):
                    # count up all the bad files
                    for root, _, files in os.walk(recycle_path):
                        item_count += len(files)
                        total_size += sum(os.path.getsize(os.path.join(root, f)) 
                                        for f in files)

        elif system == "macos":
            # mac is pretty simple, - one trash folder
            trash_path: str = os.path.expanduser(MAC_TRASH)
            for root, dirs, files in os.walk(trash_path):
                item_count += len(files) + len(dirs)
                total_size += sum(os.path.getsize(os.path.join(root, f)) 
                                for f in files)

        elif system == "linux":
            # linux hides the trash in a weird spot
            trash_path: str = os.path.expanduser(LINUX_TRASH)
            for root, dirs, files in os.walk(trash_path):
                item_count += len(files) + len(dirs)
                total_size += sum(os.path.getsize(os.path.join(root, f)) 
                                for f in files)

        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

        return (total_size / BYTES_TO_MB, item_count)  # convert to MB cause bytes are huge

    except PermissionError:
        raise OSError("Access denied to recycle bin")
    except Exception as e:
        raise RuntimeError(f"Error accessing recycle bin: {str(e)}")


def empty_recycle_bin() -> bool:
    '''
    Empty the recycle bin/trash without confirmation

        Returns
        -------------------------------------------
         bool: True if successful, False otherwise
        -------------------------------------------


        Raises
        -------------------------------------
         OSError: If permission denied
         RuntimeError: If system unsupported
        -------------------------------------
    '''

    system: str = get_system_type()

    try:
        if system == "windows":
            # windows needs some fancy dll calls
            result: int = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, EMPTY_FLAGS)
            if result != EMPTY_SUCCESS:
                raise OSError(f"Failed to empty recycle bin: {result}")

        elif system == "macos":
            # mac cleanup is pretty straightforward
            trash_path: str = os.path.expanduser(MAC_TRASH)
            for item in os.listdir(trash_path):
                path: str = os.path.join(trash_path, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

        elif system == "linux":
            # linux needs to clean both files and their info
            trash_path: str = os.path.expanduser(LINUX_TRASH)
            for subdir in LINUX_SUBDIRS:
                path: str = os.path.join(trash_path, subdir)
                if os.path.exists(path):
                    for item in os.listdir(path):
                        item_path: str = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)

        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

        print(f"\n{SUCCESS_COLOR}Successfully emptied the recycle bin")
        return True

    except PermissionError:
        print(f"\n{ERROR_COLOR}Error: Access denied to recycle bin")
        return False
    except Exception as e:
        print(f"\n{ERROR_COLOR}Error emptying recycle bin: {str(e)}")
        return False


def display_recycle_info() -> None:
    '''
    Display information about the recycle bin contents
    '''
    try:
        size_mb, count = get_recycle_bin_size()
        
        header, footer = formatter.format_header_footer("=== Recycle Bin Information ===")
        
        print(f"\n{formatter.center_with_ansi(header)}\n")
        
        # Convert MB to bytes for the formatter
        size_bytes = size_mb * BYTES_TO_MB
        
        # Create the display lines with proper indentation and alignment
        drive_line = f"{INFO_COLOR}Recycle Bin{Style.RESET_ALL}"
        items_line = formatter.create_tree_line(f"Items:    {ACCENT_COLOR}{count}{Style.RESET_ALL}", "first")
        size_line = formatter.create_tree_line(f"Size:     {SUCCESS_COLOR}{formatter.format_size_simple(size_bytes)}{Style.RESET_ALL}", "last")
        
        # Calculate consistent padding
        console_width = formatter.get_console_width()
        max_line = max(items_line, size_line, key=formatter.get_visible_length)
        padding = (console_width - formatter.get_visible_length(max_line)) // 2
        left_padding = " " * padding
        
        # Print with consistent padding
        print(formatter.center_with_ansi(drive_line))
        print(f"{left_padding}{items_line}")
        print(f"{left_padding}{size_line}")
        print(f"\n{formatter.center_with_ansi(footer)}\n")

    except Exception as e:
        print(f"\n{ERROR_COLOR}Error getting recycle bin information: {str(e)}")


def main() -> None:
    '''
    Main entry point for the recycle bin manager

        CLI Arguments
        --------------------------------------
        - e:     Empty the recycle bin
        - i:     Show recycle bin information
        --------------------------------------


        Examples
        -----------------------
        $ python recycle.py -e
        $ python recycle.py -i
        -----------------------
    '''

    parser = argparse.ArgumentParser(description='Manage system recycle bin')
    
    parser.add_argument('-e', action='store_true', help='Empty the recycle bin')
    
    parser.add_argument('-i', action='store_true', help='Display recycle bin information')
    
    args = parser.parse_args()

    if not (args.e or args.i):
        parser.print_help()
        return

    try:
        if args.i:
            display_recycle_info()
        
        if args.e:
            empty_recycle_bin()

    except Exception as e:
        print(f"\n{ERROR_COLOR}An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    '''main execution loop'''
    main()
