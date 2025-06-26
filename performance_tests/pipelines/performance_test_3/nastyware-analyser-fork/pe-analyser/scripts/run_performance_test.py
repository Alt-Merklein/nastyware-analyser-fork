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
from datetime import datetime
import random
import pandas as pd
import numpy as np
import argparse
import csv
import shutil
import yara_tools
import yara
import pefile
from sklearn.feature_extraction.text import TfidfVectorizer

from accuracy_epsilon_curve import get_accuracy_epsilon_curve
from batch_performance_test_utils import *
from performance_test_utils import *
from create_phylip_coss_distance import create_phylip_coss_distance
from export_new_format_import_files import format_import_files

import yara_utils

def main(TRAIN_PERCENTAGE, NASTYWARE_DIR, WORKING_DIR, 
         TRAIN_RAW_IMPORT_DIR, TRAIN_FORMATED_IMPORT_DIR, TRAIN_RAW_IMPORT_DIR_MALWARE, TRAIN_RAW_IMPORT_DIR_GOODWARE, 
         TEST_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR_MALWARE, TEST_RAW_IMPORT_DIR_GOODWARE,
         GOODWARE_IMPORT_FILE_DIRECTORIES, MALWARE_IMPORT_FILE_DIRECTORIES,
         BINARIES_GOODWARE_DIR, BINARIES_MALWARE_DIR, BINARIES_EXTRA_MALWARE_DIR,
         EXTRA_AMOUNT, EXTRA_MALWARE_FOLDER, FEATURES_EXTRACTED_DIR, CSV_OUTPUT, SEED, STEP, REP):

