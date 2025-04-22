"""
    Script para realizar o teste com varias amostras da abordagem que temos
    
    Porcentagem de amostras para treinamentos e testes:
    10% - 90%
    20% - 80%
    30% - 70%
    50% - 50%
    70% - 30%
    80% - 20%
    90% - 10%
"""

import os
import sys
import time
import random
import numpy as np
from batch_performance_test_utils import *
from export_new_format_import_files import format_import_files
from create_phylip_coss_distance import create_phylip_coss_distance
from accuracy_epsilon_curve import get_accuracy_epsilon_curve

WORKING_DIR = '/archive/files/nastyware-files-mix/batch-performance-test/'
TRAIN_RAW_IMPORT_DIR = '/archive/files/nastyware-files-mix/batch-performance-test/train-set/raw-import-files-mix/'
TRAIN_FORMATED_IMPORT_DIR = '/archive/files/nastyware-files-mix/batch-performance-test/train-set/formated-import-files-mix'
TEST_RAW_IMPORT_DIR = '/archive/files/nastyware-files-mix/batch-performance-test/test-set/raw-import-files-mix/'

DAMICORE_PYTHON_RESULTS_DIR = '/home/joao/my/projects/nastyware-analyser/pe-analyser/damicore-python/results'
PE_ANALYSER_DIR = '/home/joao/my/projects/nastyware-analyser/pe-analyser'
OUT_DIR = '/home/joao/my/projects/nastyware-analyser/pe-analyser/out/batch-test/'

GOODWARE_IMPORT_FILE_DIRECTORIES = [
    '/archive/files/nastyware-files-mix/goodware-mix/',
]
# GOODWARE_IMPORT_FILE_DIRECTORIES = [
#     '/archive/files/nastyware-files/import-windows-server-2016-f/',
#     '/archive/files/nastyware-files/import-windows-server-2019-f/',
#     '/archive/files/nastyware-files/import-windows-server-2022-f/'
# ]

MALWARE_IMPORT_FILE_DIRECTORIES = [
    '/archive/files/nastyware-files-mix/malware-mix/'
]
# MALWARE_IMPORT_FILE_DIRECTORIES = [
#     '/archive/files/nastyware-files/import-malware-bazaar-2021-01-to-2021-02-f/',
#     '/archive/files/nastyware-files/import-malware-bazaar-2021-03-to-2021-04/'
# ]


TOTAL_GOODWARE_FILES = count_files_in_directories(GOODWARE_IMPORT_FILE_DIRECTORIES)
TOTAL_MALWARE_FILES = count_files_in_directories(MALWARE_IMPORT_FILE_DIRECTORIES)

NUMBER_OF_WORKING_GOODWARE_FILES = min(TOTAL_GOODWARE_FILES, TOTAL_MALWARE_FILES)
NUMBER_OF_WORKING_MALWARE_FILES = min(TOTAL_GOODWARE_FILES, TOTAL_MALWARE_FILES)


TOTAL_WORKING_FILES = NUMBER_OF_WORKING_GOODWARE_FILES + NUMBER_OF_WORKING_MALWARE_FILES

TRAIN_PERCENTAGES = [0.9, 0.8, 0.7, 0.5, 0.3, 0.1]

def main():
    for train_val in TRAIN_PERCENTAGES:
        print('--------------------------------------------------')
        print(f'Iniciando treino com {train_val * 100}% de amostras para treinamento e {(1 - train_val) * 100}% para teste.')
        print('Limpando diretorios de trabalho...')
        clean_working_dir(WORKING_DIR)
        
        print('Copiando amostras para o diretorio de trabalho...')

        copy_random_files(GOODWARE_IMPORT_FILE_DIRECTORIES, TRAIN_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR, train_val)
        copy_random_files(MALWARE_IMPORT_FILE_DIRECTORIES, TRAIN_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR, train_val)

        print('Formatando amostras...')
        format_import_files(TRAIN_RAW_IMPORT_DIR, TRAIN_FORMATED_IMPORT_DIR)

        print('Criando matriz de distancias do treinamento...')
        create_phylip_coss_distance(TRAIN_FORMATED_IMPORT_DIR, os.path.join(DAMICORE_PYTHON_RESULTS_DIR, 'ncd-matrix.phylip'))

        print('Rodando o damicore...')
        os.chdir(PE_ANALYSER_DIR)
        ret = os.system(f'./pe-analyser.py --folder {TRAIN_FORMATED_IMPORT_DIR}/')
        if ret != 0:
            print('Erro ao rodar o pe-analyser.')
            sys.exit(1)

        print('Obtendo precisao dos resultados...')
        acc_dt, acc_mw_dt, acc_gw_dt = get_accuracy_epsilon_curve(TRAIN_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR)

        print('Copiando os resultados...')
        shutil.copyfile(os.path.join(DAMICORE_PYTHON_RESULTS_DIR, 'ncd-matrix.phylip'), os.path.join(OUT_DIR, f'dist-matrix-{train_val}.phylip'))
        shutil.copyfile(os.path.join(PE_ANALYSER_DIR, 'node_clustering_fastgreedy.txt'), os.path.join(OUT_DIR, f'node_clustering{train_val}.txt'))
        shutil.copyfile(os.path.join(PE_ANALYSER_DIR, 'out/epsilon_accuracy_fastgreedy.png'), os.path.join(OUT_DIR, f'epsilon_accuracy{train_val}.png'))
        
        with open(os.path.join(OUT_DIR, f'accuracy-{train_val}.txt'), 'w') as f:
            f.write(f'accuracy: {acc_dt}\n')
            f.write(f'accuracy malware: {acc_mw_dt}\n')
            f.write(f'accuracy goodware: {acc_gw_dt}\n')

        


if __name__ == '__main__':
    main()
