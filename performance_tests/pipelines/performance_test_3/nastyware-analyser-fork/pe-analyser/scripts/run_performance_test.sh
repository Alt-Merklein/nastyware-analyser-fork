#!/bin/bash

# ====== ERROR HANDLING ======
set -e # Exit immediately if a command exits with a non-zero status

trap 'echo "An error occurred. Exiting."' ERR
trap 'echo "Script interrupted. Exiting."' INT
trap 'echo "Script terminated. Exiting."' TERM


# ====== TEST PARAMETER AND OUTPUT ======
# Set the parameters as you want to test

train_percentage=0.9

step=100        # Samples' increasing pace
max_extra=1400      #2698   # Maximum extra malware samples
# extra_malware_amount=0 --- Changes must be made in the first line of 'for' loop
reps=5          # Times each sample's length will run to get its metrics


# ====== CONFIG ======

# Enviroment
python_ver="python"
script="run_performance_test.py"
base_seed=42   # Choose any integer number

## Directories
# You must set at least these four directories' paths in your machine 

csv_output="/home/djesus/tmp/ceao2025/true_performance_tests/csv_results/performance_results_3.csv" # Output file's path

nastyware_dir="/home/djesus/tmp/ceao2025/true_performance_tests/performance_test_3_new/nastyware-analyser-fork/"
nastyware_files_mix="/home/djesus/tmp/ceao2025/nastyware-files-mix/"
working_dir="/home/djesus/tmp/ceao2025/nastyware-files-mix/pipeline/"

# -----------
# (Optional) Set the specific folders below or let the script make the standard paths for the experiment pipeline

# Train
train_raw_import_dir="${working_dir}train-set/raw-import-files-mix/"
train_formated_import_dir="${working_dir}train-set/formated-import-files-mix/"
train_raw_import_dir_malware="${working_dir}train-set/raw-import-files-malware/"
train_raw_import_dir_goodware="${working_dir}train-set/raw-import-files-goodware/"

# Test
test_raw_import_dir="${working_dir}test-set/raw-import-files-mix/"
test_raw_import_dir_malware="${working_dir}test-set/raw-import-files-malware/"
test_raw_import_dir_goodware="${working_dir}test-set/raw-import-files-goodware/"

# Feature-extracted
features_extracted_dir="${nastyware_files_mix}feature-extracted-files/"

goodware_import_file_directories="${features_extracted_dir}goodware-mix/"
malware_import_file_directories="${features_extracted_dir}malware-mix/"
extra_malware_directory="${features_extracted_dir}extra-malware/"

# Binaries
executable_files_dir="${nastyware_files_mix}executable-files/"

binaries_goodware_dir="${executable_files_dir}goodware-mix-executables"
binaries_malware_dir="${executable_files_dir}malware-mix-executables"
binaries_extra_malware_dir="${executable_files_dir}extra-malware-executables"


# ====== CHECK IF THE DIRECTORIES EXISTS =====
dirs=(
  "$nastyware_dir"
  "$nastyware_files_mix"
  "$working_dir"
  "$train_raw_import_dir"
  "$train_formated_import_dir"
  "$train_raw_import_dir_malware"
  "$train_raw_import_dir_goodware"
  "$test_raw_import_dir"
  "$test_raw_import_dir_malware"
  "$test_raw_import_dir_goodware"
  "$goodware_import_file_directories"
  "$malware_import_file_directories"
  "$extra_malware_directory"
  "$binaries_goodware_dir"
  "$binaries_malware_dir"
  "$binaries_extra_malware_dir"
)

not_found_dir=0

for d in "${dirs[@]}"; do
  if [ ! -d "$d" ]; then
    not_found_dir=$((not_found_dir + 1))
    echo "Directory not found: $d"
  fi
done

if [ $not_found_dir -ge 1 ]; then
  echo "Some directories were not found. Please check the correct paths and make sure the files are in them."
  exit 1
fi

# ====== RUN SCRIPT LOOP ======
for i in "${train_percentage[@]}"; do
    extra_amount=0
    
    while [ "$extra_amount" -le "$max_extra" ]; do
        echo "Running with extra_amount=$extra_amount at train_percentage=$i"
        for r in $(seq 1 $reps); do
            echo "Starting repetition number $r"
            seed=$((base_seed)) # may add $r if you want to change the seed, for example
            $python_ver $script \
                --train_percentage $i \
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
                --malware_import_file_directories $malware_import_file_directories \
                --binaries_goodware_dir $binaries_goodware_dir \
                --binaries_malware_dir $binaries_malware_dir \
                --binaries_extra_malware_dir $binaries_extra_malware_dir \
                --extra_amount $extra_amount \
                --extra_malware_folder $extra_malware_directory \
                --features_extracted_folder $features_extracted_dir \
                --append_csv $csv_output \
                --seed $seed \
                --step $step \
                --rep $r
            echo "Ending repetition number $r"
        done
        echo -e "Done with extra_amount=$extra_amount at train_percentage=$i \n"

        extra_amount=$((extra_amount + step))
    done
