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

# kill all pending jobs
bkill -g $GROUP 0


for STEP in check subsample learn apply_weights scorer final; do
    FILE=$STEP\_out
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


R_SUMMARY=$WORK_FOLDER/results/resource_summary

echo TIMELINE >> $R_SUMMARY
echo >> $R_SUMMARY
(
    FMT="    %s %15s %s %s\n"
    for STEP in check subsample learn apply_weights scorer final; do
        FILE=$STEP\_out
        FULLPATH=$MSG_FOLDER/$FILE
        if test -f $FULLPATH; then
            grep -e ^Started\ at  $FULLPATH | cut -d" " -f7- | xargs -L1 -i printf "$FMT" {{}} $STEP start
            grep -e ^Results\ reported\ at  $FULLPATH | cut -d" " -f8- | xargs -L1 -i printf "$FMT" {{}} $STEP end
        fi
    done
) | sort >> $R_SUMMARY

echo >> $R_SUMMARY
echo resource summary for job group $GROUP >> $R_SUMMARY
echo >> $R_SUMMARY

for STEP in check subsample learn apply_weights scorer final; do
    FILE=$STEP\_out
    FULLPATH=$MSG_FOLDER/$FILE
    if test -f $FULLPATH; then
        echo >> $R_SUMMARY
        echo $STEP >> $R_SUMMARY
        sed '1,/Resource usage summary:/d;/The output (if any) follows/,$d' $FULLPATH >> $R_SUMMARY
        echo >> $R_SUMMARY
    fi;
done

echo $WORK_FOLDER/results

