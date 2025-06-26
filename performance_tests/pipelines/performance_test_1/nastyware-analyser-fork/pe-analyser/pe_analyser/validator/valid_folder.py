import os
import re
import argparse

def valid_folder(folder_path):
    if not re.match(r'/.*/$', folder_path):
        raise argparse.ArgumentTypeError(f'Folder path must be in format /*/ but is {folder_path}')

    # Check is empty
    if not os.listdir(folder_path):
        raise argparse.ArgumentTypeError(f'Folder {folder_path} is empty')
        
    if not os.path.isdir(folder_path):
        raise argparse.ArgumentTypeError(f'{folder_path} is not a valid folder')

    return folder_path