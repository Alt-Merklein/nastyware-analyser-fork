import os

def remove_empty_imports(imports_dir):
    for filename in os.listdir(imports_dir):
        if os.path.getsize(imports_dir + filename) < 40 or os.path.getsize(imports_dir + filename) == 0:
            os.remove(imports_dir + filename)

def slice_filenames(imports_dir):
    for filename in os.listdir(imports_dir):
        if len(filename) <= 10:
            continue

        new_name = filename[:9]
        if not os.path.exists(imports_dir + new_name):
            os.rename(imports_dir + filename, imports_dir + new_name)
        else:
            os.remove(imports_dir + filename)