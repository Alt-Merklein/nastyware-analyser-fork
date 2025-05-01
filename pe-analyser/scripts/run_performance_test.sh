#!/bin/bash

# ====== CONFIG ======
python_ver="python"
script="run_performance_test.py"
base_seed=42   # Choose any integer number
# -----------
# You must set at least these four directories' paths in your machine 
nastyware_dir="/home/ceao/Downloads/performance_test/performance_test/nastyware-analyser-fork"
nastyware_files_mix="/home/ceao/Downloads/performance_test/performance_test/files/nastyware-files-mix"
working_dir="/home/ceao/Downloads/performance_test/performance_test/files/nastyware-files-mix/pipeline"
csv_output="/home/ceao/Downloads/performance_test/performance_test/performance_results.csv" # Output file's path
# -----------

train_raw_import_dir="${working_dir}/train-set/raw-import-files-mix/"
train_formated_import_dir="${working_dir}/train-set/formated-import-files-mix/"
train_raw_import_dir_malware="${working_dir}/train-set/raw-import-files-malware/"
train_raw_import_dir_goodware="${working_dir}/train-set/raw-import-files-goodware/"

test_raw_import_dir="${working_dir}/test-set/raw-import-files-mix/"
test_raw_import_dir_malware="${working_dir}/test-set/raw-import-files-malware/"
test_raw_import_dir_goodware="${working_dir}/test-set/raw-import-files-goodware/"

goodware_import_file_directories="${nastyware_files_mix}/goodware-mix/"
malware_import_file_directories="${nastyware_files_mix}/malware-mix/"

extra_malware_directory="${nastyware_files_mix}/extra-malware/"

# ====== TEST PARAMETER AND OUTPUT ======
# Set the parameters as you want to test

train_percentage=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9)
# train_percentage=(0.001 0.002 0.003 0.004 0.005 0.006 0.007 0.008 0.009) # Use for testing adjustments at the script

step=100        # Samples' increasing pace
max_extra=1400   # Maximum extra malware samples
# extra_amount=0 --- Changes must be made in the first line of 'for' loop
reps=3          # Times each sample's length will run to get its metrics

# -----------------------------

# ====== CREATE DIRECTORIES WHICH DON'T EXISTS =====
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
)

for d in "${dirs[@]}"; do
  if [ ! -d "$d" ]; then
    echo "Creating directory: $d"
    mkdir -p "$d"
  fi
done

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
                --extra_amount $extra_amount \
                --extra_malware_folder $extra_malware_directory \
                --append_csv $csv_output \
                --seed $seed
            echo "Ending repetition number $r"
        done
        echo -e "Done with extra_amount=$extra_amount at train_percentage=$i \n"

        extra_amount=$((extra_amount + step))
    done
done

echo "All runs completed."
