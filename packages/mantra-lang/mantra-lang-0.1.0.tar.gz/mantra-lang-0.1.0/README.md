# 🕉️ Mantra Programming Language

<div align="center">

**A Sanskrit-inspired programming language for concise, expressive code**

*"कम शब्द, अधिक कार्य" (Less Words, More Work)*

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/codecravings/mantra-lang.svg)](https://github.com/codecravings/mantra-lang/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/codecravings/mantra-lang.svg)](https://github.com/codecravings/mantra-lang/network)
[![Issues](https://img.shields.io/github/issues/codecravings/mantra-lang.svg)](https://github.com/codecravings/mantra-lang/issues)

**[📚 Documentation](https://github.com/codecravings/mantra-lang/wiki) • [🚀 Quick Start](#-quick-start) • [💡 Examples](#-examples) • [🤝 Contributing](#-contributing)**

</div>

---

## 🌟 What is Mantra?

Mantra is a revolutionary programming language that brings the elegance and precision of Sanskrit to modern software development. With intuitive keywords rooted in ancient wisdom, Mantra makes code more readable, expressive, and meaningful.

### ✨ Key Features

- **🕉️ Sanskrit-Inspired**: Keywords like `kriya` (function), `sthana` (variable), `prakash` (print)
- **🎯 Concise Syntax**: Accomplish more with fewer lines of code
- **🌍 Unicode Ready**: Full support for Sanskrit text and symbols
- **⚡ Fast & Modern**: Built on Python with clean, efficient design
- **🔧 Developer Friendly**: REPL, debugging, and excellent error messages
- **📱 Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/codecravings/mantra-lang.git
cd mantra-lang

# Install dependencies
pip install -r requirements.txt

# Install Mantra
pip install -e .
```

### Your First Program

Create `hello.man`:
```mantra
sthana message = "Namaste, World!"
prakash(message)
prakash("🕉️ Welcome to Sanskrit programming!")
```

Run it:
```bash
python -m mantra hello.man
```

### Try the REPL

```bash
python -m mantra --repl
```

```
Mantra Programming Language REPL v0.1.0
॥ Om Gam Ganapataye Namaha ॥

mantra> sthana name = "Arjuna"
mantra> prakash("Hello,", name)
Hello, Arjuna
mantra> exit
```

## 💡 Examples

### 🔢 Simple Calculator
```mantra
kriya add(a, b) {
    gati a + b
}

kriya multiply(a, b) {
    gati a * b
}

prakash("5 + 3 =", add(5, 3))        # Output: 5 + 3 = 8
prakash("6 * 7 =", multiply(6, 7))   # Output: 6 * 7 = 42
```

### 🔁 Fibonacci Sequence
```mantra
kriya fibonacci(n) {
    yadi n <= 1 {
        gati n
    } athava {
        gati fibonacci(n - 1) + fibonacci(n - 2)
    }
}

prakash("fib(10) =", fibonacci(10))  # Output: fib(10) = 55
```

### 🌐 Pure Sanskrit Programming
```mantra
# Variables in Sanskrit
sthana naam = "राम"              # naam = name
sthana ayu = 30                  # ayu = age

# Function in Sanskrit  
kriya namaskar(vyakti) {         # vyakti = person
    prakash("नमस्ते", vyakti + "!")
    gati "नमस्कार पूर्ण"         # "greeting complete"
}

namaskar(naam)                   # Output: नमस्ते राम!
```

### 🎮 Control Flow
```mantra
# Conditional statements
sthana score = 85

yadi score >= 90 {               # yadi = if
    prakash("Grade: A")
} athava yadi score >= 80 {      # athava = else
    prakash("Grade: B") 
} athava {
    prakash("Grade: C")
}

# Loops
sthana count = 1
punar count <= 5 {               # punar = repeat/loop
    prakash("Iteration:", count)
    count = count + 1
}
```

## 📚 Language Reference

### Keywords

| Sanskrit | English | Meaning | Usage |
|----------|---------|---------|-------|
| `kriya` | function | "action" | Define functions |
| `sthana` | variable | "place" | Declare variables |
| `yadi` | if | "if/when" | Conditional statements |
| `athava` | else | "or/else" | Alternative conditions |
| `punar` | loop | "again" | Iteration |
| `gati` | return | "path/direction" | Return values |
| `saty` | true | "truth" | Boolean true |
| `asaty` | false | "untruth" | Boolean false |
| `shunya` | null | "void/empty" | Null value |

### Built-in Functions

| Sanskrit | English | Purpose | Example |
|----------|---------|---------|---------|
| `prakash()` | `print()` | Display output | `prakash("Hello")` |
| `lambh()` | `len()` | Get length | `lambh("text")` |
| `shabd()` | `str()` | Convert to string | `shabd(123)` |
| `ank()` | `int()` | Convert to integer | `ank("42")` |

## 🏗️ Project Structure

```
mantra-lang/
├── mantra/              # Core language implementation
│   ├── lexer.py        # Tokenizer
│   ├── parser.py       # Parser  
│   ├── interpreter.py  # Interpreter
│   ├── ast_nodes.py    # AST definitions
│   └── cli.py          # Command line interface
├── examples/           # Example programs
│   ├── hello.man      # Hello world
│   ├── calculator.man # Calculator demo
│   └── fibonacci.man  # Fibonacci sequence
├── tests/             # Unit tests
├── docs/              # Documentation
└── README.md          # This file
```

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_basic.py -v
```

## 🤝 Contributing

We welcome contributions from developers of all backgrounds! Whether you're interested in:

- 🐛 **Bug fixes**
- ✨ **New features** 
- 📚 **Documentation**
- 🌍 **Translations**
- 💡 **Ideas and suggestions**

### Getting Started

1. **Fork** this repository
2. **Clone** your fork: `git clone https://github.com/your-username/mantra-lang.git`
3. **Create** a branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Add** tests for new features
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/codecravings/mantra-lang.git
cd mantra-lang

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful Sanskrit-inspired names where appropriate
- Add docstrings for all public functions
- Include tests for new features

## 🗺️ Roadmap

### Version 0.2.0
- [ ] Enhanced error messages with suggestions
- [ ] VS Code extension with syntax highlighting
- [ ] Package manager (`mantra install`)
- [ ] Module system for imports

### Version 0.3.0
- [ ] GUI framework (`yantra` system)
- [ ] Web development tools (`shakti` expressions)
- [ ] Standard library expansion
- [ ] Performance optimizations

### Version 1.0.0
- [ ] Production-ready interpreter
- [ ] Complete language specification
- [ ] Comprehensive documentation
- [ ] Community ecosystem

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Sanskrit Language**: For inspiring the keywords and philosophy
- **Python Community**: For the excellent development tools
- **Contributors**: Everyone who helps make Mantra better
- **Ancient Wisdom**: For teaching us that simplicity is the ultimate sophistication

## 📞 Support & Community

- **Issues**: [Report bugs or request features](https://github.com/codecravings/mantra-lang/issues)
- **Discussions**: [Join the conversation](https://github.com/codecravings/mantra-lang/discussions)
- **Email**: [codecravings@proton.me](mailto:codecravings@proton.me)

## 🌟 Show Your Support

If you find Mantra useful, please:
- ⭐ **Star** this repository
- 🍴 **Fork** it for your own experiments
- 📢 **Share** it with friends
- 🐛 **Report** bugs you find
- 💡 **Suggest** new features

---

<div align="center">

**॥ सत्यमेव जयते ॥**  
*Truth alone triumphs*

Made with ❤️ and ancient wisdom by [@codecravings](https://github.com/codecravings)

**[⬆ Back to Top](#-mantra-programming-language)**

</div>