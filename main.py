# encoding: utf-8
from __future__ import print_function

from pyprophet_jobs.core import (data_folder, data_filename_pattern,
                                 job_count, sample_factor)

from click import option


def run(self):
    print("HI")


def config():

    options = [data_folder, data_filename_pattern, job_count, sample_factor,
               option("--extra-args-check", default="",
                      help="extra args for calling check command"),
               option("--extra-args-subsample", default="",
                      help="extra args for calling subsample command"),
               option("--extra-args-learn", default="",
                      help="extra args for calling learn command"),
               option("--extra-args-apply-weights", default="",
                      help="extra args for calling apply-weights command"),
               option("--extra-args-score", default="",
                      help="extra args for calling score command"), ]

    help_ = "help"
    return "run_on_brutus_eth", options, run, help_
