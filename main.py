# encoding: utf-8
from __future__ import print_function

import os

from pyprophet_cli.core import (data_folder, data_filename_pattern,
                                 job_count, sample_factor)

from click import option


def _user_email():
    return "{}@ethz.ch".format(os.environ.get("USER"))


def _run_workflow(self):

    from run_on_lsf import run_workflow

    def send_notification(output, result_folder):
        from send_email import send_result
        send_result(from_=_user_email(), to=self.notification_email_address, output=output,
                    result_folder=result_folder, logger=self.logger)

    if self.notification_email_address != "none":
        callback = send_notification
    else:
        callback = None

    output, result_folder = run_workflow(self.data_folder, self.data_filename_pattern,
                                         self.job_count, self.sample_factor,
                                         self.extra_args_subsample, self.extra_args_learn,
                                         self.extra_args_apply_weights, self.extra_args_score,
                                         callback=callback, logger=self.logger)

def _options():

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
                      help="extra args for calling score command"),
               option("--notification-email-address", default=_user_email(),
                      help=("send result notification to this address, use 'null' to disable this "
                            "[default={}]".format(_user_email()))),
               ]
    return options


def config():

    options = _options()
    help_ = """runs full pyprophet-cli workflow on brutus cluster of eth.
    """
    return "run_on_brutus", options, _run_workflow, help_
