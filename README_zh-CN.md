# Polyglot-CPP: C++ MCP 服务器

[![许可证: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 版本](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP 兼容](https://img.shields.io/badge/MCP-Compliant-brightgreen.svg)](https://gofastmcp.com/)
[![由 FastMCP 驱动](https://img.shields.io/badge/Made%20with-FastMCP-orange.svg)](https://github.com/jlowin/fastmcp)

**[English](./README.md) | [简体中文](./README_zh-CN.md)**

一个功能强大、高性能的 MCP (模型驱动协同编程协议) 服务器，专为即时编译、运行、调试和分析 C++ 代码而设计。作为不断发展的 MCP 生态系统的重要组成部分，该工具非常适用于编程竞赛平台、AI 驱动的开发工具、教育平台以及快速 C++ 原型开发。

## 🌟 为何发起这个项目？

模型驱动协同编程协议 (MCP) 正在彻底改变 AI 模型与外部工具的交互方式。尽管这个生态系统正在迅速扩张，但其中存在一个关键的空白：缺少一个专为 C++ 语言设计的、功能齐全的 MCP 服务器，而 C++ 是性能关键型计算的基石之一。

`polyglot-cpp` 正是为了填补这一空白而生。它不仅仅是另一个在线编译器；它是一个即用型的、由 API 驱动的桥梁，将 C++ 的强大功能（包括调试和性能分析）连接到任何兼容 MCP 的 AI 助手或工作流中。我们创建它，是因为在 GitHub 的公共 MCP 生态系统中，缺少具备这一特定功能集的工具。

## ✨ 主要特性

- **🚀 即时编译**: 使用 `clang++` 编译器，并启用了必要的编译标志。
- **🏃‍♂️ 超时控制执行**: 运行编译后的代码，并设置 10 秒的执行超时，以防止无限循环和失控进程。
- **🐞 集成内存调试**: 自动启用 AddressSanitizer (`-fsanitize=address`) 来捕获常见的内存错误，如段错误和缓冲区溢出，并提供详细的错误报告。
- **⏱️ 性能分析**: 使用 `gprof` 生成简洁的性能报告，以识别代码热点和函数调用耗时。
- **💾 持久化构建物**: 编译后的程序会存储 24 小时，允许在不重新编译的情况下重复执行。
- **🔌 简洁的 API**: 通过 MCP 协议暴露了三个简单明了的工具接口。

## 🛠️ 环境要求

在开始之前，请确保您的系统上已安装以下软件：
- Python 3.9+
- `clang++` 编译器
- `gprof` (通常是 binutils 的一部分)

这些工具必须在您系统的 `PATH` 环境变量中可用。

## ⚙️ 安装

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/your-username/polyglot-cpp.git
    cd polyglot-cpp
    ```

2.  **安装依赖:**
    本项目使用 `uv` 进行包管理。
    ```bash
    pip install uv
    uv pip install -r requirements.txt 
    # 如果您没有 requirements.txt，可以从 pyproject.toml 安装
    # uv pip install .
    ```
    *(注意: 您可能需要从 `pyproject.toml` 创建一个 `requirements.txt` 文件，或直接安装依赖项)。*

## 🚀 运行服务器

要启动 MCP 服务器，请运行 `main.py`:

```bash
python main.py
```

服务器将启动并通过 SSE 传输协议在 `0.0.0.0:53482` 上提供服务。

## 🌐 MCP 生态系统

本服务器使用 [FastMCP](https://github.com/jlowin/fastmcp) 构建，这是 **模型驱动协同编程协议 (MCP)** 的首选 Python 框架。MCP 是一个开放标准，旨在成为“AI 的 USB-C 端口”，允许语言模型无缝地与外部工具和数据源连接。

通过与 MCP 兼容，`polyglot-cpp` 可以被任何兼容 MCP 的客户端或 AI 助手即时发现和使用，使其成为这个不断发展的生态系统中一个有价值的、即插即用的组件。

## 📚 API / 工具

该服务器通过 MCP 协议提供三个主要工具。

### 1. `create_program`
编译 C++ 代码并返回一个指向已编译二进制文件的 `file_id`。

- **描述**: 接收一个 C++ 代码字符串，使用性能分析和地址消毒器标志进行编译，并存储二进制文件。
- **参数**:
  - `content` (字符串, 必需): 要编译的 C++ 源代码。
- **返回**:
  - `success` (布尔值): 如果编译成功则为 `true`，否则为 `false`。
  - `file_id` (字符串): 已编译程序的唯一 ID。
  - `error` (字符串, 可选): 如果编译失败，则返回编译错误信息。

### 2. `run_program`
使用 `file_id` 执行一个先前已编译的程序。

- **描述**: 运行一个已编译的程序。您可以提供标准输入和预期的输出来进行差异比较。
- **参数**:
  - `file_id` (字符串, 必需): 要运行的程序的 ID。
  - `custom_input` (字符串, 可选): 传递给程序的标准输入。
  - `expected_output` (字符串, 可选): 用于与实际输出进行比较的预期标准输出。
- **返回**:
  - `success` (布尔值): 如果执行成功则为 `true`。
  - `stdout` (字符串): 程序的标准输出。
  - `stderr` (字符串): 程序的标准错误。
  - `diff` (字符串, 可选): 实际输出与预期输出之间的统一差异。
  - `run_time` (浮点数): 执行时间（秒）。
  - `profiling_report` (字符串): 来自 `gprof` 的简明报告。

### 3. `create_and_run_program`
一个方便的工具，可以在一个步骤中完成编译和运行。

- **描述**: 结合了 `create_program` 和 `run_program` 的功能。
- **参数**: 与 `create_program` 和 `run_program` 的参数相同。
- **返回**: 一个包含创建和执行结果的组合 JSON 对象。

## 🤝 贡献

欢迎各种贡献！如果您有关于新功能、错误修复或改进的想法，请随时开启一个 issue 或提交一个 pull request。

1.  Fork 本项目
2.  创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。更多信息请参见 `LICENSE` 文件。