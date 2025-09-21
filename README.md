# Mailcast

A specification-based email merging tool

Mailcast is designed to simplify your mail-sending workflow. By using a clean and human-readable YAML file, you can effortlessly define recipient lists, email content, and customization details without writing a single line of code.

## ✨ Features

- **YAML-based Specification**\
  Define your email sending tasks using a clear, intuitive YAML format, eliminating the need for complex interfaces or scripts.
- **Single Command Execution**\
  A single command is all it takes to kick off the entire mailing process.
- **Robust Data Validation**\
  Includes a JSON Schema for instant syntax checking and auto-completion when paired with a YAML Language Server, ensuring your specification is always correct.

## 🌳 Message Tree

```
message/rfc822
└-- multipart/mixed
    ├-- multipart/alternative
    │   ├-- multipart/related
    │   │   ├-- text/html
    │   │   └-- */* (inline attachment)
    │   └- text/plain
    └-- */* (attachment)
```

## 🚀 Quick Start

### Basic Usage

Just one command will run Mailcast directly. Be sure you have uv installed.

```sh
uvx mailcast register mailcast.yaml
```

### Advanced Usage

For more advanced customization or integration into your existing Python projects, you can install Mailcast as a library from PyPI using any package manager.

```sh
uv add mailcast
```

Once installed, you can import and use the library's functions directly in your Python code for full control over the process.

## ✍️ Enhanced Editing Experience

For an improved editing experience with your `mailcast.yaml` file, we highly recommend installing a [YAML Language Server](https://github.com/redhat-developer/yaml-language-server) client. This allows your code editor to leverage the included JSON Schema for real-time validation, autocompletion, and helpful hints.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.
