# encoding: utf-8
from __future__ import print_function

import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def test_0():

    data_folder = "/cluster/scratch_xp/public/schmittu"

    file_path = "{HERE}/test_data.txt".format(HERE=HERE)
    shutil.copy(file_path, data_folder + "/test_data_0.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_1.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_2.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_3.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_4.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_5.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_6.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_7.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_8.tsv")
    #os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_9.tsv")
    # os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_10.tsv")
    # os.symlink(data_folder + "/test_data_0.tsv", data_folder + "/test_data_11.tsv")
    #shutil.copy(file_path, data_folder + "/test_data_2.tsv")
    #shutil.copy(file_path, data_folder + "/test_data_3.tsv")
    #shutil.copy(file_path, data_folder + "/test_data_4.tsv")

    cmd = """bsub pyprophet-cli run_on_brutus\
            --data-folder {data_folder} \
            --data-filename-pattern 'test_data_0.tsv' \
            --job-count 1 \
            --sample-factor 0.2 \
            --statistics-mode local \
            --extra-group-column transition_group_id\
            --extra-group-column transition_group_id\
            --extra-group-column transition_group_id\
            --lambda 0.8
          """.format(**locals())

    subprocess.call(cmd, shell=True)




