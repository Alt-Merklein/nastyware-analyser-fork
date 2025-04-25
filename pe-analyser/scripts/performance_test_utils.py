import os
import re
import argparse
import shutil

def valid_folder(folder_path):
    if not re.match(r'/.*/$', folder_path):
        raise argparse.ArgumentTypeError(f'Folder path must be in format /*/ but is {folder_path}')

    # Check is empty
    if not os.listdir(folder_path):
        raise argparse.ArgumentTypeError(f'Folder {folder_path} is empty')
        
    if not os.path.isdir(folder_path):
        raise argparse.ArgumentTypeError(f'{folder_path} is not a valid folder')

    return folder_path

def folder_exists(folder_path):
    if not os.path.isdir(folder_path):
        raise argparse.ArgumentTypeError(f'{folder_path} is not a valid folder')

    return folder_path

def format_new_malware(folder_path):
    # Check if the folder path is valid
    changed = 0
    if not os.path.isdir(folder_path):
        print(f'Error: {folder_path} is not a valid folder')
        return -1

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            if os.path.getsize(file_path) == 0:
                print(f'Removing empty file: {file}')
                os.remove(file_path)
                continue  
                
            if file.startswith('R-') and len(file) > 10:
                new_file_name = file[:9]
                new_file_path = os.path.join(folder_path, new_file_name)
                os.rename(file_path, new_file_path)
                changed += 1
        else:
            print(f'Skipping {file} as it is not a file')

    return changed

def copy_new_samples(new_samples_folder, destination_folders, amount):
    # Check if the folder path is valid
    if not os.path.isdir(new_samples_folder):
        print(f'Error: {new_samples_folder} is not a valid folder')
        return -1

    # Get all files in the folder
    files = os.listdir(new_samples_folder)

    # Check if there are enough files in the folder
    if len(files) < amount:
        print(f'Error: Not enough files in {new_samples_folder} (expected amount is {amount} but found only {len(files)})')
        return -1

    files = sorted(files)
    chosen_files = files[:amount]

    for i, file in enumerate(chosen_files):
        for folder in destination_folders:
            if not os.path.isdir(folder):
                print(f'Error: {folder} is not a valid folder')
                return -1

            # copy file to folder
            file_path = os.path.join(new_samples_folder, file)
            new_file_path = os.path.join(folder, file)
            shutil.copy(file_path, new_file_path)