# Fusera SDK

Submit PyTorch models for cloud compilation with a single line of code.

## Installation

### From PyPI (Coming Soon)
```bash
pip install fusera
```

### From Source
```bash
pip install git+https://github.com/fusera/fusera-sdk.git
```

### Development Installation
```bash
git clone https://github.com/fusera/fusera-sdk.git
cd fusera-sdk
pip install -e .
```

## Quick Start

```python
import fusera
import torch.nn as nn
from dotenv import load_dotenv

# This line looks for a .env file and loads the variables from it
load_dotenv()

# Define your model
model = nn.Sequential(
    nn.Linear(10, 100),
    nn.ReLU(),
    nn.Linear(100, 10)
)

# Submit for compilation
result = fusera.compile(model)
print(result['message'])
# Output: ✓ Model submitted! Track progress at: https://fusera.dev/jobs/job_123...
```

## Configuration

The SDK uses these environment variables (configured in `.env`):

```bash
FUSERA_API_URL=http://your-backend-url:8000    # Backend API endpoint
FUSERA_API_KEY=fus_your_key_here               # Your API key
FUSERA_DEV_MODE=false                          # Set to true for local testing
```

## API Reference

### `fusera.compile(model, **kwargs)`

Submit a PyTorch model for cloud compilation.

**Parameters:**
- `model` (torch.nn.Module): The PyTorch model to compile
- `**kwargs`: Additional compilation options

**Returns:**
- `dict`: Response containing job ID and tracking URL

**Example:**
```python
import fusera
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(10, 100),
    nn.ReLU(),
    nn.Linear(100, 10)
)

result = fusera.compile(model)
print(result['job_id'])  # job_abc123...
print(result['dashboard_url'])  # https://fusera.dev/jobs/job_abc123...
```

### Exceptions

- `FuseraError`: Base exception for all Fusera SDK errors
- `AuthenticationError`: Invalid or missing API key
- `CompilationError`: Model compilation failed
- `NetworkError`: Network connection issues

## Development

To contribute to the SDK:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy fusera

# Linting
ruff check fusera

# Format code
ruff format fusera
```

## License

MIT License - see LICENSE file for details.
