import os
import re
import argparse
import shutil
import pefile

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


def export_files_imports(files_dir, output_dir, amount=None, malware=False):
    """
        Extrai features dos arquivos executáveis.
    """
    # for directory in outputdir:
    # print(f"Processing: {directory}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(files_dir)
    
    files_len = len(files)

    if files_len == 0:
        print('No files to export function imports.')
        sys.exit(1)


    if amount != None:
        # print(f'\t amount = {amount}. Selecionando arquivos...')
        if len(files) < amount:     # Check if there are enough files in the folder
            print(f'Error: Not enough files in {files_dir} (expected amount is {amount} but found only {len(files)})')
            return -1

        if amount == 0:
            print('No files processed, amount = 0.')
            return

        files = sorted(files)[:amount]  
        # print(f'\t arquivos selecionados: {len(files)}')      

    prefix = "R" if malware else "G"
    for file in files:
        if os.path.exists(f'{output_dir}/{prefix}-{file}'):
            continue

        try:
            pe = pefile.PE(f'{files_dir}/{file}')
            fname = file.split('-',1) # específico para o dataset que contém g- ou r- como prefixo
            with open(f'{output_dir}/{prefix}-{fname[1]}', 'w') as f:
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    for function in entry.imports:
                        if function.name != None:
                            f.write(f'{entry.dll.decode().lower()} {function.name.decode()}\n')

        except AttributeError:
            print(f'{file} does not have imports.')

        except pefile.PEFormatError:
            print(f'{file} may not be a PE file.')