# Shell Hacks SDK

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)

<!-- markdownlint-disable no-inline-html -->

<div align="center">
   <h1>🚀 Shell Hacks SDK</h1>
   <h3>
      A Python library for building Agent2Agent (A2A) compliant applications with modern async patterns.
   </h3>
</div>

<!-- markdownlint-enable no-inline-html -->

---

## ✨ Features

- **A2A Protocol Compliant:** Build agentic applications that adhere to the Agent2Agent (A2A) Protocol.
- **Extensible:** Easily add support for different communication protocols and database backends.
- **Asynchronous:** Built on modern async Python for high performance.
- **Optional Integrations:** Includes optional support for:
  - HTTP servers ([FastAPI](https://fastapi.tiangolo.com/), [Starlette](https://www.starlette.io/))
  - [gRPC](https://grpc.io/)
  - [OpenTelemetry](https://opentelemetry.io/) for tracing
  - SQL databases ([PostgreSQL](https://www.postgresql.org/), [MySQL](https://www.mysql.com/), [SQLite](https://sqlite.org/))

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `uv` (recommended) or `pip`

### 🔧 Installation

Install the core SDK and any desired extras using your preferred package manager.

| Feature                  | `uv` Command                               | `pip` Command                                |
| ------------------------ | ------------------------------------------ | -------------------------------------------- |
| **Core SDK**             | `uv add shell-hacks-sdk`                   | `pip install shell-hacks-sdk`                |
| **All Extras**           | `uv add shell-hacks-sdk[all]`              | `pip install shell-hacks-sdk[all]`           |
| **HTTP Server**          | `uv add "shell-hacks-sdk[http-server]"`    | `pip install "shell-hacks-sdk[http-server]"` |
| **gRPC Support**         | `uv add "shell-hacks-sdk[grpc]"`           | `pip install "shell-hacks-sdk[grpc]"`        |
| **OpenTelemetry Tracing**| `uv add "shell-hacks-sdk[telemetry]"`      | `pip install "shell-hacks-sdk[telemetry]"`   |
| **Encryption**           | `uv add "shell-hacks-sdk[encryption]"`     | `pip install "shell-hacks-sdk[encryption]"`  |
|                          |                                            |                                              |
| **Database Drivers**     |                                            |                                              |
| **PostgreSQL**           | `uv add "shell-hacks-sdk[postgresql]"`     | `pip install "shell-hacks-sdk[postgresql]"`  |
| **MySQL**                | `uv add "shell-hacks-sdk[mysql]"`          | `pip install "shell-hacks-sdk[mysql]"`       |
| **SQLite**               | `uv add "shell-hacks-sdk[sqlite]"`         | `pip install "shell-hacks-sdk[sqlite]"`      |
| **All SQL Drivers**      | `uv add "shell-hacks-sdk[sql]"`            | `pip install "shell-hacks-sdk[sql]"`         |

## Examples

### Quick Start Example

1. Install Shell Hacks SDK

   ```bash
   uv add shell-hacks-sdk[all]
   # or
   pip install shell-hacks-sdk[all]
   ```

2. Create a simple agent

   ```python
   from a2a import create_server
   
   # Your agent code here
   server = create_server()
   server.run()
   ```

3. Build your own A2A-compliant applications!

---

## 🤝 Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get involved.

---

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for more details.
