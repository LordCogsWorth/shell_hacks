# Copilot Instructions for shell_hacks

## Project Overview
This is a fork of the **A2A Python SDK** - a library for building agentic applications that follow the Agent2Agent (A2A) Protocol. The SDK provides async Python interfaces for creating A2A-compliant servers with optional HTTP, gRPC, and database integrations.

**Key Goal**: Enable developers to build agent communication systems using the standardized A2A protocol with modern async Python patterns.

## Architecture & Components

### Core Structure (`src/a2a/`)
- **`server/`**: A2A server implementations (HTTP, gRPC endpoints)
- **`client/`**: Client SDK for communicating with A2A servers
- **`auth/`**: Authentication and authorization components
- **`extensions/`**: Optional integrations (databases, telemetry)
- **`grpc/`**: Protocol buffer definitions and gRPC service implementations
- **`utils/`**: Shared utilities and helper functions
- **`types.py`**: Core type definitions and Pydantic models

### Data Flow
1. **Agent Requests** → A2A Server (HTTP/gRPC) → **Protocol Validation**
2. **Business Logic** → Optional Database/Extensions → **Response Generation**
3. **Structured Responses** → Client SDK → **Consuming Applications**

### External Dependencies
- **Core**: `httpx`, `pydantic`, `protobuf`, `google-api-core`
- **Optional**: FastAPI/Starlette (HTTP), gRPC, OpenTelemetry, SQL databases

## Development Workflows

### Getting Started
```bash
# Install with uv (recommended) or pip
uv add a2a-sdk[all]  # All optional dependencies
uv add a2a-sdk       # Core only

# Development setup
uv sync --all-extras --dev
pre-commit install
```

### Code Quality & Testing
```bash
# Format and lint (uses Ruff with Google Python Style Guide)
./scripts/format.sh

# Run tests
uv run pytest tests/
uv run pytest tests/integration/  # Integration tests

# Type checking
uv run mypy src/
```

### Protocol Buffer Generation
```bash
# Generate gRPC types from .proto files
./scripts/generate_types.sh
```

## Project Conventions

### Code Patterns
- **Google Python Style Guide** (80-char line limit, 4-space indentation)
- **Async-first**: All I/O operations use `async/await` patterns
- **Pydantic Models**: Strict type validation for all data structures
- **Protocol Compliance**: All components must adhere to A2A Protocol specification

### File Organization
```
src/a2a/           # Main package
├── server/        # Server implementations
├── client/        # Client SDK
├── auth/          # Authentication
├── extensions/    # Optional features
├── grpc/          # Protocol buffers
└── utils/         # Shared utilities

tests/             # Mirror src/ structure
├── integration/   # End-to-end tests
└── unit/          # Component tests
```

### Configuration Management
- **Environment Variables**: Standard pattern for optional integrations
- **Pydantic Settings**: Type-safe configuration validation
- **Extension Loading**: Dynamic imports for optional dependencies

## Integration Points

### A2A Protocol Endpoints
- **HTTP**: RESTful APIs with FastAPI/Starlette integration
- **gRPC**: High-performance binary protocol support
- **WebSocket**: Real-time agent communication (via HTTP extensions)

### Database Integration
- **SQL Support**: PostgreSQL, MySQL, SQLite via optional extensions
- **Connection Pooling**: Async database connections
- **Migration Patterns**: Database schema management utilities

### Observability
- **OpenTelemetry**: Distributed tracing for agent interactions
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Metrics**: Performance monitoring for protocol operations

## Key Files to Understand

### Essential Architecture
- `src/a2a/_base.py`: Core abstract classes and interfaces
- `src/a2a/types.py`: Fundamental type definitions
- `pyproject.toml`: Dependencies, build config, and optional extras

### Development Tools
- `.ruff.toml`: Code formatting and linting rules (Google Style)
- `.pre-commit-config.yaml`: Git hooks for code quality
- `scripts/generate_types.sh`: Protocol buffer compilation

### Testing Patterns
- `tests/README.md`: Testing strategy and conventions
- `tests/integration/`: End-to-end A2A protocol testing

## Common Tasks

```bash
# Add new A2A server endpoint
# 1. Define in src/a2a/server/
# 2. Add tests in tests/server/
# 3. Update protocol documentation

# Add optional integration
# 1. Create in src/a2a/extensions/
# 2. Add to pyproject.toml [project.optional-dependencies]
# 3. Add conditional imports with try/except

# Debug A2A protocol issues
uv run pytest tests/integration/ -v -s  # Verbose integration tests
# Check gRPC definitions in src/a2a/grpc/

# Performance optimization
# Focus on async patterns, connection pooling, and protocol efficiency
```