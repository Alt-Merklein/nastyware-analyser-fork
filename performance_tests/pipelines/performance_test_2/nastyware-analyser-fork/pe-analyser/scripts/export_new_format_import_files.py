import sys
import os
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
import matplotlib.pyplot as plt
import argparse
import hashlib

func_dict = {}

def ld_data(dir_name):
    # Load data in files from directory dir_name in a pandas dataframe
    df = pd.DataFrame()
    for filename in os.listdir(dir_name):
        funcs = []
        with open(os.path.join(dir_name, filename), 'r') as f:
            lines = f.read().splitlines()
            
            for line in lines:
                lib, func = line.split(' ')
                if '@' in func or '?' in func:
                    continue
                
                # TODO: Comentado para testar Vectorizer sem lower()
                # if not func.lower() in func_dict:
                #     func_dict[func.lower()] = [(lib, func)]
                # else:
                #     func_dict[func.lower()].append((lib, func))

                if not func in func_dict:
                    func_dict[func] = [(lib, func)]
                else:
                    # TODO: Melhorar. So dar append se a lib for diferente das atuais
                    func_dict[func].append((lib, func))


                funcs.append(func)

        label = 'MALWARE' if filename.startswith('R') else 'GOODWARE'
        df = pd.concat([df, pd.DataFrame({'filename': filename, 'label': label, 'funcs': ' '.join(funcs)}, index=[0])], ignore_index=True)
        
    return df

def format_import_files(train_dt_dir_name, export_dt_dir_name):
    func_dict = {}
    
    train = ld_data(train_dt_dir_name)
    vectorizer = CountVectorizer(lowercase=False)
    train_vectors = vectorizer.fit_transform(train['funcs'])

    with open('feature_names.txt', 'w') as f:
        for feature in vectorizer.get_feature_names_out():
            f.write(feature + '\n')

    for index, row in train.iterrows():
        filename = row['filename']
        # Create file in export directory 
        with open(os.path.join(export_dt_dir_name, filename), 'w') as f:
            # write train_vectors list as a string in the file
            f.write(''.join([str(x) * 1 for x in train_vectors[index].toarray()[0]]))


# def delete_duplicates_string_based(dir_path, preserve_files=None):
def delete_duplicates(dir_path, preserve_files=None):
    """
    Remove arquivos duplicados com base no conteúdo textual (string de 0s e 1s).
    Preserva arquivos listados em `preserve_files`, se fornecido.
    """
    if preserve_files is None:
        preserve_files = set()

    seen_contents = {}
    removed_files = 0

    for fname in os.listdir(dir_path):
        fpath = os.path.join(dir_path, fname)
        if not os.path.isfile(fpath):
            continue

        try:
            with open(fpath, 'r') as f:
                content = f.read().strip()
        except Exception as e:
            print(f"Erro ao ler {fpath}: {e}")
            continue

        if content in seen_contents:
            original_path = seen_contents[content]
            original_name = os.path.basename(original_path)

            if original_name in preserve_files:
                # Remove o duplicado atual
                try:
                    os.remove(fpath)
                    removed_files += 1
                except Exception as e:
                    print(f"Erro ao remover {fpath}: {e}")
            else:
                # Remove o antigo e preserva o atual
                try:
                    os.remove(original_path)
                    seen_contents[content] = fpath  # atualiza o mapeamento
                    removed_files += 1
                except Exception as e:
                    print(f"Erro ao remover {original_path}: {e}")
        else:
            seen_contents[content] = fpath

    print(f"\t Total de arquivos removidos: {removed_files}")
    print(f"\t Arquivos únicos restantes: {len(seen_contents)}")
    # return removed_files, len(seen_contents)


# def md5_hash(filepath):
#     """Gera hash MD5 a partir do conteúdo de um arquivo binário."""
#     hasher = hashlib.md5()
#     with open(filepath, 'rb') as f:
#         while chunk := f.read(8192):
#             hasher.update(chunk)
#     return hasher.hexdigest()

# def delete_duplicates_hash_based(dir_path, preserve_files=None):
#     """
#     Remove arquivos duplicados com base no conteúdo binário (hash MD5).
#     Preserva arquivos listados em `preserve_files`, se fornecido.
#     """
#     if preserve_files is None:
#         preserve_files = set()

#     seen_hashes = {}
#     removed_files = 0

#     for fname in os.listdir(dir_path):
#         fpath = os.path.join(dir_path, fname)
#         if not os.path.isfile(fpath):
#             continue

#         try:
#             file_hash = md5_hash(fpath)
#         except Exception as e:
#             print(f"Erro ao ler {fpath}: {e}")
#             continue

#         if file_hash in seen_hashes:
#             original_path = seen_hashes[file_hash]
#             original_name = os.path.basename(original_path)

#             # Se o original já está na matriz, preserva ele e remove o duplicado atual
#             if original_name in preserve_files:
#                 try:
#                     os.remove(fpath)
#                     removed_files += 1
#                 except Exception as e:
#                     print(f"Erro ao remover {fpath}: {e}")
#             else:
#                 # Caso contrário, remove o original e mantém o atual
#                 try:
#                     os.remove(original_path)
#                     seen_hashes[file_hash] = fpath  # atualiza para novo "original"
#                     removed_files += 1
#                 except Exception as e:
#                     print(f"Erro ao remover {original_path}: {e}")
#         else:
#             seen_hashes[file_hash] = fpath

#     print(f"Total de arquivos removidos: {removed_files}")
#     print(f"Arquivos únicos restantes: {len(seen_hashes)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='Directory of input files', required=True)
    #parser.add_argument('-o', '--output', help='file to output features', default="./features")
    args = parser.parse_args()  

    format_import_files(args.directory, "./features")

if __name__ == '__main__':
    main()