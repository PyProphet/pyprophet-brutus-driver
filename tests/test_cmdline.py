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
    shutil.copy(file_path, data_folder + "/test_data_1.tsv")
    shutil.copy(file_path, data_folder + "/test_data_2.tsv")
    shutil.copy(file_path, data_folder + "/test_data_3.tsv")
    shutil.copy(file_path, data_folder + "/test_data_4.tsv")

    cmd = """pyprophet-cli run_on_brutus --data-folder {data_folder} \
                                         --data-filename-pattern '*.tsv' \
                                         --job-count 3 \
                                         --sample-factor 0.2 \
          """.format(**locals())

    subprocess.call(cmd, shell=True)




