# encoding: utf-8
from __future__ import print_function

import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_result(from_, to, output, result_folder, logger):

    msg = MIMEMultipart()
    msg['Subject'] = 'pyrophet workflow on brutus.ethz.ch finished'
    msg['From'] = from_
    msg['To'] = to

    # create body
    pathes = []
    for name in os.listdir(result_folder):
        path = os.path.join(result_folder, name)
        pathes.append(path)

    pathes.sort()

    txt = "pyprophet created the following result files: \n\n    %s" % "\n    ".join(pathes)
    txt += "\n\n"

    path = os.path.join(result_folder, "resource_summary")
    if os.path.exists(path):
        with open(path, "r") as fp:
            txt += fp.read()
    else:
        txt += "no resource_summary file created !"

    msg.attach(MIMEText(txt))

    # create attachment
    data = MIMEText(output)
    data.add_header('Content-Disposition', 'attachment', filename="recorded_lsf_output.txt")
    msg.attach(data)

    s = smtplib.SMTP('localhost')
    logger.info("connected successfully to mail server")
    s.sendmail(from_, to, msg.as_string())
    logger.info("sent email from %s to %s", from_, to)
    s.quit()
