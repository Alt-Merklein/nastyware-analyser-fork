import sys
import os
import pandas as pd
import numpy as np
import seaborn as sns
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
import matplotlib.pyplot as plt
import multiprocessing as mp

TRAIN_DIR = '/archive/files/nastyware-files-mix/pipeline/train-set/raw-import-files-mix'
TEST_DIR = '/archive/files/nastyware-files-mix/pipeline/test-set/raw-import-files-mix'
# TRAIN_DIR = '/archive/files/import-small-dir/'
#TEST_MALWARE_DIR = '/archive/files/nastyware-files/import-malware-bazaar-2021-03-to-2021-04/'
#TEST_GOODWARE_DIR = '/archive/files/nastyware-files/import-windows-server-2019/'

acc_dt = []
acc_mw_dt = []
acc_gw_dt = []
acc_sd = []
mostly_malware_clusters = []

cluster_alg = 'fastgreedy'

def ld_data(dir_name, files, label=None):
    # Load data in files from directory dir_name in a pandas dataframe
    df = pd.DataFrame()
    for filename in files:
        funcs = []
        with open(os.path.join(dir_name, filename), 'r') as f:
            lines = f.read().splitlines()

            for line in lines:
                lib, func = line.split(' ')
                if '@' in func or '?' in func:
                    continue

                if not func.lower() in func_dict:
                    func_dict[func.lower()] = [(lib, func)]
                else:
                    func_dict[func.lower()].append((lib, func))

                funcs.append(func)

        # TODO: Gambiarra
        if label == None:
            label = 'MALWARE' if filename.startswith('R-') else 'GOODWARE'

        df = pd.concat([df, pd.DataFrame({'filename': filename, 'label': label, 'funcs': ' '.join(funcs)}, index=[0])], ignore_index=True)

        # TODO: Gambiarra
        if label == 'MALWARE' or label == 'GOODWARE':
            label = None

    return df

# Functions that occur in all malwares in the cluster
def plus_functions(dir, cluster):
    file_sets = []

    for file in cluster:
        file_sets.append(set(line.split(' ')[1] for line in open(os.path.join(dir, file)).read().splitlines()))
    
    intersection = set.intersection(*file_sets)

    return intersection

# Functions that does not occur in any malwares in the cluster
def minus_functions(dir, cluster):
    others_set = set()

    dir = os.path.join(dir)

    for file in os.listdir(dir):
        if file in cluster:
            continue

        others_set.update(set(line.split(' ')[1] for line in open(os.path.join(dir, file)).read().splitlines()))
    
    cluster_set = set()
    for file in cluster:
        cluster_set.update(set(line.split(' ')[1] for line in open(os.path.join(dir, file)).read().splitlines()))

    others_minus_cluster = others_set - cluster_set

    return others_minus_cluster

def functions(dir):
    return [set(line.split(' ')[1] for line in open(os.path.join(dir, file)).read().splitlines()) for file in os.listdir(dir)]

def predict_similarity_difference(file_functions_set, plus_functions_set_list, minus_functions_set_list):

    for plus_functions_set, minus_functions_set in zip(plus_functions_set_list, minus_functions_set_list):
        plus_functions_intersection = file_functions_set & plus_functions_set
        minus_functions_intersection = file_functions_set & minus_functions_set

        if len(plus_functions_intersection) == len(plus_functions_set) and len(minus_functions_intersection) == 0:
            return 'MALWARE'

    return 'GOODWARE'


func_dict = {}

def dt_classification(mostly_malware_clusters, epsilon):
    malware_clusters_df = [ld_data(TRAIN_DIR, cluster, str(i)) for i, cluster in enumerate(mostly_malware_clusters)]
    rest_df = ld_data(TRAIN_DIR, [f for f in os.listdir(TRAIN_DIR) if not any([f in cluster for cluster in mostly_malware_clusters])], '-1')
    df = pd.concat([rest_df] + malware_clusters_df, ignore_index=True)

    vectorizer = TfidfVectorizer()
    df_vectors = vectorizer.fit_transform(df['funcs']).ceil()
    classifier = DecisionTreeClassifier(criterion='entropy')
    classifier.fit(df_vectors, df['label'])

    if TEST_DIR != '':
        test_df = ld_data(TEST_DIR, os.listdir(TEST_DIR))
        test_mw = test_df[test_df['label'] == 'MALWARE']
        test_gw = test_df[test_df['label'] == 'GOODWARE']
    else:
        test_mw = ld_data(TEST_MALWARE_DIR, os.listdir(TEST_MALWARE_DIR), 'MALWARE')
        test_gw = ld_data(TEST_GOODWARE_DIR, os.listdir(TEST_GOODWARE_DIR), 'GOODWARE')
        test_df = pd.concat([test_mw, test_gw], ignore_index=True)

    test_mw_vectors = vectorizer.transform(test_mw['funcs']).ceil()
    test_gw_vectors = vectorizer.transform(test_gw['funcs']).ceil()
    test_vectors = vectorizer.transform(test_df['funcs']).ceil()
    pred_mw = classifier.predict(test_mw_vectors)
    pred_gw = classifier.predict(test_gw_vectors)
    pred = classifier.predict(test_vectors)
    pred_mw = ['MALWARE' if p != '-1' else 'GOODWARE' for p in pred_mw]
    pred_gw = ['MALWARE' if p != '-1' else 'GOODWARE' for p in pred_gw]
    pred = ['MALWARE' if p != '-1' else 'GOODWARE' for p in pred]

    return classifier, accuracy_score(test_df['label'], pred), accuracy_score(test_mw['label'], pred_mw), accuracy_score(test_gw['label'], pred_gw)

