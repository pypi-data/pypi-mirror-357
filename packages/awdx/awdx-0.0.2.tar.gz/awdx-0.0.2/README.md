# awdx

**awdx** (AWS DevOps X) is a next-generation, human-friendly CLI tool for AWS DevSecOps. It helps you manage, automate, and secure your AWS environment with simple, interactive commands and smart suggestions.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Status](#status)

---

## Features
- **Profile Management:** Create, switch, and validate AWS profiles interactively.
- **Security Audits:** Scan for misconfigurations, exposed secrets, and risky permissions.
- **Cost Insights:** Get clear summaries of your AWS spending.
- **Resource Checks:** Instantly check S3 buckets, security groups, IAM users, and more for best practices.
- **Automation:** Run common DevSecOps tasks with a single, smart command.
- **Suggestions:** Receive actionable best-practice tips after every action.
- **Human-Friendly CLI:** Simple, memorable commands and interactive prompts.
- **Future:** AI/NLP-powered natural language commands.

---

## Requirements
- Python 3.8+
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [typer](https://typer.tiangolo.com/)

---

## Installation

### From Source
```bash
pip install .
```

### From PyPI (after publishing)
```bash
pip install awdx
```

---

## Usage

Show help and available commands:
```bash
awdx --help
```

List all AWS profiles:
```bash
awdx profile list
```

Show the current AWS profile:
```bash
awdx profile current
```

Switch to a different AWS profile:
```bash
awdx profile switch <profile>
```

Add a new AWS profile interactively:
```bash
awdx profile add
```

FUTURE commands:
```bash
awdx check s3             # Check S3 buckets for best practices
awdx suggest security     # Get security suggestions
```

Example interactive session:
```
$ awdx profile list
👤 Found 3 profiles:
🎯 👤 default (current)
👤 devops
👤 prod

$ awdx s3 list
Found 2 public buckets! It's best to block public access. Want to fix this now? (Y/n)

$ awdx security suggest
Tip: 3 IAM users don't have MFA enabled. Would you like to send them a reminder email?
```

---

## Project Status

Early development. See `docs/` for design and installation details. 