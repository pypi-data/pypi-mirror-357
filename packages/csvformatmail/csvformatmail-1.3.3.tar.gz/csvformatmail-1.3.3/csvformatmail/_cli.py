# Copyright 2019-2021, Jean-Benoist Leger <jb@leger.tf>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import textwrap
import sys

import csvspoon
import argcomplete
import jinja2

from csvformatmail.mail import Mailer, Mail, is_gpgsm_available

try:
    from csvformatmail._version import version as __version__
except ImportError:
    __version__ = "unknown"


def parseargs():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            A tool to format mails from csv and to send them.

            Mails are formatted as f-string with namespace from csv.
            """
        ),
        epilog=textwrap.dedent(
            """
            Examples:

              - Basic one:
                - A template file can be:
                  > From: Me <my-mail-address@example.org>
                  > To: {{email}}
                  > Bcc: my-mail-address@example.org
                  > Subject: Your results
                  >
                  > Hi {{name.capitalize()}},
                  >
                  > You obtain the following result {{result}}, with the value {{"{:.1f}".format(value)}}.
                  >
                  > -- 
                  > me

                - With a csv file containg columns email, name, result, value.

                - With the command:
                    %(prog)s template.txt -t value:float listing.csv

              - More complex template file:
                  > From: Me <my-mail-address@example.org>
                  > To: {{email}}
                  > Bcc: my-mail-address@example.org
                  > Subject: Your results
                  > Attachment: {{result_file}}
                  >
                  > Hi {{name.capitalize()}},
                  >
                  > You obtain the following result {{result}}, with the value {{"{:.1f}".format(value)}}.
                  > For information, for results for the class are:
                  >  - mean: {{np.mean(allrows['value'])}}
                  >  - standard deviation: {{np.std(allrows['value'])}}
                  >
                  > -- 
                  > me
                With the command:
                    %(prog)s template.txt --np -t value:float listing.csv
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit",
    )
    parser.add_argument(
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help=argparse._("show this help message and exit"),
    )

    # Input files options group
    input_group = parser.add_argument_group("Input files options")
    input_group.add_argument(
        "-d",
        "--delim",
        dest="delim",
        default=",",
        help="CSV input file delimiter. (default: ',')",
    )
    input_group.add_argument(
        "-e",
        "--encoding-csv",
        dest="encoding_csv",
        default=None,
        help="Encoding of the CSV file. If not specified, system default encoding is used.",
    )
    input_group.add_argument(
        "-E",
        "--encoding-template",
        dest="encoding_template",
        default=None,
        help="Encoding of the template file. If not specified, system default encoding is used.",
    )

    # Formatting options group
    format_group = parser.add_argument_group("Formatting options")
    format_group.add_argument(
        "-b",
        "--before",
        action="append",
        default=[],
        help="""
            Run the following code before evaluate the expression on each row.
            Can be specified multiple times. (e.g. "import math").
            """,
    )
    format_group.add_argument(
        "--np",
        "--numpy",
        action="store_true",
        help="""
            Quick alias to `--before "import numpy as np"`
            """,
    )
    format_group.add_argument(
        "-t",
        "--type",
        action="append",
        type=csvspoon.ColType,
        default=[],
        help="""
            Apply type conversion on specified command prior to expression. The
            argument must be a column name followed by a valid Python type. See
            "--before" to define non standard type. e.g. "a_column:int" or
            "a_column:float". This option can be specified multiple time to type
            different columns.
            """,
    )
    format_group.add_argument(
        "--allrows-name",
        default="allrows",
        help="""
            Dict used to access for each column the value of all rows. See
            example. Must not be a valid column name. (default: 'allrows').
            """,
    )

    # SMTP server options group
    smtp_group = parser.add_argument_group("SMTP server options")
    smtp_group.add_argument(
        "-h",
        "--host",
        default="localhost",
        help="""
            SMTP host (default: localhost)
            """,
    )
    smtp_group.add_argument(
        "-p",
        "--port",
        default=0,
        type=int,
        help="""
            SMTP port (default: 587 if STARTTLS enabled else 25)
            """,
    )
    smtp_group.add_argument(
        "--starttls",
        default=False,
        action="store_true",
        help="""
            Enable TLS with STARTTLS.
            """,
    )
    smtp_group.add_argument(
        "-l",
        "--login",
        default=None,
        type=str,
        help="""
            Login used for authentification on SMTP server. Implies STARTTLS."
            """,
    )

    # S/MIME signing options group
    smime_group = parser.add_argument_group("S/MIME signing options")
    # Create mutually exclusive group within smime_group
    sign_method = smime_group.add_mutually_exclusive_group()
    sign_method.add_argument(
        "-s",
        "--sign",
        action="store_true",
        help="""
            Sign emails using S/MIME. Will use gpgsm if available (key selected based on From address),
            otherwise will show error message suggesting to use --sign-p12.
            """,
    )
    sign_method.add_argument(
        "--sign-gpgsm",
        action="store_true",
        help="""
            Sign emails using gpgsm. The signing key will be selected based on
            the From address in the email.
            Requires gpgsm to be installed and configured.
            """,
    )
    sign_method.add_argument(
        "--sign-p12",
        help="""
            Sign emails using a PKCS#12 (.p12) certificate file.
            Password will be prompted interactively.
            """,
        type=str,
        metavar="FILE",
    )

    parser.add_argument(
        "--without-confirm",
        action="store_true",
        help="""
            Send mails without confirmation.
            """,
    )

    parser.add_argument(
        "--wait",
        "-w",
        default=0.0,
        type=float,
        help="""
            Wait time between mail, In seconds. (default: 0s)
            """,
    )

    parser.add_argument(
        "template",
        help="""
            Template file. Must contains header, a empty line, and mail content.
            Header must contains lines From, To and Subject. Other header (as
            Bcc) can be provided.
            Special header "Attachements" can be used to specify attachments.
            Templates are jinja2 template. Each mail is a rendering of the 
            template for each row of the csv file. The template can contain 
            {{val}} to access value of csv file, or more complex construction allowed 
            by jinja2.
            """,
        type=argparse.FileType("rb"),
    )

    parser.add_argument(
        "inputcsv",
        help="""
            CSV input file specification. Can be a filename (e.g. "file.csv"), a filename
            followed a semicolon and column names separated by commas (e.g.
            "file.csv:a_colname,another_colname"). A column can be renamed while
            reading the file (e.g. "file.csv:a_colname,new_colname=old_colname").
            When column names are specified, only these columns are used, with the provided order.
            Typing can be applied, see '-t'. Delimiter can be changed, see '-d'.
            """,
        type=csvspoon.CsvFileSpec,
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    return args


def main():
    args = parseargs()

    # Handle --sign option
    if args.sign:
        if is_gpgsm_available():
            args.sign_gpgsm = True
        else:
            print(
                "Error: gpgsm is not available. To sign emails, either:\n"
                "1. Install gpgsm (usually part of gnupg2 package), or\n"
                "2. Use --sign-p12 option with a PKCS#12 certificate file",
                file=sys.stderr,
            )
            sys.exit(1)

    template_bytes = args.template.read()
    if args.encoding_template:
        template_str = template_bytes.decode(args.encoding_template)
    else:
        template_str = template_bytes.decode()
    try:
        template = jinja2.Template(template_str, undefined=jinja2.StrictUndefined)
    except Exception as exc:
        print(
            f"Error when building the template: {exc.__class__}\n{exc}", file=sys.stderr
        )
        sys.exit(1)
    input_csv = csvspoon.ContentCsv(
        filespec=args.inputcsv, delim=args.delim, encoding=args.encoding_csv
    )
    fake_global = {"__name__": "__main__"}
    before_np = ["import numpy as np"] if args.np else []
    for before in before_np + args.before:
        ast = compile(before, "<string>", "exec")
        exec(ast, fake_global)

    for t in args.type:
        t.build_type(fake_global)
        input_csv.add_type(*t.get_coltype)
    starttls = args.starttls
    password = None
    if args.login is not None:
        login = args.login
        starttls = True
    else:
        login = None
    port = args.port
    if port == 0:
        port = 587 if starttls else 25
    mailer = Mailer(
        args.host,
        port,
        starttls=starttls,
        login=login,
        password=password,
        sign_gpgsm=args.sign_gpgsm,
        sign_p12=args.sign_p12,
        p12_password=None,
    )
    rows = list(input_csv.rows_typed)
    cols = {c: [r[c] for r in rows] for c in input_csv.fieldnames}
    for row in rows:
        if args.allrows_name not in input_csv.fieldnames:
            row[args.allrows_name] = cols
        try:
            mail = Mail(template, row, fake_global)
        except Exception as exc:
            print(
                f"Error when rendering mail: {exc.__class__}\n{exc}",
                file=sys.stderr,
            )
            sys.exit(1)
        mailer.add_mail(mail)
    if args.without_confirm:
        mailer.send_mails(args.wait)
    else:
        mailer.prompt(args.wait)


if __name__ == "__main__":
    main()