def sd_classification(epsilon):
    plus = [plus_functions(TRAIN_DIR, cluster) for cluster in mostly_malware_clusters]
    minus = [minus_functions(TRAIN_DIR, cluster) for cluster in mostly_malware_clusters]

    test_mw = functions(TEST_MALWARE_DIR)
    test_gw = functions(TEST_GOODWARE_DIR)
    test = test_mw + test_gw
    test_mw_label = ['MALWARE' for _ in test_mw]
    test_gw_label = ['GOODWARE' for _ in test_gw]
    test_label = test_mw_label + test_gw_label
    pred_mw = [predict_similarity_difference(file_functions_set, plus, minus) for file_functions_set in test_mw]
    pred_gw = [predict_similarity_difference(file_functions_set, plus, minus) for file_functions_set in test_gw]
    pred = [predict_similarity_difference(file_functions_set, plus, minus) for file_functions_set in test]

    return accuracy_score(test_label, pred)

def get_accuracy(clusters, epsilon, queue):
    print(f'Processing epsilon {epsilon}')

    mostly_malware_clusters = []
    for cluster in clusters:
        if len(cluster) > 1:
            malware_count = 0
            for node in cluster:
                if node.startswith('R-'):
                    malware_count += 1
            if malware_count >= epsilon * len(cluster):
                mostly_malware_clusters.append(cluster)

    queue.put((epsilon, dt_classification(mostly_malware_clusters.copy(), epsilon)))

def get_accuracy_epsilon_curve(train_dir, test_dir):
    global TRAIN_DIR
    global TEST_DIR
    global mostly_malware_clusters

    TRAIN_DIR = train_dir
    TEST_DIR = test_dir

    acc_dt = []
    acc_mw_dt = []
    acc_gw_dt = []
    mostly_malware_clusters = []

    cluster_alg = 'fastgreedy'

    lines = open(f'./node_clustering_{cluster_alg}.txt', 'r').readlines()
    lines = lines[1:]
    clusters = [[el.strip() for el in line.strip().split(',') if not el.strip().startswith('-')] for line in lines]

    xx = np.linspace(0.1, 1, 10)

    processes = min(len(xx), mp.cpu_count())
    pool = mp.Pool(processes)
    manager = mp.Manager()
    queue = manager.Queue()

    for epsilon in xx:
        pool.apply_async(get_accuracy, args=(clusters, epsilon, queue))

    pool.close()
    pool.join()

    epsilons = []
    classifiers = {}

    while not queue.empty():
        epsilon, (classifier, acc, acc_mw, acc_gw) = queue.get()
        epsilons.append(epsilon)
        classifiers[round(10*epsilon) - 1] = classifier
        acc_dt.append(acc)
        acc_mw_dt.append(acc_mw)
        acc_gw_dt.append(acc_gw)

    # Sort
    idx = np.argsort(epsilons)
    xx = np.array(epsilons)[idx]
    acc_dt = np.array(acc_dt)[idx]
    acc_mw_dt = np.array(acc_mw_dt)[idx]
    acc_gw_dt = np.array(acc_gw_dt)[idx]

    plt.clf()
    # Plot the results varying epsilon
    plt.plot(xx, acc_dt, label='Decision Tree (Total)')
    plt.plot(xx, acc_mw_dt, label='Decision Tree (Malware)')
    plt.plot(xx, acc_gw_dt, label='Decision Tree (Goodware)')
    # plt.plot(xx, acc_sd, label='Similarity Difference')
    plt.grid()
    plt.xlabel('Epsilon')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig(f'out/epsilon_accuracy_{cluster_alg}.png')
    return classifiers, acc_dt, acc_mw_dt, acc_gw_dt


if __name__ == '__main__':
    lines = open(f'./node_clustering_{cluster_alg}.txt', 'r').readlines()
    lines = lines[1:]
    clusters = [[el.strip() for el in line.strip().split(',') if not el.strip().startswith('-')] for line in lines]

    xx = np.linspace(0.1, 1, 10)

    for epsilon in xx:
        print(f'Processing epsilon {epsilon} / {xx[-1]}', end='\r')

        mostly_malware_clusters = []
        for cluster in clusters:
            if len(cluster) > 1:
                malware_count = 0
                for node in cluster:
                    if node.startswith('R-'):
                        malware_count += 1
                if malware_count >= epsilon * len(cluster):
                    mostly_malware_clusters.append(cluster)

        acc_tot, acc_mw, acc_gw = dt_classification(mostly_malware_clusters,epsilon)
        acc_dt.append(acc_tot)
        acc_mw_dt.append(acc_mw)
        acc_gw_dt.append(acc_gw)
        # acc_sd.append(sd_classification(epsilon))

    print()

    # Plot the results varying epsilon
    plt.plot(xx, acc_dt, label='Decision Tree (Total)')
    plt.plot(xx, acc_mw_dt, label='Decision Tree (Malware)')
    plt.plot(xx, acc_gw_dt, label='Decision Tree (Goodware)')
    # plt.plot(xx, acc_sd, label='Similarity Difference')
    plt.grid()
    plt.xlabel('Epsilon')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig(f'out/epsilon_accuracy_{cluster_alg}.png')
