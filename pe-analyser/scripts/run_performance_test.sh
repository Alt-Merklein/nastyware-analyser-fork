#!/bin/bash

# ====== CONFIG ======
python_ver="python"
script="run_performance_test.py"

train_percentage=0.005

nastyware_dir="/home/ceao/nastyware-analyser-fork/"
working_dir="/home/ceao/files/nastyware-files-mix/pipeline/"

train_raw_import_dir="${working_dir}/train-set/raw-import-files-mix/"
train_formated_import_dir="${working_dir}/train-set/formated-import-files-mix/"
train_raw_import_dir_malware="${working_dir}/train-set/raw-import-files-malware/"
train_raw_import_dir_goodware="${working_dir}/train-set/raw-import-files-goodware/"

test_raw_import_dir="${working_dir}/test-set/raw-import-files-mix/"
test_raw_import_dir_malware="${working_dir}/test-set/raw-import-files-malware/"
test_raw_import_dir_goodware="${working_dir}/test-set/raw-import-files-goodware/"

goodware_import_file_directories="/home/ceao/files/nastyware-files-mix/goodware-mix/"
malware_import_file_directories="/home/ceao/files/nastyware-files-mix/malware-mix/"

# ====== RUN SCRIPT ======
$python_ver $script \
    --train_percentage $train_percentage \
    --nastyware_dir $nastyware_dir \
    --working_dir $working_dir \
    --train_raw_import_dir $train_raw_import_dir \
    --train_formated_import_dir $train_formated_import_dir \
    --test_raw_import_dir $test_raw_import_dir \
    --train_raw_import_dir_malware $train_raw_import_dir_malware \
    --train_raw_import_dir_goodware $train_raw_import_dir_goodware \
    --test_raw_import_dir_malware $test_raw_import_dir_malware \
    --test_raw_import_dir_goodware $test_raw_import_dir_goodware \
    --goodware_import_file_directories $goodware_import_file_directories \
    --malware_import_file_directories $malware_import_file_directories

# pause
