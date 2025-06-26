
import os
import sys
import time
import shutil
import random
import numpy as np
import pandas as pd

def count_files_in_directories(directories):
    total_files = 0
    for directory in directories:
        total_files += len(os.listdir(directory))
    return total_files

def copy_random_files(source_directories, destination_train_directories, destination_test_directories, percentage):
    for source_directory in source_directories:
        print(f'\t processing {source_directory}')
        files = os.listdir(source_directory)
        for file in files:
            full_path = os.path.join(source_directory, file)
            if not os.path.isfile(full_path):
                continue

            if random.random() < percentage:
                for train_directory in destination_train_directories:
                    shutil.copy(full_path, train_directory)
            else:
                for test_directory in destination_test_directories:
                    shutil.copy(full_path, test_directory)

def clean_working_dir(working_dir):
    # Remove all files from test-set/raw-import-files
    dir = os.path.join(working_dir, 'test-set/raw-import-files-mix/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

    dir = os.path.join(working_dir, 'test-set/raw-import-files-malware/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

    dir = os.path.join(working_dir, 'test-set/raw-import-files-goodware/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
    
    # Remove all files from train-set/raw-import-files
    dir = os.path.join(working_dir, 'train-set/raw-import-files-mix/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

    dir = os.path.join(working_dir, 'train-set/raw-import-files-malware/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

    dir = os.path.join(working_dir, 'train-set/raw-import-files-goodware/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
    # Remove all files from train-set/formated-import-files
    dir = os.path.join(working_dir, 'train-set/formated-import-files-mix/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

def clean_features_extracted_dir(features_extracted_dir):
    # Remove all files from extra-malware/
    dir = os.path.join(features_extracted_dir, 'extra-malware/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

    # Remove all files from goodware-mix/
    dir = os.path.join(features_extracted_dir, 'goodware-mix/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

    # Remove all files from malware-mix/
    dir = os.path.join(features_extracted_dir, 'malware-mix/')
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
