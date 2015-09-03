#!/bin/bash


# ROOT_FOLDER=/cluster/scratch_xp/public/schmittu

RESOURCE="-R rusage[scratch=50000] -R lustre"

DATA_FOLDER={data_folder}
WORK_FOLDER={work_folder}

NUM_WORKERS={job_count}

# import fake data:
# cp tests/data/test_data.txt $DATA_FOLDER/test_data_0.txt
# cp tests/data/test_data.txt $DATA_FOLDER/test_data_1.txt


GROUP={work_folder}

MSG_FOLDER={message_folder}


bsub -o $MSG_FOLDER/check_out -cwd $GROUP -J"check" $RESOURCE -g $GROUP <<EOL
    pyprophet-cli check --data-folder $DATA_FOLDER \
                        --data-filename-pattern "*.txt"
EOL

bsub -o $MSG_FOLDER/subsample_out -J"subsample[1-$NUM_WORKERS]" -w"done(check)" $RESOURCE -g $GROUP <<EOL
     pyprophet-cli subsample --data-folder $DATA_FOLDER \
                             --data-filename-pattern "{data_filename_pattern}" \
                             --working-folder $WORK_FOLDER \
                             --job-number \$LSB_JOBINDEX \
                             --job-count \$LSB_JOBINDEX_END \
                             --sample-factor {sample_factor} \
                             --ignore-invalid-scores \
                             --local-folder \$TMPDIR \
                             {extra_args_subsample}
EOL

bsub -o $MSG_FOLDER/learn_out -J"learn" -w"done(subsample)" -g $GROUP <<EOL
     pyprophet-cli learn     --working-folder $WORK_FOLDER \
                             {extra_args_learn}
EOL

bsub -o $MSG_FOLDER/apply_weights_out -J"apply_weights[1-$NUM_WORKERS]" -w"done(learn)" $RESOURCE -g $GROUP <<EOL
     pyprophet-cli apply_weights --data-folder $DATA_FOLDER \
                                 --data-filename-pattern "{data_filename_pattern}" \
                                 --working-folder $WORK_FOLDER \
                                 --job-number \$LSB_JOBINDEX \
                                 --job-count \$LSB_JOBINDEX_END \
                                 --local-folder \$TMPDIR \
                                 {extra_args_apply_weights}
EOL

bsub -o $MSG_FOLDER/scorer_out -J"score[1-$NUM_WORKERS]" -w"done(apply_weights)" $RESOURCE -g $GROUP <<EOL
     pyprophet-cli score     --data-folder $DATA_FOLDER \
                             --data-filename-pattern "{data_filename_pattern}" \
                             --working-folder $WORK_FOLDER \
                             --job-number \$LSB_JOBINDEX \
                             --job-count \$LSB_JOBINDEX_END \
                             --local-folder \$TMPDIR \
                             --overwrite-results \
                             {extra_args_score}
EOL


bsub -J"error"  -w"exit(score)||exit(check)||exit(subsample)||exit(learn)||exit(apply_weights)" -g $GROUP "echo failed"
bsub -J"done"  -w"done(score)" -g $GROUP "echo done"

# block until done
bsub -K -w"done(score) || done(error)" -g $GROUP "echo finalized"

bkill -g $GROUP 0

for FILE in subsample_out learn_out apply_weights_out scorer_out; do
    FULLPATH=$MSG_FOLDER/$FILE
    echo
    if test -f $FULLPATH; then
        echo CONTENT OF $FULLPATH
        echo
        cat $FULLPATH
    else
        echo $FULLPATH is empty
    fi
    echo
    echo "----------------------------------------------------------------------------------"
done;

echo $WORK_FOLDER/results