done

echo "All runs completed."


# python_ver="python"
# script="run_performance_test.py"
# base_seed=42   # Choose any integer number
# # -----------
# # You must set at least these four directories' paths in your machine 
# nastyware_dir="/home/ceao/tcc/performance_tests/performance_test_0/nastyware-analyser-fork"
# nastyware_files_mix="/home/ceao/tcc/files/nastyware-files-mix/"
# working_dir="/home/ceao/tcc/files/nastyware-files-mix/pipeline"
# csv_output="/home/ceao/tcc/performance_tests/performance_test_0/performance_results.csv" # Output file's path
# # -----------

# train_raw_import_dir="${working_dir}/train-set/raw-import-files-mix/"
# train_formated_import_dir="${working_dir}/train-set/formated-import-files-mix/"
# train_raw_import_dir_malware="${working_dir}/train-set/raw-import-files-malware/"
# train_raw_import_dir_goodware="${working_dir}/train-set/raw-import-files-goodware/"

# test_raw_import_dir="${working_dir}/test-set/raw-import-files-mix/"
# test_raw_import_dir_malware="${working_dir}/test-set/raw-import-files-malware/"
# test_raw_import_dir_goodware="${working_dir}/test-set/raw-import-files-goodware/"

# goodware_import_file_directories="${nastyware_files_mix}/goodware-mix/"
# malware_import_file_directories="${nastyware_files_mix}/malware-mix/"

# extra_malware_directory="${nastyware_files_mix}/extra-malware/"

# # ====== TEST PARAMETER AND OUTPUT ======
# # Set the parameters as you want to test

# train_percentage=0.9

# step=100        # Samples' increasing pace
# max_extra=2698   # Maximum extra malware samples
# # extra_amount=0 --- Changes must be made in the first line of 'for' loop
# reps=3          # Times each sample's length will run to get its metrics

# # -----------------------------

# # ====== CREATE DIRECTORIES WHICH DON'T EXISTS =====
# dirs=(
#   "$nastyware_dir"
#   "$nastyware_files_mix"
#   "$working_dir"
#   "$train_raw_import_dir"
#   "$train_formated_import_dir"
#   "$train_raw_import_dir_malware"
#   "$train_raw_import_dir_goodware"
#   "$test_raw_import_dir"
#   "$test_raw_import_dir_malware"
#   "$test_raw_import_dir_goodware"
#   "$goodware_import_file_directories"
#   "$malware_import_file_directories"
#   "$extra_malware_directory"
# )

# dir_created=0

# for d in "${dirs[@]}"; do
#   if [ ! -d "$d" ]; then
#     dir_created=1
#     echo "Creating directory: $d"
#     mkdir -p "$d"
#     echo "Directory created. Please check the paths and put the files in them."
#   fi
# done

# if [ $dir_created -eq 1 ]; then
#   echo "ATTENTION: Some directories were created. Please check the paths and put the files in them."
#   exit 1
# fi

# # ====== RUN SCRIPT LOOP ======
# for i in "${train_percentage[@]}"; do
#     extra_amount=0
    
#     while [ "$extra_amount" -le "$max_extra" ]; do
#         echo "Running with extra_amount=$extra_amount at train_percentage=$i"
#         for r in $(seq 1 $reps); do
#             echo "Starting repetition number $r"
#             seed=$((base_seed)) # may add $r if you want to change the seed, for example
#             $python_ver $script \
#                 --train_percentage $i \
#                 --nastyware_dir $nastyware_dir \
#                 --working_dir $working_dir \
#                 --train_raw_import_dir $train_raw_import_dir \
#                 --train_formated_import_dir $train_formated_import_dir \
#                 --test_raw_import_dir $test_raw_import_dir \
#                 --train_raw_import_dir_malware $train_raw_import_dir_malware \
#                 --train_raw_import_dir_goodware $train_raw_import_dir_goodware \
#                 --test_raw_import_dir_malware $test_raw_import_dir_malware \
#                 --test_raw_import_dir_goodware $test_raw_import_dir_goodware \
#                 --goodware_import_file_directories $goodware_import_file_directories \
#                 --malware_import_file_directories $malware_import_file_directories \
#                 --extra_amount $extra_amount \
#                 --extra_malware_folder $extra_malware_directory \
#                 --append_csv $csv_output \
#                 --seed $seed
#             echo "Ending repetition number $r"
#         done
#         echo -e "Done with extra_amount=$extra_amount at train_percentage=$i \n"

#         extra_amount=$((extra_amount + step))
#     done
# done

# echo "All runs completed."
