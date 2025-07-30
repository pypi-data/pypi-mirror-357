#!/usr/bin/python3

import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
import re
import sys
import subprocess
import textwrap
from getpass import getpass
import pathlib

import jinja2


def read_template(fn):
    with open(fn) as f:
        template = "".join(line for line in f)
    return template


def _extract_email_from_header(header_value):
    """Extract email address from a header value like 'Name <email@example.com>'"""
    match = re.search(r"<([^>]+)>", header_value)
    if match:
        return match.group(1)
    return header_value.strip()


class Mail:
    def __init__(self, template: jinja2.Template, row: dict, glob: dict):
        self._text = ""
        self._header = {}
        self._attachments = []
        formatted_mail = template.render(glob | row)
        header = True
        parser = re.compile("^([^:]+): (.*)$")
        for line in formatted_mail.splitlines():
            if header:
                m = parser.match(line)
                if m:
                    k, v = m.groups()
                    if k.lower() in (
                        "attachment",
                        "attachments",
                        "attachement",
                        "attachements",
                    ):
                        for path_str in v.split(","):
                            path = pathlib.Path(path_str.strip())
                            if not path.exists():
                                raise ValueError(f"Attachment file not found: {path}")
                            self._attachments.append(path)
                    else:
                        self._header[k] = v
            else:
                self._text += line + "\n"
            if not line and self._header:
                header = False
        lower_headers = set(h.lower() for h in self._header)
        if "from" not in lower_headers:
            raise ValueError('invalid mail, "From" header must be specified')
        if "to" not in lower_headers:
            raise ValueError('invalid mail, "To" header must be specified')
        if "subject" not in lower_headers:
            raise ValueError('invalid mail, "Subject" header must be specified')

        self.from_address = _extract_email_from_header(self._header.get("From", ""))

    def __str__(self):
        attachments_str = (
            ""
            if not self._attachments
            else f"Attachment: {self._attachments[0]}\n"
            if len(self._attachments) == 1
            else "Attachments:\n"
            + "\n".join(f"  {path}" for path in self._attachments)
            + "\n"
        )

        ret = (
            "\n".join(f"{k}: {v}" for k, v in self._header.items())
            + "\n"
            + attachments_str
            + "\n\n"
            + self._text
        )
        return ret

    def to_email(self) -> MIMEText | MIMEMultipart:
        if not self._attachments:
            msg = MIMEText(self._text)
        else:
            msg = MIMEMultipart()
            msg.attach(MIMEText(self._text))

            for path in self._attachments:
                with open(path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=path.name)

                part["Content-Disposition"] = f'attachment; filename="{path.name}"'
                msg.attach(part)

        for k, v in self._header.items():
            msg[k] = v
        return msg


