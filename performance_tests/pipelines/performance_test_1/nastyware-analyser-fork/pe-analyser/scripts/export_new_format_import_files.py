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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='Directory of input files', required=True)
    #parser.add_argument('-o', '--output', help='file to output features', default="./features")
    args = parser.parse_args()  

    format_import_files(args.directory, "./features")

if __name__ == '__main__':
    main()