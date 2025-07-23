# Polyglot-CPP: The C++ MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP Compliant](https://img.shields.io/badge/MCP-Compliant-brightgreen.svg)](https://gofastmcp.com/)
[![Made with FastMCP](https://img.shields.io/badge/Made%20with-FastMCP-orange.svg)](https://github.com/jlowin/fastmcp)

**[English](./README.md) | [简体中文](./README_zh-CN.md)**

A powerful, high-performance MCP (Model-driven Co-programming Protocol) server designed to compile, run, debug, and profile C++ code on the fly. As a vital component of the growing MCP ecosystem, this tool is perfect for competitive programming platforms, AI-driven development tools, educational platforms, and rapid C++ prototyping.

## 🌟 Why This Project?

The Model Context Protocol (MCP) is revolutionizing how AI models interact with external tools. While the ecosystem is expanding rapidly, there was a critical gap: a dedicated, full-featured MCP server for the C++ language, one of the cornerstones of performance-critical computing.

`polyglot-cpp` was built to fill that gap. It's not just another online compiler; it's a ready-to-use, API-driven bridge that connects the power of C++ (including debugging and profiling) to any MCP-compatible AI assistant or workflow. It was created because a tool with this specific feature set was missing from the public MCP ecosystem on GitHub.

## ✨ Key Features

- **🚀 On-the-Fly Compilation**: Compiles C++ code using `clang++` with essential flags enabled.
- **🏃‍♂️ Timeout-Controlled Execution**: Runs compiled code with a 10-second execution timeout to prevent infinite loops and runaway processes.
- **🐞 Integrated Memory Debugging**: Automatically enables AddressSanitizer (`-fsanitize=address`) to catch common memory errors like segmentation faults and buffer overflows, providing detailed reports.
- **⏱️ Performance Profiling**: Generates a concise performance report using `gprof` to identify hotspots and function call times.
- **💾 Persistent Artifacts**: Compiled programs are stored for 24 hours, allowing for repeated execution without recompilation.
- **🔌 Simple API**: Exposes a clean and straightforward API through the MCP protocol with three simple tools.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.9+
- `clang++` compiler
- `gprof` (usually part of binutils)

These tools must be available in your system's `PATH`.

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/polyglot-cpp.git
    cd polyglot-cpp
    ```

2.  **Install dependencies:**
    This project uses `uv` for package management.
    ```bash
    pip install uv
    uv pip install -r requirements.txt 
    # If you don't have a requirements.txt, you can install from pyproject.toml
    # uv pip install .
    ```
    *(Note: You may need to create a `requirements.txt` from `pyproject.toml` or install dependencies directly).*

## 🚀 Running the Server

To start the MCP server, run `main.py`:

```bash
python main.py
```

The server will start and be accessible on `0.0.0.0:53482` using the SSE transport.

## 🌐 The MCP Ecosystem

This server is built with [FastMCP](https://github.com/jlowin/fastmcp), the premier Python framework for the **Model Context Protocol (MCP)**. MCP is an open standard designed to be the "USB-C port for AI," allowing language models to seamlessly connect with external tools and data sources.

By being MCP-compliant, `polyglot-cpp` can be instantly discovered and used by any MCP-compatible client or AI assistant, making it a valuable, plug-and-play addition to this growing ecosystem.

## 📚 API / Tools

The server provides three main tools via the MCP protocol.

### 1. `create_program`
Compiles C++ code and returns a `file_id` for the compiled binary.

- **Description**: Accepts C++ code as a string, compiles it with profiling and address sanitizer flags, and stores the binary.
- **Parameters**:
  - `content` (string, required): The C++ source code to compile.
- **Returns**:
  - `success` (boolean): `true` if compilation succeeded, `false` otherwise.
  - `file_id` (string): The unique ID for the compiled program.
  - `error` (string, optional): The compilation error message if it failed.

### 2. `run_program`
Executes a previously compiled program using its `file_id`.

- **Description**: Runs a compiled program. You can provide standard input and an expected output for diffing.
- **Parameters**:
  - `file_id` (string, required): The ID of the program to run.
  - `custom_input` (string, optional): The standard input to pass to the program.
  - `expected_output` (string, optional): The expected standard output to compare against.
- **Returns**:
  - `success` (boolean): `true` if execution was successful.
  - `stdout` (string): The program's standard output.
  - `stderr` (string): The program's standard error.
  - `diff` (string, optional): A unified diff between the actual and expected output.
  - `run_time` (float): The execution time in seconds.
  - `profiling_report` (string): A concise report from `gprof`.

### 3. `create_and_run_program`
A convenience tool that compiles and runs code in a single step.

- **Description**: Combines `create_program` and `run_program`.
- **Parameters**: Same as `create_program` and `run_program` combined.
- **Returns**: A combined JSON object containing the results from both creation and execution.

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, please open an issue or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is distributed under the MIT License. See `LICENSE` file for more information.