# ——————— Reprodutibilidade ———————
    seed = SEED
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
# ————————————————————————————————

    DAMICORE_PYTHON_RESULTS_DIR = f'{NASTYWARE_DIR}/pe-analyser/damicore-python/results/'
    PE_ANALYSER_DIR = f'{NASTYWARE_DIR}/pe-analyser/'
    # OUT_DIR =f'{NASTYWARE_DIR}/pe-analyser/out/batch-test/'
    OUT_DIR = f'{NASTYWARE_DIR}/pe-analyser/out/batch-test/train_percentage{TRAIN_PERCENTAGE}-extra_malware{EXTRA_AMOUNT}-rep{REP}'
    if not (os.path.isdir(OUT_DIR) and os.path.exists(OUT_DIR)):
        os.mkdir(OUT_DIR)
    
    YARA_DIR = os.path.join(OUT_DIR, 'yara-rules')
    if not (os.path.isdir(YARA_DIR) and os.path.exists(YARA_DIR)):
        os.mkdir(YARA_DIR)

    train_val = TRAIN_PERCENTAGE

    print('--------------------------------------------------')
    print(f'Iniciando treino com {train_val * 100}% de amostras para treinamento e {(1 - train_val) * 100}% para teste.')
    print(f'extra_amount = {EXTRA_AMOUNT}')
    extract_features_start_time = time.time()

    print('Limpando diretórios das features extraídas...')
    clean_features_extracted_dir(FEATURES_EXTRACTED_DIR)

    print('Extraindo features dos binários de goodwares...')
    export_files_imports(BINARIES_GOODWARE_DIR, GOODWARE_IMPORT_FILE_DIRECTORIES, malware=False)
    print('Extraindo features dos binários de malwares...')
    export_files_imports(BINARIES_MALWARE_DIR, MALWARE_IMPORT_FILE_DIRECTORIES, malware=True)
    print('Extraindo features dos binários de malwares extras...')
    export_files_imports(BINARIES_EXTRA_MALWARE_DIR, EXTRA_MALWARE_FOLDER, amount=EXTRA_AMOUNT, malware=True)

    extract_features_end_time = time.time()
    extract_features_time = extract_features_end_time - extract_features_start_time


    prepare_samples_start_time = time.time()
    print('Limpando diretórios de trabalho...')
    
    clean_working_dir(WORKING_DIR)
    
    print('Copiando amostras para o diretorio de trabalho...')
    copy_random_files([GOODWARE_IMPORT_FILE_DIRECTORIES], [TRAIN_RAW_IMPORT_DIR, TRAIN_RAW_IMPORT_DIR_GOODWARE], [TEST_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR_GOODWARE], train_val)
    copy_random_files([MALWARE_IMPORT_FILE_DIRECTORIES], [TRAIN_RAW_IMPORT_DIR, TRAIN_RAW_IMPORT_DIR_MALWARE], [TEST_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR_MALWARE], train_val)
    
    copy_new_samples(EXTRA_MALWARE_FOLDER, [TRAIN_RAW_IMPORT_DIR, TRAIN_RAW_IMPORT_DIR_MALWARE], EXTRA_AMOUNT)
    train_raw_samples = len(os.listdir(TRAIN_RAW_IMPORT_DIR))

    print('Formatando amostras...')
    format_import_files(TRAIN_RAW_IMPORT_DIR, TRAIN_FORMATED_IMPORT_DIR)

    prepare_samples_end_time = time.time()
    prepare_samples_time = prepare_samples_end_time - prepare_samples_start_time

    coss_distance_start_time = time.time()
    print('Criando matriz de distancias do treinamento...')
    
    input_matrix = os.path.join(DAMICORE_PYTHON_RESULTS_DIR, f"ncd-matrix-{EXTRA_AMOUNT - STEP}-extra-malwares.phylip")
    output_matrix = os.path.join(DAMICORE_PYTHON_RESULTS_DIR, f"ncd-matrix-{EXTRA_AMOUNT}-extra-malwares.phylip")
    create_phylip_coss_distance(TRAIN_FORMATED_IMPORT_DIR, input_matrix, output_matrix)
    # create_phylip_coss_distance(TRAIN_FORMATED_IMPORT_DIR, output_matrix)
    # create_phylip_coss_distance(TRAIN_FORMATED_IMPORT_DIR, os.path.join(DAMICORE_PYTHON_RESULTS_DIR, 'ncd-matrix.phylip'))
    
    coss_distance_end_time = time.time()
    coss_distance_time = coss_distance_end_time - coss_distance_start_time

    unique_vectors = len(os.listdir(TRAIN_FORMATED_IMPORT_DIR))
    duplicated_vectors = train_raw_samples - unique_vectors 

    shutil.copyfile(output_matrix, os.path.join(DAMICORE_PYTHON_RESULTS_DIR, f"ncd-matrix.phylip"))

    print('Rodando o damicore...')
    os.chdir(PE_ANALYSER_DIR)

    damicore_start_time = time.time()
    ret = os.system(f'python ./pe-analyser.py --folder {TRAIN_FORMATED_IMPORT_DIR}/')
    if ret != 0:
        print('Erro ao rodar o pe-analyser.')
        sys.exit(1)

    damicore_end_time = time.time()
    damicore_time = damicore_end_time - damicore_start_time

    print('Avaliando o desempenho de um decision tree classifier...')
    best_epsilon_start_time = time.time()
    classifiers, acc_dt, acc_mw_dt, acc_gw_dt = get_accuracy_epsilon_curve(TRAIN_RAW_IMPORT_DIR, TEST_RAW_IMPORT_DIR, seed)
    
    best_epsilon_end_time = time.time()
    best_epsilon_time = best_epsilon_end_time - best_epsilon_start_time

    print('Copiando os resultados...')
    
    shutil.copyfile(output_matrix, os.path.join(OUT_DIR, f'dist-matrix-{train_val}-{EXTRA_AMOUNT}-{REP}.phylip'))
    # shutil.copyfile(os.path.join(DAMICORE_PYTHON_RESULTS_DIR, 'ncd-matrix.phylip'), os.path.join(OUT_DIR, f'dist-matrix-{train_val}.phylip'))
    shutil.copyfile(os.path.join(PE_ANALYSER_DIR, 'node_clustering_fastgreedy.txt'), os.path.join(OUT_DIR, f'node_clustering-{train_val}-{EXTRA_AMOUNT}-{REP}.txt'))
    shutil.copyfile(os.path.join(PE_ANALYSER_DIR, 'out/epsilon_accuracy_fastgreedy.png'), os.path.join(OUT_DIR, f'epsilon_accuracy-{train_val}-{EXTRA_AMOUNT}-{REP}.png'))
    
    accuracy_output = os.path.join(OUT_DIR, f'accuracy-{train_val}-{EXTRA_AMOUNT}-{REP}.txt')
    with open(accuracy_output, 'w') as f:
        f.write(f'accuracy: {acc_dt}\n')
        f.write(f'accuracy malware: {acc_mw_dt}\n')
        f.write(f'accuracy goodware: {acc_gw_dt}\n')
    
    # Retrieving clusters and best epsilon

    with open(accuracy_output, 'r') as f:
        lines = f.readlines()
        tot_acc_line = [line for line in lines if 'accuracy' in line][0]
        values = tot_acc_line.split('[')[1].split(']')[0]
        acc_values = np.fromstring(values, sep = ' ')

        best_epsilon_idx = np.argmax(acc_values)

    print(f"Most accurate epsilon index: {best_epsilon_idx}")

    best_classifier = classifiers[best_epsilon_idx]

    node_clustering_fn = 'node_clustering_fastgreedy.txt' # output padrão do Damicore

    lines = open(node_clustering_fn, 'r').readlines()
    lines = lines[1:]
    clusters = [[el.strip() for el in line.strip().split(',') if not el.strip().startswith('-')] for line in lines]
    EPSILON = float(best_epsilon_idx + 1) / 10

    mostly_malware_clusters = []
    for cluster in clusters:
        if len(cluster) > 1:
            malware_count = 0
            for node in cluster:
                if node.startswith('R-'):
                    malware_count += 1

            # Verificar a frequencia com que sera adicionado no cluster
            if malware_count >= EPSILON * len(cluster):
                mostly_malware_clusters.append(cluster)

    print(f"Mostly malware clusters: {mostly_malware_clusters}")

    func_dict = {}
    malware_clusters_df = [yara_utils.ld_data(func_dict, TRAIN_RAW_IMPORT_DIR, cluster, str(i)) for i, cluster in enumerate(mostly_malware_clusters)]
    rest_df = yara_utils.ld_data(func_dict, TRAIN_RAW_IMPORT_DIR, [f for f in os.listdir(TRAIN_RAW_IMPORT_DIR) if not any([f in cluster for cluster in mostly_malware_clusters])], '-1')
    df = pd.concat([rest_df] + malware_clusters_df, ignore_index=True)

    generate_yara_start_time = time.time()
    n_nodes = best_classifier.tree_.node_count
    children_left = best_classifier.tree_.children_left
    children_right = best_classifier.tree_.children_right
    feature = best_classifier.tree_.feature
    threshold = best_classifier.tree_.threshold
    value = best_classifier.tree_.value
    impurity = best_classifier.tree_.impurity

    file_content = ''

    for i in range(len(df['label'].unique()) - 1):

        rule = yara_tools.create_rule(name=f"rule_cluster_{i}", default_boolean='or')

        rule.add_import(name="pe")

        vectorizer = TfidfVectorizer()
        df_vectors = vectorizer.fit_transform(df['funcs']).ceil()
        # Leaves
        leave_id = best_classifier.apply(df_vectors)

        paths = {}
        for leaf in np.unique(leave_id):
            path_leaf = []
            yara_utils.find_path(0, path_leaf, leaf, children_left, children_right)
            paths[leaf] = np.unique(np.sort(path_leaf))

            # Cut paths that lead to goodwares
        filtered_paths = {}
        for path in paths:
            samples_count = value[path][0]
            goodware_value_index = 0
            malware_value_index = i + 1
            if samples_count[malware_value_index] > samples_count[goodware_value_index]:
                filtered_paths[path] = paths[path]

        paths = filtered_paths

        for leaf_num in paths:
            rule.create_condition_group(name="group_{}".format(leaf_num), default_boolean='and')
            yara_utils.get_yara_rule(rule, "group_{}".format(leaf_num), paths[leaf_num], vectorizer.get_feature_names_out(), children_left, feature, func_dict)

            try:
                generated_rule = rule.build_rule(condition_groups=True)

                compiled_rule = yara.compile(source=generated_rule)

                file_content += str(generated_rule) + '\n'
            except:
                print('Error on rule {}'.format(rule.name))

    fn = os.path.join(YARA_DIR, f'rules-{train_val}-{EXTRA_AMOUNT}-{REP}')
    
    file_content = file_content.replace("import \"pe\"\n", "")
    with open(f'{fn}.yar', 'w') as f:
        f.write("import \"pe\"" + file_content)

    file_content = file_content.replace("import \"pe\"", "")\
        .replace("rule ", " drvnskm_rule ")\
        .replace("\"", "'")\
        .replace("\t", "")\
        .replace("\n", "")

    with open(f'{fn}.drv.yar', 'w') as f:
        f.write(file_content[1:])

    generate_yara_end_time = time.time()
    generate_yara_time = generate_yara_end_time - generate_yara_start_time
    

    # Save Results to CSV
    csv_path = CSV_OUTPUT
    write_header = not os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow([   
                'id',          
                'train_percentage',
                'extra_amount',
                'repetition_number',
                'train_raw_samples',
                'duplicated_vectors',
                'unique_vectors',
                'features_extraction_time',
                'prepare_samples_time',
                'coss_distance_time',
                'damicore_time',
                'best_epsilon_time',
                'generate_yara_time',
            ])
        writer.writerow([
            f'{TRAIN_PERCENTAGE}-{EXTRA_AMOUNT}-{REP}',
            TRAIN_PERCENTAGE,
            EXTRA_AMOUNT,
            REP,
            train_raw_samples,
            duplicated_vectors,
            unique_vectors,
            extract_features_time,
            prepare_samples_time,
            coss_distance_time,
            damicore_time,
            best_epsilon_time,
            generate_yara_time
        ])        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Saucy Performance test')
    parser.add_argument('--train_percentage', type=float, help='train files / (train files + test files)', default=0.8)
    parser.add_argument('--nastyware_dir', type=folder_exists, required=True, help='Folder with nastyware repo')
    parser.add_argument('--working_dir', type=folder_exists, help='Temporary directory to store files during the test', required=True)
    parser.add_argument('--train_raw_import_dir', type=folder_exists, help='Temporary directory to store copied training files', required=True)
    parser.add_argument('--train_formated_import_dir', type=folder_exists, help='Temporary directory to store formated training files', required=True)
    parser.add_argument('--test_raw_import_dir', type=folder_exists, help='Temporary directory to store copied test files', required=True)
    parser.add_argument('--train_raw_import_dir_malware', type=folder_exists, help='Temporary directory to store copied training files (malware only)', required=True)
    parser.add_argument('--train_raw_import_dir_goodware', type=folder_exists, help='Temporary directory to store copied training files (goodware only)', required=True)
    parser.add_argument('--test_raw_import_dir_malware', type=folder_exists, help='Temporary directory to store copied test files (malware only)', required=True)
    parser.add_argument('--test_raw_import_dir_goodware', type=folder_exists, help='Temporary directory to store copied test files (goodware only)', required=True)
    parser.add_argument('--goodware_import_file_directories', type=folder_exists, help='Directories with all goodware import files that may be used for train/test', required=True)#, nargs='+')
    parser.add_argument('--malware_import_file_directories', type=folder_exists, help='Directories with all malware import files that may be used for train/test', required=True)#, nargs= '+')
    parser.add_argument('--binaries_goodware_dir', type= folder_exists, help='Directory with the executable goodware files', required=True)
    parser.add_argument('--binaries_malware_dir', type= folder_exists, help='Directory with the executable malware files', required=True)
    parser.add_argument('--binaries_extra_malware_dir', type= folder_exists, help='Directory with the executable extra malware files', required=True)
    parser.add_argument('--extra_amount', type=int, help='Amount of extra malware to use on test', required=True)
    parser.add_argument('--extra_malware_folder', type=folder_exists, help='Folder with extra malware to use on training', required=True)
    parser.add_argument('--features_extracted_folder', type=folder_exists, help='Folder with extracted features files', required=True)
    parser.add_argument('--append_csv', type=str, help='CSV file to store results', required=True)
    parser.add_argument('--seed', type=int, default=42, help="Set seed for the random elements", required=True)
    parser.add_argument('--step', type=int, default=100, help='Increasing step of the extra malware amount', required=True)
    parser.add_argument('--rep', type=int, help='Repetition number at an extra_amount and train_percentage', required=True)


    args = parser.parse_args()

    main(
        args.train_percentage,
        args.nastyware_dir,
        args.working_dir,
        args.train_raw_import_dir,
        args.train_formated_import_dir,
        args.train_raw_import_dir_malware, 
        args.train_raw_import_dir_goodware,
        args.test_raw_import_dir, 
        args.test_raw_import_dir_malware,
        args.test_raw_import_dir_goodware, 
        args.goodware_import_file_directories,
        args.malware_import_file_directories,
        args.binaries_goodware_dir,
        args.binaries_malware_dir,
        args.binaries_extra_malware_dir,
        args.extra_amount, 
        args.extra_malware_folder, 
        args.features_extracted_folder,
        args.append_csv,
        args.seed,
        args.step,
        args.rep
    )
