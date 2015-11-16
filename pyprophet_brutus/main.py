# encoding: utf-8
from __future__ import print_function

import os


import pkg_resources  # part of setuptools
version = tuple(map(int, pkg_resources.require("pyprophet-brutus")[0].version.split(".")))


from pyprophet_cli.common_options import (data_folder, data_filename_pattern, job_count,
                                          sample_factor, extra_group_columns, lambda_)

from click import option, echo, Path

# overwrite some options, work and result folder do not have to exist:

work_folder = option("--work-folder",
                     help="folder for intermediate results which are needed by following processing steps",
                     type=Path(file_okay=False, dir_okay=True, readable=True, writable=True),
                     required=False, default=None)

result_folder = option("--result-folder",
                       help="folder for final results",
                       type=Path(file_okay=False, dir_okay=True, writable=True),
                       required=False, default=None)

# other options:

job_slot_limit = option("--job-slot-limit",
                        help="maximum number of jobs that are allowed to run at any one time",
                        type=int,
                        default=32
                        )

extra_args_prepare = option("--extra-args-prepare", default="",
                            help="extra args for calling prepare command")
extra_args_subsample = option("--extra-args-subsample", default="",
                              help="extra args for calling subsample command")
extra_args_learn = option("--extra-args-learn", default="",
                          help="extra args for calling learn command")
extra_args_apply_weights = option("--extra-args-apply-weights", default="",
                                  help="extra args for calling apply-weights command")

extra_args_score = option("--extra-args-score", default="",
                          help="extra args for calling score command")

notification_email_address = option("--notification-email-address", default=_user_email(),
                                    help=("send result notification to this address, use 'null' to disable this "
                                          "[default={}]".format(_user_email())))

print_version = option("--version", is_flag=True, callback=print_version, expose_value=False,
                       is_eager=True, help="print version of brutus plugin")


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

    (output,
     result_folder,
     work_folder) = run_workflow(self.work_folder, self.result_folder, self.data_folder, self.data_filename_pattern,
                                 self.job_count, self.sample_factor, self.job_slot_limit,
                                 self.lambda_, self.extra_group_columns,
                                 self.extra_args_prepare,
                                 self.extra_args_subsample, self.extra_args_learn,
                                 self.extra_args_apply_weights, self.extra_args_score,
                                 callback=callback, logger=self.logger)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    echo("%d.%d.%d" % version)
    ctx.exit()


def _options():

    options = [data_folder, data_filename_pattern, job_count, sample_factor,
               job_slot_limit,
               result_folder, work_folder,
               extra_group_columns, lambda_,
               notification_email_address,
               print_version
               extra_args_prepare,
               extra_args_subsample,
               extra_args_learn,
               extra_args_apply_weights,
               extra_args_score,
               ]
    return options


def config():

    options = _options()
    help_ = """runs full pyprophet-cli workflow on brutus cluster of eth.
    """
    return "run_on_brutus", options, _run_workflow, help_
