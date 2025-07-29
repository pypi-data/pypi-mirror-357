# Bloomberg API Controller (BBG API Controller)

A Python package providing utility functions for Bloomberg API controller. This package helps streamline the process of handling Bloomberg data fetching process and provides related database management.

## Features

- Bloomberg API data fetching and parsing
- MongoDB integration for data storage

## Installation

You can install the package using pip:

```bash
pip install git+https://github.com/nailen1/module-bbg_api_controller.git
```

## Package Structure

```
bbg_api_controller/
├── __init__.py            # Package initialization
├── application.py         # Application level functionality
├── composed.py           # Collection of composed or partial functions
├── connector.py          # Bloomberg connection management
├── utils.py              # Utility functions
├── basis/                # Core functionality
│   ├── __init__.py       # Subpackage initialization
│   ├── fetcher.py        # Data fetching operations
│   └── ...               # Other base modules
└── consts/               # Constants and configurations
    ├── __init__.py       # Subpackage initialization
    ├── bbg_consts.py     # Bloomberg-specific constants
    └── ...               # Other constant definitions
```

## Usage

```python
from bbg_api_controller import application

# Example usage code
# ...
```

# Requirements

- pdblp
- pandas
- tqdm
- python-dotenv
- canonical_transformer
- string_date_controller
- shining_pebbles
- mongodb_controller

## Version History

### v0.1.2
- Added MANIFEST.in to include requirements.txt and other non-Python files in the package
- Improved package distribution configuration

### v0.1.1
- Added `recurse_squared` function for recursive data fetching, parsing, and insertion process across multiple dates
- Improved package structure documentation

## License

This project is licensed under the MIT License.

## Author

**June Young Park**
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

## Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
