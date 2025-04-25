@echo off
REM ====== CONFIG ======
set PYTHON=python
set SCRIPT=run_performance_test.py

set TRAIN_PERCENTAGE=0.005

set NASTYWARE_DIR=/Users/Guilherme/Desktop/Academic/ITA/PROF/5oPeriodo/TG/nastyware-analyser-fork/
set WORKING_DIR=/archive/files/nastyware-files-mix/pipeline/

set TRAIN_RAW_IMPORT_DIR=%WORKING_DIR%train-set/raw-import-files-mix/
set TRAIN_FORMATED_IMPORT_DIR=%WORKING_DIR%train-set/formated-import-files-mix/
set TRAIN_RAW_IMPORT_DIR_MALWARE=%WORKING_DIR%train-set/raw-import-files-malware/
set TRAIN_RAW_IMPORT_DIR_GOODWARE=%WORKING_DIR%train-set/raw-import-files-goodware/

set TEST_RAW_IMPORT_DIR=%WORKING_DIR%test-set/raw-import-files-mix/
set TEST_RAW_IMPORT_DIR_MALWARE=%WORKING_DIR%test-set/raw-import-files-malware/
set TEST_RAW_IMPORT_DIR_GOODWARE=%WORKING_DIR%test-set/raw-import-files-goodware/

set GOODWARE_IMPORT_FILE_DIRECTORIES=/archive/files/nastyware-files-mix/goodware-mix/
set MALWARE_IMPORT_FILE_DIRECTORIES=/archive/files/nastyware-files-mix/malware-mix/

set EXTRA_MALWARE_DIRECTORY=/archive/files/nastyware-files-mix/extra-malware/

set STEP=10
set MAX_EXTRA=20
set CSV_OUTPUT=performance_results.csv

setlocal enabledelayedexpansion
set EXTRA_AMOUNT=0

:loop
if %EXTRA_AMOUNT% gtr %MAX_EXTRA% goto end

echo Running with EXTRA_AMOUNT=%EXTRA_AMOUNT%


REM ====== RUN SCRIPT ======
%PYTHON% %SCRIPT% ^
    --train_percentage %TRAIN_PERCENTAGE% ^
    --nastyware_dir %NASTYWARE_DIR% ^
    --working_dir %WORKING_DIR% ^
    --train_raw_import_dir %TRAIN_RAW_IMPORT_DIR% ^
    --train_formated_import_dir %TRAIN_FORMATED_IMPORT_DIR% ^
    --test_raw_import_dir %TEST_RAW_IMPORT_DIR% ^
    --train_raw_import_dir_malware %TRAIN_RAW_IMPORT_DIR_MALWARE% ^
    --train_raw_import_dir_goodware %TRAIN_RAW_IMPORT_DIR_GOODWARE% ^
    --test_raw_import_dir_malware %TEST_RAW_IMPORT_DIR_MALWARE% ^
    --test_raw_import_dir_goodware %TEST_RAW_IMPORT_DIR_GOODWARE% ^
    --goodware_import_file_directories %GOODWARE_IMPORT_FILE_DIRECTORIES% ^
    --malware_import_file_directories %MALWARE_IMPORT_FILE_DIRECTORIES% ^
    --extra_amount %EXTRA_AMOUNT% ^
    --extra_malware_folder %EXTRA_MALWARE_DIRECTORY% ^
    --append_csv %CSV_OUTPUT%

set /a EXTRA_AMOUNT+=%STEP%
goto loop

:end
echo All runs completed.
pause
