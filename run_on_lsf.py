# encoding: utf-8
from __future__ import print_function

import tempfile
import os
import shutil
import subprocess
import threading
import time


def run_workflow(data_folder, data_filename_pattern, job_count, sample_factor,
                 extra_args_subsample="", extra_args_learn="",
                 extra_args_apply_weights="", extra_args_score="", callback=None, logger=None):

    user = os.environ.get("USER")
    tmp_root = "/cluster/scratch_xp/public/%s/pyprophet_tmp" % user
    if not os.path.exists(tmp_root):
        os.makedirs(tmp_root)

    #now = str(time.ctime(time.time())).split(" ")
    #weekday = now[0]
    #time_ = now[3].replace(":", "_")

    #prefix = "%s_%s_" % (weekday, time_)
    prefix = time.strftime("%a_%H_%M_%d_%m_%Y_")

    root_folder = tempfile.mkdtemp(dir=tmp_root, prefix=prefix)
    if logger is not None:
        logger.info("created workflow root folder at %s", root_folder)
    message_folder = os.path.join(root_folder, "messages")
    work_folder = os.path.join(root_folder, "workfolder")
    result_folder = os.path.join(work_folder, "results")

    if not os.path.exists(message_folder):
        os.makedirs(message_folder)
        if logger is not None:
            logger.info("created message folder at %s", message_folder)

    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
        if logger is not None:
            logger.info("created work folder at %s", work_folder)

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
        if logger is not None:
            logger.info("created result folder at %s", result_folder)

    if logger is not None:
        logger.info("%s is now %s", "message_folder", message_folder)
        logger.info("%s is now %s", "work_folder", work_folder)
        logger.info("%s is now %s", "result_folder", result_folder)

    here = os.path.dirname(os.path.abspath(__file__))
    script_template_path = os.path.join(here, "submit_jobs_template.sh")
    template = open(script_template_path, "r").read()
    if logger is not None:
        logger.info("use script template from %s", script_template_path)

    script = template.format(**locals())

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
        return None, None

    else:
        if logger is not None:
            logger.info("run workflow script")
        out = subprocess.check_output("bash run.sh", shell=True, cwd=work_folder, stderr=subprocess.STDOUT)
        return out, result_folder
