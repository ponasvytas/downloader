# Downloader

A CLI tool to download and process game videos from ice rinks.

## Features

- Download video segments from multiple ice rinks
- Concatenate video parts into a single file
- Trim videos at start and end
- Support for panoramic mode
- Interactive CLI with fuzzy search and auto-completion

## Installation

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Install it first:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd downloader

# Install dependencies and the package
uv sync --native-tls
```

### Production Installation

```bash
# Install from PyPI (when published)
uv pip install downloader

# Or install from source
uv pip install .
```

## Configuration

Create a `.env` file in the project root with your credentials:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:

```
HOST_URL=https://www.your-video-host.com/
DOWNLOADER_USERNAME=your_username
DOWNLOADER_PASSWORD=your_password
```

## Usage

### Using the installed CLI

After installation, you can use the `downloader` command directly:

```bash
# If installed in a uv environment
uv run downloader

# Or if globally installed
downloader
```


## Project Structure

```
downloader/
├── src/
│   └── downloader/
│       ├── cli/                 # CLI interface
│       ├── core/               # Core functionality
│       ├── config/             # Configuration and constants
│       ├── models/             # Data models
│       └── utils/              # Utility functions
├── tests/                      # Test suite
├── video/                      # Output directory
├── pyproject.toml             # Project configuration
├── scripts.py                 # Development task runner
└── README.md                  # This file
```

## Development

### Managing Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv lock

# Sync dependencies (like npm install)
uv sync --native-tls
```

### Running Tests

```bash
# Run all tests
uv run pytest 

```


## Environment Variables

- `HOST_URL`: Base URL for the video hosting service
- `DOWNLOADER_USERNAME`: Your username for authentication
- `DOWNLOADER_PASSWORD`: Your password for authentication