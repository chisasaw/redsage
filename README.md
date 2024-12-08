# RedSage: Minimal Terminal Pair Programmer

**Author:** Warren Chisasa  

RedSage is a lightweight, terminal-based coding assistant that connects to LLM APIs (e.g., Claude, OpenAI) to provide real-time pair programming capabilities. Designed for developers seeking a simple yet powerful coding companion, RedSage focuses on **simplicity**, **ease of setup**, and **intuitive functionality**. 

---

## 🚀 Overview

RedSage empowers developers to write, analyze, and improve code directly from the terminal. Whether you're debugging, writing new functions, or collaborating with AI, RedSage is your go-to lightweight coding assistant.

---

## ✨ Features

- 🤖 **Multi-LLM Support**: Integrates with Claude or OpenAI APIs.
- 📂 **Intelligent File Watching**: Tracks changes in your codebase in real-time.
- 🔗 **Seamless Git Integration**: Easily manage branches and commits.
- 🖥️ **Minimal Configuration Requirements**: Simple YAML-based setup.
- 💬 **Intuitive Command-Line Interface**: Easy-to-use CLI with rich features.
- 🌐 **Multi-Language Programming Support**: Write and analyze code in various languages.

---

## 🛠️ Installation

### Prerequisites
Ensure the following are installed on your system:
- Python 3.8+
- `pip` (Python Package Manager)
- `git`

### Install via pip
```bash
pip install redsage
```

---

## ⚡ Quick Setup

### 1. Initialize Configuration
Run the following command to initialize Redsage:
```bash
redsage init
```

### 2. Set API Key
Export your API key securely using environment variables:
```bash
export REDSAGE_API_KEY=your_api_key
```

Or update the `redsage.yaml` file with your API key:
```yaml
llm:
  provider: "openai"
  api_key: "your_api_key_here"
```

---

## 📖 Usage

### Start RedSage
```bash
redsage start
```

### Available Commands
- `/help` - Show available commands.
- `/context` - Display conversation context.
- `/suggest` - Get code improvement suggestions.
- `/explain` - Explain selected code.
- `/diff` - Show current changes.
- `/save` - Save changes to a git branch.
- `/undo` - Revert the last change.
- `/switch` - Switch LLM provider.
- `/quit` - Exit RedSage.
- `/paste` - Paste code for further queries.
- `/ask` - Ask questions about pasted content. 


---

## ⚙️ Configuration

Create a `redsage.yaml` file in your project root for fine-tuned settings:
```yaml
llm:
  provider: "openai"  # or "claude"
  api_key: "${REDSAGE_API_KEY}"

watch:
  paths: ["./src"]
  ignore: ["*.pyc", "__pycache__"]

git:
  enabled: true
  branch_prefix: "redsage/"
```

---

## 🔒 Security Considerations

- **API Keys**: Stored securely in environment variables or YAML files.
- **Local File Access Only**: Redsage doesn't transmit local code to external servers unless specified by the user.
- **Git Confirmation**: Git operations require user confirmation.
- **Sanitized Input Handling**: Redsage validates all inputs to prevent injection attacks.

---

## 🧩 Dependencies

- `watchdog`
- `click`
- `anthropic`
- `openai`
- `pyyaml`
- `gitpython`
- `prompt_toolkit`

---

## 🤝 Contributing

We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create your feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request.

---

## 🗺️ Roadmap

- 🧠 Enhanced context management.
- 🌍 Support for more LLM providers.
- 📊 Advanced code analysis capabilities.
- ⚡ Performance optimizations.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📬 Contact

Warren Chisasa  
📧 Email: [warrenchisasa@gmail.com](mailto:warrenchisasa@gmail.com)  
🔗 Project Link: [GitHub Repository](https://github.com/chisasaw/redsage)