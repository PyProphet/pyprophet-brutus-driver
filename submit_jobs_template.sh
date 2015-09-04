#!/bin/bash


R="-W 3:00 -R rusage[scratch=100000] -R lustre"

DATA_FOLDER={data_folder}
WORK_FOLDER={work_folder}

JC={job_count}


GROUP={work_folder}

MSG_FOLDER={message_folder}


bsub -o $MSG_FOLDER/check_out -cwd $GROUP -J "check" $R -g $GROUP <<EOL
    pyprophet-cli check --data-folder $DATA_FOLDER \
                        --data-filename-pattern "{data_filename_pattern}"
EOL

bsub -o $MSG_FOLDER/subsample_out -J "subsample[1-$JC]" -w "done(check)" $R -g $GROUP <<EOL
     pyprophet-cli subsample --data-folder $DATA_FOLDER \
                             --data-filename-pattern "{data_filename_pattern}" \
                             --working-folder $WORK_FOLDER \
                             --job-number \$LSB_JOBINDEX \
                             --job-count \$LSB_JOBINDEX_END \
                             --sample-factor {sample_factor} \
                             --ignore-invalid-scores \
                             --local-folder \$TMPDIR \
                             --chunk-size 1000000 \
                             {extra_args_subsample}
EOL

bsub -o $MSG_FOLDER/learn_out -J "learn" -w "done(subsample)" -g $GROUP $R <<EOL
     pyprophet-cli learn     --working-folder $WORK_FOLDER \
                             {extra_args_learn}
EOL

bsub -o $MSG_FOLDER/apply_weights_out -J "apply_weights[1-$JC]" -w "done(learn)" $R -g $GROUP <<EOL
     pyprophet-cli apply_weights --data-folder $DATA_FOLDER \
                                 --data-filename-pattern "{data_filename_pattern}" \
                                 --working-folder $WORK_FOLDER \
                                 --job-number \$LSB_JOBINDEX \
                                 --job-count \$LSB_JOBINDEX_END \
                                 --local-folder \$TMPDIR \
                                 --chunk-size 1000000 \
                                 {extra_args_apply_weights}
EOL

bsub -o $MSG_FOLDER/scorer_out -J "score[1-$JC]" -w "done(apply_weights)" $R -g $GROUP <<EOL
     pyprophet-cli score --data-folder $DATA_FOLDER \
                         --data-filename-pattern "{data_filename_pattern}" \
                         --working-folder $WORK_FOLDER \
                         --job-number \$LSB_JOBINDEX \
                         --job-count \$LSB_JOBINDEX_END \
                         --local-folder \$TMPDIR \
                         --overwrite-results \
                         --chunk-size 1000000 \
                         {extra_args_score}
EOL


bsub -oo $MSG_FOLDER/final_out -J "error" \
     -w "exit(score)||exit(check)||exit(subsample)||exit(learn)||exit(apply_weights)"\
     -g $GROUP "echo workflow failed"

bsub -oo $MSG_FOLDER/final_out -J "success"\
     -w "done(score)"\
     -g $GROUP "echo workflow finished"

# block until done
bsub -K -w "done(success) || done(error)" -g $GROUP "echo finalized"

bkill -g $GROUP 0

for FILE in check_out subsample_out learn_out apply_weights_out scorer_out final_out; do
    FULLPATH=$MSG_FOLDER/$FILE
    echo
    if test -f $FULLPATH; then
        echo CONTENT OF $FULLPATH
        echo
        # indent:
        cat $FULLPATH | sed 's/^/||     /'
    else
        echo $FULLPATH is empty
    fi
    echo
    echo "----------------------------------------------------------------------------------"
done;

echo $WORK_FOLDER/results
