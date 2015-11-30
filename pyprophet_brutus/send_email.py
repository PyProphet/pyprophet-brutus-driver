# encoding: utf-8
from __future__ import print_function

import glob
import os
import smtplib
import tempfile
import zipfile

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def _zip(data, name):
    """creates temporary zipfile with one entry named "name", "data" is the content
    and returns the content of the zipfile as a binary string.
    """
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "data.zip")
    with zipfile.ZipFile(path, "w") as fh:
        fh.writestr(name, data)
    with open(path, "rb") as fh:
        return fh.read()


def _create_msg(from_, to):
    msg = MIMEMultipart()
    msg['Subject'] = 'pyrophet workflow on brutus.ethz.ch finished'
    msg['From'] = from_
    msg['To'] = to
    return msg


def _read_summ_stat(result_folder):

    path = os.path.join(result_folder, "summary_stats.txt")
    if os.path.exists(path):
        with open(path, "r") as fp:
            txt = fp.read()
    else:
        txt = "no summary stat created"
    return txt


def _create_email_text(msg, result_folder):
    # create body
    pathes = []
    for name in os.listdir(result_folder):
        path = os.path.join(result_folder, name)
        pathes.append(path)

    pathes.sort()

    txt = _read_summ_stat(result_folder)

    txt += "\n\npyprophet created the following result files: \n\n    %s" % "\n    ".join(pathes)
    txt += "\n\n"

    path = os.path.join(result_folder, "resource_summary.txt")
    if os.path.exists(path):
        with open(path, "r") as fp:
            txt += fp.read()
    else:
        txt += "no resource_summary file created !"

    msg.attach(MIMEText(txt))


def _build_full_email(from_, to, output, result_folder):
    msg = _create_msg(from_, to)
    _create_email_text(msg, result_folder)
    _attach_lsf_output(msg, output)
    _attach_report_pdfs(msg, result_folder)
    return msg


def _build_stripped_email(from_, to, output, result_folder):
    msg = _create_msg(from_, to)
    _create_email_text(msg, result_folder)
    _attach_report_pdfs(msg, result_folder)
    return msg


def send_result(from_, to, output, result_folder, logger):

    # we try to send email in decreasing size until mailserver accepts:
    builders = [_build_full_email, _build_stripped_email]

    for builder in builders:
        msg = builder(from_, to, output, result_folder)
        try:
            s = smtplib.SMTP('localhost')
            s.sendmail(from_, to, msg.as_string())
            s.quit()
            logger.info("email server accepted email created by %s" % builder)
            break
        except smtplib.SMTPSenderRefused, e:
            logger.warn("email server refused email created by %s" % builder)
            if e.smtp_code == 552:   # refused because email too big.
                continue

    logger.info("connected successfully to mail server")
    logger.info("sent email from %s to %s", from_, to)


def _attach_lsf_output(msg, output):

    # create attachment: attach zipped lsf output

    zipped_output = MIMEBase('application', 'zip')
    zipped_output.set_payload(_zip(output, "output.txt"))
    encoders.encode_base64(zipped_output)
    zipped_output.add_header('Content-Disposition', 'attachment', filename='recoreded_lsf_output.zip')
    msg.attach(zipped_output)


def _attach_report_pdfs(msg, result_folder):

    report_paths = glob.glob(os.path.join(result_folder, "report*.pdf"))

    if not report_paths:
        return

    temp_zipfile_path = os.path.join(tempfile.mkdtemp(), "reports.zip")
    with zipfile.ZipFile(temp_zipfile_path, "w") as fh:
        for report_path in report_paths:
            name = os.path.basename(report_path)
            fh.writestr(name, open(report_path).read())
    payload = open(temp_zipfile_path, "rb").read()
    zipped_reports = MIMEBase('application', 'zip')
    zipped_reports.set_payload(payload)
    encoders.encode_base64(zipped_reports)
    zipped_reports.add_header('Content-Disposition', 'attachment', filename='reports.zip')
    msg.attach(zipped_reports)

    with open(report_paths[0], "rb") as fp:
        data = fp.read()
        pdf = MIMEApplication(data, _subtype="pdf")
        pdf.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', "first report.pdf"))
        msg.attach(pdf)


if __name__ == "__main__":
    import logging
    from_ = to = "schmittu@ethz.ch"
    output = open("o", "r").read()
    result_folder = "/cluster/scratch_xp/public/collinsb/pyprophet_tmp/Sun_18_44_15_11_2015_ydjJrf"
    # "/cluster/scratch_xp/public/collinsb/pyprophet_tmp/Sun_18_44_15_11_2015_ydjJrf/"
    send_result(from_, to, output, result_folder, logger=logging)
