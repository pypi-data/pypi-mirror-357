# csvformatmail: A tool to format mails from csv and to send them

A simple yet powerful tool to send personalized emails using a template and CSV data.

## Installation

```bash
pipx install csvformatmail  # Recommended
# or
pip install csvformatmail
```

### Shell Completion

For bash or other shells using bash-completion:

```bash
mkdir -p ~/.local/share/bash-completion/completions
register-python-argcomplete csvformatmail > ~/.local/share/bash-completion/completions/csvformatmail
```

## Quick Start

1. Create a template (`template.txt`):
```
From: Me <sender@example.com>
To: {{email}}
Subject: Hello {{name}}

Hi {{name}},
Welcome!

Best regards,
-- 
Me
```

2. Prepare your data (`contacts.csv`):
```
name,email
Alice,alice@example.com
Bob,bob@example.com
```

3. Send emails:
```bash
csvformatmail template.txt contacts.csv
```

## Template Files

Templates use the Jinja2 syntax. The structure is:
- Email headers (From, To, Subject are mandatory)
- Empty line
- Email body

Variables from your CSV are accessed using `{{variable}}`.

If your template file uses a specific encoding (by default the system default encoding is used), see the `-E` option.

## CSV Data

The CSV file provides the data for personalizing each email. Column names in the CSV become variables in the template.

Example:
```csv
first_name,last_name,email,order_id
John,Doe,john@example.com,12345
Jane,Smith,jane@example.com,12346
```

Options:
- Change delimiter: `-d ";"` for semicolon-separated files
- Use `-e` to specify CSV encoding (by default the system default encoding is used).
- Rename columns on the fly: `data.csv:email,name=full_name`

## Sending Emails

### Local SMTP Server
```bash
csvformatmail template.txt data.csv
```

### Remote SMTP Server with authentication
```bash
csvformatmail -h smtp.example.com -l username template.txt data.csv
```

The password will be prompted interactively if needed. Authentication is always performed in an encrypted tunnel (STARTTLS). Plain text authentication without STARTTLS is deliberately not supported for security reasons.

Other server options are available, see `csvformatmail --help`.


## Attachments

Add attachments using the `Attachments` fake header:

```
From: sender@example.com
To: {{email}}
Subject: Your Document
Attachments: common.pdf, {{document}}

Please find attached your documents.
```

Corresponding CSV file:
```csv
email,document
alice@example.com,alice_report.pdf
bob@example.com,bob_report.pdf
```

The attachment paths can be either fixed or from CSV variables.

## Advanced Formatting

### Type Conversion and Formatting
Convert CSV columns to specific types for formatting:
```bash
csvformatmail -t score:float -t date:str template.txt data.csv
```

In the template, you can use the formatted value:
```
Average score: {{"{:.1f}".format(score)}}
```

### Conditional Formatting
Use Jinja2 conditional statements to customize your message:
```
Your score is {{"{:.1f}".format(score)}}/20.
{% if score >= 10 %}
Congratulations, you passed the test!
{% else %}
Unfortunately, you did not pass the test. You need at least 10/20 to pass.
{% endif %}
```

### Accessing All Rows
Use `allrows` in the template to access complete columns:
```
Average score: {{"{:.1f}".format(np.mean(allrows['score']))}}
```

Enable numpy with `--np`:
```bash
csvformatmail --np template.txt data.csv
```

### Text Formatting
Use textwrap for better text formatting:
```bash
csvformatmail -b "import textwrap" template.txt data.csv
```

Then in template:
```
{{textwrap.fill(long_text, width=72)}}
{{textwrap.indent(text, "> ")}}
```

## S/MIME Signing

### Using gpgsm
```bash
# Automatic signing using From address
csvformatmail -s template.txt data.csv

# Explicit gpgsm usage
csvformatmail --sign-gpgsm template.txt data.csv
```

### Using PKCS#12 Certificate
```bash
csvformatmail --sign-p12 cert.p12 template.txt data.csv
```

The certificate password will be prompted interactively.