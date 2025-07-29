# path-comment-hook

```
    /·\
   /│·│\    ┌─┐┌─┐┬ ┬
  / │·│ \   ├─┘│  ├─┤
 /  │·│  >  ┴  └─┘┴ ┴
/___│·│___\ path-comment-hook
```

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/path-comment-hook.svg)](https://badge.fury.io/py/path-comment-hook)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![CI](https://github.com/Shorzinator/path-comment-hook/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/Shorzinator/path-comment-hook/actions)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://shorzinator.github.io/path-comment-hook)
[![Coverage](https://codecov.io/gh/Shorzinator/path-comment-hook/branch/main/graph/badge.svg)](https://codecov.io/gh/Shorzinator/path-comment-hook)

**Automatically add file path headers to your source code for better navigation and context.**

Never lose track of where you are in large codebases. This pre-commit hook automatically adds file path comments to the top of your source files, making code navigation effortless.

**Use `pch` for quick access** - convenient shorthand for all operations.

[**Documentation**](https://shorzinator.github.io/path-comment-hook) • [**Quick Start**](https://shorzinator.github.io/path-comment-hook/getting-started/quick-start/) • [**Configuration**](https://shorzinator.github.io/path-comment-hook/user-guide/configuration/) • [**API Reference**](https://shorzinator.github.io/path-comment-hook/api/reference/)

</div>

## What It Does

Transform your codebase with automatic path headers that provide instant context:

<div align="center">

| **Before** | **After** |
|------------|-----------|
| ```python<br/>def calculate_tax(amount, rate):<br/>    return amount * rate<br/>``` | ```python<br/># src/utils/tax_calculator.py<br/><br/>def calculate_tax(amount, rate):<br/>    return amount * rate<br/>``` |

</div>

**Key Benefits:**
- **Enhanced Navigation** - Know exactly where you are in your codebase
- **Better Code Reviews** - Reviewers can quickly identify file locations
- **Improved Search** - Context-aware code snippets
- **Self-Documenting** - Built-in file references
- **Fast Performance** - Parallel processing for large projects

## Quick Start

### 1. Install via pip

```bash
pip install path-comment-hook
```

### 2. Try it out instantly

```bash
# Using the convenient shorthand
pch your_file.py

# Or the full command name
path-comment-hook your_file.py
```

### 3. Add to pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Shorzinator/path-comment-hook
    rev: v0.1.0  # Use the latest version
    hooks:
      - id: path-comment
```

### 4. Install and run

```bash
pre-commit install
pre-commit run path-comment --all-files
```

**That's it!** Your files now have path headers for better navigation.

Use `pch` for quick access to all features!

## Supported Languages

Works with **10+ programming languages** out of the box:

| Language | Extensions | Comment Style | Example |
|----------|------------|---------------|---------|
| **Python** | `.py`, `.pyx` | `#` | `# src/models/user.py` |
| **JavaScript** | `.js` | `//` | `// src/components/Button.js` |
| **TypeScript** | `.ts`, `.tsx` | `//` | `// src/types/api.ts` |
| **C/C++** | `.c`, `.cpp`, `.h` | `//` | `// src/core/engine.cpp` |
| **Shell** | `.sh`, `.bash` | `#` | `# scripts/deploy.sh` |
| **YAML** | `.yml`, `.yaml` | `#` | `# config/database.yml` |
| **TOML** | `.toml` | `#` | `# pyproject.toml` |
| **Makefile** | `Makefile` | `#` | `# Makefile` |

> **Smart Detection**: Automatically handles shebangs, encoding, and file types using the [`identify`](https://github.com/pre-commit/identify) library.

## Advanced Features

### Performance Optimized
- **Parallel Processing** - Utilizes all CPU cores
- **Smart Caching** - Avoids unnecessary modifications
- **Memory Efficient** - Handles large files safely

### Safe & Reliable
- **Atomic Operations** - Safe file modifications
- **Encoding Preservation** - Maintains UTF-8, Latin-1, etc.
- **Line Ending Preservation** - Keeps LF/CRLF intact
- **Comprehensive Testing** - 152 tests with 69% coverage

### Rich CLI Experience
- **Progress Bars** - Visual feedback for large operations
- **Colored Output** - Easy-to-read status messages
- **Detailed Reporting** - Comprehensive summaries
- **Multiple Modes** - Check, fix, and delete operations
- **Convenient Shorthand** - Use `pch` instead of `path-comment-hook`

## Real-World Examples

### Django Web Application

```python
# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
```

### React Component

```javascript
// src/components/LoginForm.jsx

import React, { useState } from 'react';
import { validateEmail } from '../utils/validation';

export function LoginForm({ onSubmit }) {
    const [email, setEmail] = useState('');
    // Component logic...
}
```

### API Configuration

```yaml
# config/api.yml

environment: production
database:
  host: localhost
  port: 5432
```

## Configuration

Customize behavior in your `pyproject.toml`:

```toml
[tool.path-comment]
exclude_globs = [
    "*.md",
    "tests/fixtures/**",
    "node_modules/**",
    "build/**"
]
```

**Popular configurations:**
- [Python Library](https://shorzinator.github.io/path-comment-hook/user-guide/configuration/#python-library)
- [Web Application](https://shorzinator.github.io/path-comment-hook/user-guide/configuration/#web-application)
- [Data Science Project](https://shorzinator.github.io/path-comment-hook/user-guide/configuration/#data-science-project)
- [Monorepo](https://shorzinator.github.io/path-comment-hook/user-guide/configuration/#monorepo)

## CLI Usage

The tool provides both full and shorthand commands for convenience:

```bash
# Using full command name
path-comment-hook src/main.py src/utils.py
path-comment-hook --all
path-comment-hook --check --all
path-comment-hook --delete --all
path-comment-hook show-config

# Using convenient shorthand (pch)
pch src/main.py src/utils.py
pch --all
pch --check --all
pch --delete --all
pch show-config
```

**Common workflows:**
```bash
# Quick project-wide update
pch --all

# Check what would change (dry run)
pch --check --all

# Remove all path headers
pch delete --all

# Process specific file types
pch src/**/*.py tests/**/*.py

# Show current configuration
pch show-config

# View help
pch --help
```

**All options:**
```bash
pch --help  # or path-comment-hook --help
```

See the [CLI Usage Guide](https://shorzinator.github.io/path-comment-hook/user-guide/cli-usage/) for complete details.

## Quality & Testing

- **152 Test Cases** - Comprehensive test coverage
- **Real-time Coverage** - Monitored via Codecov integration (69% current)
- **Type Safe** - Full type hints with mypy
- **Linted & Formatted** - Ruff for code quality
- **Cross-Platform CI** - Ubuntu, Windows, macOS testing
- **Professional Standards** - Enterprise-grade code quality

```bash
# Run tests locally
make test
make test-cov  # With coverage report
```

## Documentation

**Complete documentation available at:** https://shorzinator.github.io/path-comment-hook

- [Quick Start Guide](https://shorzinator.github.io/path-comment-hook/getting-started/quick-start/) - Get up and running in 5 minutes
- [User Guide](https://shorzinator.github.io/path-comment-hook/user-guide/cli-usage/) - Complete CLI reference
- [Configuration](https://shorzinator.github.io/path-comment-hook/user-guide/configuration/) - Customize for your project
- [Pre-commit Setup](https://shorzinator.github.io/path-comment-hook/user-guide/pre-commit-setup/) - Automate your workflow
- [API Reference](https://shorzinator.github.io/path-comment-hook/api/reference/) - Programmatic usage
- [FAQ](https://shorzinator.github.io/path-comment-hook/faq/) - Common questions answered

## Contributing

We welcome contributions! Check out our [Development Guide](https://shorzinator.github.io/path-comment-hook/contributing/development/) to get started.

**Quick setup:**
```bash
git clone https://github.com/Shorzinator/path-comment-hook.git
cd path-comment-hook
poetry install
make test

# Try the tool locally with shorthand
pch --help
pch examples/basic_usage.py
```

## Integration Examples

### GitHub Actions
```yaml
- name: Check path headers
  run: pch --check --all
```

### GitLab CI
```yaml
check-headers:
  script: pch --check --all
```

### Docker
```dockerfile
RUN pip install path-comment-hook && \
    pch --all
```

See [CI/CD Integration](https://shorzinator.github.io/path-comment-hook/advanced/ci-integration/) for more examples.

## Requirements

- **Python 3.8+** - Modern Python support
- **Cross-platform** - Works on Linux, macOS, and Windows
- **Minimal dependencies** - Only essential packages

## Troubleshooting

**Common issues:**
- [Files not being processed](https://shorzinator.github.io/path-comment-hook/troubleshooting/#files-not-being-processed) - Try `pch --verbose --all`
- [Performance optimization](https://shorzinator.github.io/path-comment-hook/troubleshooting/#performance-issues) - Use `pch --workers 8 --all`
- [Pre-commit integration](https://shorzinator.github.io/path-comment-hook/troubleshooting/#pre-commit-issues) - Test with `pch --check --all`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Why Choose path-comment-hook?

**Production Ready** - Used in real projects with comprehensive testing
**Zero Configuration** - Works immediately with sensible defaults
**Language Agnostic** - Supports 10+ programming languages
**Performance Focused** - Parallel processing for large codebases
**Developer Friendly** - Rich CLI with progress bars and colored output
**Well Documented** - Comprehensive guides and examples
**Actively Maintained** - Regular updates and community support
**Easy Integration** - Works with existing tools and workflows

**Star us on GitHub • Read the docs • Report issues**

Made with care for developers who value code organization and navigation.
