import os
import re
import argparse
import shutil
import pefile
import pathlib
from concurrent.futures import ProcessPoolExecutor

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

def _core_name(basename: str) -> str:
    """Remove o prefixo original (g- ou r-) se existir."""
    # Regex: início de string, g ou r (maiúsc/min), hífen, depois qualquer coisa
    return re.sub(r'^[grGR]-', '', basename, count=1)

def _extract_one(task):
    file_path, prefix = task
    try:
        pe = pefile.PE(file_path, fast_load=True)
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']]
        )
        lines = [
            f"{entry.dll.decode().lower()} {imp.name.decode()}"
            for entry in pe.DIRECTORY_ENTRY_IMPORT
            for imp in entry.imports if imp.name
        ]
        basename = os.path.basename(file_path)
        core     = _core_name(basename)        
        return f"{prefix}-{core}", "\n".join(lines) + "\n"
    except (AttributeError, pefile.PEFormatError):
        return None

max_workers = max(4, min(32, os.cpu_count() * 2))

def export_files_imports(src_dir, out_dir, amount=None, malware=False, n_jobs=max_workers):
    src_dir  = pathlib.Path(src_dir)
    out_dir  = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prefix   = "R" if malware else "G"
    files    = sorted(src_dir.iterdir())
    if amount: files = files[:amount]

    tasks = []
    for f in files:
        core_name  = _core_name(f.name)          # ← AQUI
        final_name = f"{prefix}-{core_name}"
        if (out_dir / final_name).exists():
            continue
        tasks.append((str(f), prefix))

    if not tasks:
        print("Nenhum arquivo novo para extrair.")
        return

    n_jobs = n_jobs or max(1, os.cpu_count() - 1)
    with ProcessPoolExecutor(max_workers=n_jobs) as ex:
        for res in ex.map(_extract_one, tasks, chunksize=64):
            if res is None:
                continue
            final_name, blob = res
            with open(out_dir / final_name, "w") as fo:
                fo.write(blob)
