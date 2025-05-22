# Inventory Management TUI (`inv`)

[![PyPI - Version](https://img.shields.io/pypi/v/inv.svg)](https://pypi.org/project/inv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/inv.svg)](https://pypi.org/project/inv)

---

## Overview

`inv` is a terminal-based inventory management application designed for organizations that need to track lots, shipments, and inventory levels across multiple sites. It features a modern Textual TUI (Text User Interface) for easy navigation and management, and uses a SQLite database with SQLAlchemy ORM for robust data storage.

### Key Features
- **Lot, Site, and Shipment Management:** Create, view, update, and delete records for lots, sites, and shipments.
- **Inventory Tracking:** Track inventory levels for each lot at each site, with automatic updates when shipments arrive or stock is used.
- **Usage Analytics:** Calculate usage rates, predict run-out dates, and estimate leftover quantities based on expiration dates and usage trends.
- **Dashboard Warnings:** Get warnings for lots nearing expiration, low inventory, or slow-moving stock.
- **Inventory Transfers:** Suggest transfers between sites to optimize stock levels.
- **Reporting:** Generate reports on stock levels, expirations, and usage by site.
- **Configurable Database Path:** Easily configure the database location, including support for network drives.
- **User-Friendly TUI:** Navigate between dashboard, lot, site, shipment, and inventory screens with keyboard shortcuts or menus.

## How It Works

1. **Database Setup:**
   - On first run, the app initializes a SQLite database with tables for Lots, Sites, Shipments, and Inventory.
   - All data is stored locally (or on a network drive if configured).

2. **Textual TUI:**
   - The app launches a terminal UI with a main dashboard, navigation menu, and dedicated screens for managing lots, sites, shipments, and inventory.
   - Data entry and editing is performed via TUI forms.

3. **Inventory Logic:**
   - When shipments are received or stock is used, inventory levels are updated automatically.
   - The app calculates usage rates and predicts when lots will run out or expire.
   - Warnings and suggestions (such as transfers) are displayed on the dashboard.

4. **Reporting:**
   - Users can generate simple reports on current stock, upcoming expirations, and usage trends.

5. **Testing and Packaging:**
   - The project includes unit tests for core logic and database operations.
   - The app can be packaged and distributed using modern Python packaging tools (e.g., Hatch).

## Installation

```console
pip install inv
```

## Getting Started

1. Run the app from the command line:
   ```console
   inv
   ```
2. Follow the on-screen instructions to navigate and manage your inventory.
3. Configure the database path if you wish to use a network drive (see app settings or CLI options).

## For Developers

### Setting Up a Development Environment

```console
# Clone the repository
git clone https://github.com/maccam912/inv.git
cd inv

# Set up development environment with Hatch
hatch env create
```

### Running Tests

```console
# Run all tests
hatch run test

# Run with code coverage
hatch run cov
```

### Building the Package

The project uses Hatch for packaging and distribution:

```console
# Build the package (creates both wheel and sdist)
hatch build

# Resulting distribution files will be in the dist/ directory
ls dist/
```

### Installing the Development Version

```console
# Install the package in development mode
hatch env run pip install -e .
```

### Quality Checks

```console
# Run all checks (formatting, linting, type checking, tests)
hatch run check

# Format the code
hatch run format

# Run type checking
hatch run typecheck
```



## Roadmap

The project is developed in phases:

- **Phase 1:** Core data structures and database setup
- **Phase 2:** TUI skeleton and navigation
- **Phase 3:** Shipment and inventory tracking
- **Phase 4:** Business logic and warnings
- **Phase 5:** Advanced features and refinements
- **Phase 6:** Testing, documentation, and deployment

See the `issues.txt` file for a detailed breakdown of planned features and development phases.

## License

`inv` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
