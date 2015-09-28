# encoding: utf-8
from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time


def run_workflow(work_folder, result_folder, data_folder, data_filename_pattern, job_count, sample_factor,
                 extra_args_prepare="", extra_args_subsample="", extra_args_learn="",
                 extra_args_apply_weights="", extra_args_score="", callback=None, logger=None):

    if result_folder is None:
        user = os.environ.get("USER")
        tmp_root = "/cluster/scratch_xp/public/%s/pyprophet_tmp" % user
        if not os.path.exists(tmp_root):
            os.makedirs(tmp_root)

        prefix = time.strftime("%a_%H_%M_%d_%m_%Y_")
        result_folder = tempfile.mkdtemp(dir=tmp_root, prefix=prefix)

    if work_folder is None:
        work_folder = os.path.join(result_folder, "_workfolder")

    for folder in (result_folder, work_folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
            if logger is not None:
                logger.info("created folder %s", folder)

    if logger is not None:
        logger.info("result folder at %s", result_folder)
        logger.info("work folder at %s", work_folder)

    here = os.path.dirname(os.path.abspath(__file__))
    script_template_path = os.path.join(here, "submit_jobs_template.sh")
    template = open(script_template_path, "r").read()
    if logger is not None:
        logger.info("use script template from %s", script_template_path)

    script = template.format(**locals())

    if sys.platform == "linux2":
        script = script.replace("\r\n", "\n")

    script_path = os.path.join(work_folder, "run.sh")
    with open(script_path, "w") as fp:
        fp.write(script)

    if logger is not None:
        logger.info("wrote script for submitting jobs to %s", script_path)

    if callback is not None:
        def inner():
            out = subprocess.check_output("bash run.sh", shell=True, cwd=work_folder,
                                          stderr=subprocess.STDOUT)
            callback(out, result_folder)

        thread = threading.Thread(target=inner)
        thread.start()
        if logger is not None:
            logger.info("created background thread for running the workflow script")
        return None, None, None

    else:
        if logger is not None:
            logger.info("run workflow script")
        out = subprocess.check_output("bash run.sh", shell=True, cwd=work_folder, stderr=subprocess.STDOUT)
        return out, result_folder, work_folder