class Mailer:
    def __init__(
        self,
        host="localhost",
        port=25,
        starttls=False,
        login=None,
        password=None,
        progress=True,
        sign_gpgsm=None,
        sign_p12=None,
        p12_password=None,
    ):
        self._host = host
        self._port = port
        self._starttls = starttls
        self._login = login
        self._password = password
        self._progress = progress
        self._mails = []
        self._sign_gpgsm = sign_gpgsm
        self._sign_p12 = sign_p12
        self._p12_password = p12_password

    def add_mail(self, mail):
        self._mails.append(mail)

    def _prepare_message_for_signing(
        self, message: MIMEText | MIMEMultipart
    ) -> tuple[MIMEMultipart, bytes]:
        """Common preparation for both signing methods"""
        outer = MIMEMultipart(
            _subtype="signed", protocol="application/pkcs7-signature", micalg="sha-384"
        )

        skip_headers = {"content-type", "mime-version", "content-transfer-encoding"}

        for k, v in message.items():
            if k.lower() not in skip_headers:
                outer[k] = v
                del message[k]

        outer.attach(message)

        content_to_sign = (
            message.as_string()
            .replace("\r\n", "\n")
            .replace("\n", "\r\n")
            .encode("utf-8")
        )

        return outer, content_to_sign

    def _create_signature_part(self, signature: bytes) -> MIMEApplication:
        """Create the signature attachment part"""
        sig_part = MIMEApplication(
            signature,
            _subtype="pkcs7-signature",
            protocol="application/pkcs7-signature",
            name="smime.p7s",
        )
        sig_part.add_header("Content-Disposition", "attachment", filename="smime.p7s")
        return sig_part

    def _sign_message_p12(
        self, message: MIMEText | MIMEMultipart
    ) -> MIMEText | MIMEMultipart:
        if not self._sign_p12 or not self._p12_password:
            raise ValueError("PKCS#12 certificate path and password are required")

        from cryptography.hazmat.primitives.serialization import pkcs12
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.serialization import Encoding
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import pkcs7

        with open(self._sign_p12, "rb") as f:
            (
                private_key,
                certificate,
                additional_certs,
            ) = pkcs12.load_key_and_certificates(f.read(), self._p12_password.encode())

        outer, content_to_sign = self._prepare_message_for_signing(message)

        options = [pkcs7.PKCS7Options.DetachedSignature]
        signature = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(content_to_sign)
            .add_signer(certificate, private_key, hashes.SHA384())
            .sign(encoding=Encoding.DER, options=options)
        )

        sig_part = self._create_signature_part(signature)
        outer.attach(sig_part)

        return outer

    def _sign_message_gpgsm(
        self, message: MIMEText | MIMEMultipart, signing_id: str
    ) -> MIMEText | MIMEMultipart:
        """Sign a message using gpgsm"""
        signing_id = "jean-benoist.leger@hds.utc.fr"
        outer, content_to_sign = self._prepare_message_for_signing(message)

        gpgsm = subprocess.Popen(
            [
                "gpgsm",
                "--detach-sign",
                "--local-user",
                signing_id,
                "--include-certs",
                "1",
                "--digest-algo",
                "SHA384",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        signature, stderr = gpgsm.communicate(input=content_to_sign)

        if gpgsm.returncode != 0:
            raise RuntimeError(f"GPGSM signing failed: {stderr.decode()}")

        sig_part = self._create_signature_part(signature)
        outer.attach(sig_part)

        return outer

    def send_mails(self, wait=0):
        if self._sign_p12 and not self._p12_password:
            self._p12_password = getpass("PKCS#12 certificate password: ")

        if self._login is not None and self._password is None:
            self._password = getpass(f"SMTP password for user {self._login}: ")

        ngroups = len(self._mails) // 25 + 1
        i = 0
        for group in range(ngroups):
            mailserver = smtplib.SMTP(self._host, self._port)
            mailserver.ehlo()
            if self._starttls:
                mailserver.starttls()
                if self._login is not None and self._password is not None:
                    mailserver.login(self._login, self._password)
            for mail in self._mails[group::ngroups]:
                msg = mail.to_email()

                if self._sign_gpgsm:
                    signed_data = self._sign_message_gpgsm(msg, mail.from_address)
                    msg = signed_data
                elif self._sign_p12:
                    signed_data = self._sign_message_p12(msg)
                    msg = signed_data

                mailserver.send_message(msg)
                i += 1
                if self._progress:
                    print(
                        f"\rSending mails… {i}/{len(self._mails)} ",
                        end="",
                        file=sys.stderr,
                    )
                time.sleep(wait)
            del mailserver
        self._mails.clear()
        if self._progress:
            print("\r                                      \r", end="", file=sys.stderr)

    def _show_mails_in_pager(self):
        pager = os.environ.get("PAGER", "less")
        sp = subprocess.Popen((pager,), stdin=subprocess.PIPE)

        mail_format = textwrap.dedent(
            """\
            #
            # Mail {i}
            #
            {mail}
        """
        )

        mails = "\n".join(
            mail_format.format(i=i, mail=mail) for i, mail in enumerate(self._mails)
        )
        sp.stdin.write(mails.encode())
        sp.communicate()

    def prompt(self, wait=0):
        while True:
            print(
                f"Loaded {len(self._mails)} mails. What do you want to do with?",
                file=sys.stderr,
            )
            print(" - show", file=sys.stderr)
            print(" - send", file=sys.stderr)
            print(" - quit", file=sys.stderr)
            try:
                choice = input("Choice: ")
            except EOFError:
                choice = "quit"

            if choice == "quit":
                return None
            elif choice == "send":
                validation = "I want to send {number} mails."
                print(
                    f'To confirm, type "{validation.format(number="<number>")}"',
                    file=sys.stderr,
                )
                sentence = input("Confirmation: ")
                if sentence == validation.format(number=len(self._mails)):
                    self.send_mails(wait)
                    print("Done", file=sys.stderr)
                    return None
                print("Not confirmed", file=sys.stderr)
                continue
            elif choice == "show":
                try:
                    self._show_mails_in_pager()
                except BrokenPipeError:
                    pass
                continue
            print("Incorrect input.\n", file=sys.stderr)


def is_gpgsm_available():
    """Check if gpgsm is available on the system"""
    try:
        subprocess.run(["gpgsm", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
