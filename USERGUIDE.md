# Inventory Management TUI (inv) - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Core Functionality](#core-functionality)
   - [Managing Lots](#managing-lots)
   - [Managing Sites](#managing-sites)
   - [Managing Shipments](#managing-shipments)
   - [Tracking Inventory](#tracking-inventory)
   - [Reports](#reports)
6. [Advanced Features](#advanced-features)
   - [Dashboard Warnings](#dashboard-warnings)
   - [Inventory Transfer Suggestions](#inventory-transfer-suggestions)
   - [Usage Analytics](#usage-analytics)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Troubleshooting](#troubleshooting)

## Introduction

`inv` is a terminal-based inventory management application designed for organizations that need to track lots, shipments, and inventory levels across multiple sites. It features a modern Text User Interface (TUI) for easy navigation and management, and uses a SQLite database with SQLAlchemy ORM for robust data storage.

The application helps you:
- Track lots, sites, shipments, and inventory levels
- Monitor usage rates and predict stock depletion
- Get warnings about expiring or low inventory
- Optimize inventory allocation through transfer suggestions
- Generate reports on current stock, expirations, and usage trends

## Installation

### System Requirements

- Python 3.12 or higher
- Terminal with support for modern TUI applications
- Recommended: Terminal with true color support for the best experience

### Installation Steps

1. Install using pip:
   ```bash
   pip install inv
   ```

2. Verify installation:
   ```bash
   inv --version
   ```
   This should display the version number of the installed package.

## Configuration

### Database Configuration

By default, `inv` uses a local SQLite database file (`inventory.db`) in the current working directory. You can configure a custom database path for scenarios like:

- Using a network drive for multi-user access
- Specifying a different local storage location

#### Command Line Options

Currently, the application does not have command line options for database configuration. Future versions may add this functionality.

#### Manual Configuration

To manually configure the database location:

1. Locate the database initialization in your application code (typically in `app.py`)
2. Modify the `init_db()` call to specify a custom database path:
   ```python
   # Example (for reference only):
   self.Session: sessionmaker = init_db("sqlite:///path/to/your/inventory.db")
   ```

#### Network Drive Configuration

To use a network drive for the database:

1. Ensure the network drive is properly mounted
2. Use a full path to the network location:
   ```
   sqlite:////network/path/to/inventory.db
   ```

## Basic Usage

### Starting the Application

Run the application from the command line:
```bash
inv
```

This launches the TUI interface with the main dashboard.

### UI Navigation

The application has a tabbed interface with the following main screens:

1. **Dashboard**: Displays overview information, warnings, and suggestions
2. **Lots**: Manage product lots
3. **Sites**: Manage storage locations
4. **Shipments**: Track movement of lots between sites
5. **Inventory**: View and manage current inventory levels
6. **Reports**: Generate and view reports

Navigate between screens using:
- The keyboard shortcuts (see [Keyboard Shortcuts](#keyboard-shortcuts))
- Clicking on the tabs at the top of the interface

### Main Dashboard

The dashboard provides an overview of your inventory system:

- **Summary Statistics**: Total lots, sites, and current inventory levels
- **Warnings**: Notifications about expiring lots or low inventory
- **Transfer Suggestions**: Recommendations to optimize inventory allocation

## Core Functionality

### Managing Lots

Lots represent batches of products with unique identifiers and expiration dates.

#### Creating a Lot

1. Navigate to the Lots screen using the `l` key
2. Click "Add Lot" or use the appropriate shortcut
3. Fill in the required information:
   - **Lot Number**: A unique identifier for the lot (required)
   - **Expiration Date**: When the lot will expire (required)
   - **Initial Quantity**: The original quantity of items in the lot (required)
4. Save the lot

#### Viewing Lots

The Lots screen displays a table of all lots with:
- Lot number
- Expiration date
- Initial quantity
- Current total inventory across all sites
- Status indicators (e.g., warnings for approaching expiration)

#### Editing a Lot

1. Select the lot you want to edit in the lots table
2. Click "Edit" or use the appropriate shortcut
3. Modify the lot details
4. Save your changes

#### Deleting a Lot

1. Select the lot you want to delete in the lots table
2. Click "Delete" or use the appropriate shortcut
3. Confirm the deletion

### Managing Sites

Sites represent physical locations where inventory is stored.

#### Creating a Site

1. Navigate to the Sites screen using the `s` key
2. Click "Add Site" or use the appropriate shortcut
3. Fill in the required information:
   - **Site Name**: A unique identifier for the site (required)
   - **Contact Information**: Details about the site (optional)
4. Save the site

#### Viewing Sites

The Sites screen displays a table of all sites with:
- Site name
- Contact information
- Current total inventory at the site
- Number of different lots at the site

#### Editing a Site

1. Select the site you want to edit in the sites table
2. Click "Edit" or use the appropriate shortcut
3. Modify the site details
4. Save your changes

#### Deleting a Site

1. Select the site you want to delete in the sites table
2. Click "Delete" or use the appropriate shortcut
3. Confirm the deletion

### Managing Shipments

Shipments track the movement of lots between sites.

#### Creating a Shipment

1. Navigate to the Shipments screen using the `h` key
2. Click "Add Shipment" or use the appropriate shortcut
3. Fill in the required information:
   - **Lot Number**: The lot being shipped (select from existing lots)
   - **Site Name**: The destination site (select from existing sites)
   - **Shipment Date**: When the shipment was sent
   - **Quantity Shipped**: Number of items in the shipment
   - **Anticipated Arrival Date**: Expected arrival date (optional)
4. Save the shipment

#### Recording Shipment Arrival

When a shipment arrives at its destination:

1. Select the shipment in the shipments table
2. Click "Record Arrival" or use the appropriate shortcut
3. The inventory at the destination site will be automatically updated

#### Viewing Shipments

The Shipments screen displays a table of all shipments with:
- Shipment ID
- Lot number
- Destination site
- Shipment date
- Quantity shipped
- Anticipated arrival date
- Status (pending or arrived)

#### Deleting a Shipment

1. Select the shipment you want to delete in the shipments table
2. Click "Delete" or use the appropriate shortcut
3. Confirm the deletion

### Tracking Inventory

The Inventory screen shows the current stock levels for each lot at each site.

#### Viewing Inventory

The Inventory screen displays a table of inventory records with:
- Lot number
- Site name
- Current quantity
- Last updated date
- Usage rate (if available)
- Estimated run-out date (if available)

#### Recording Stock Usage

To record that stock has been used from a site:

1. Navigate to the Inventory screen using the `i` key
2. Select the inventory record for the lot and site
3. Click "Record Usage" or use the appropriate shortcut
4. Enter the quantity used
5. Save the usage record

### Reports

The Reports screen allows you to generate and view various reports about your inventory.

#### Available Reports

1. **Current Stock Levels**: Shows inventory levels for all lots across all sites
2. **Expiration Report**: Lists lots that will expire within a specified time frame
3. **Usage Trends**: Shows usage rates and patterns for lots
4. **Site Inventory**: Detailed inventory breakdown for a specific site

#### Generating a Report

1. Navigate to the Reports screen using the `r` key
2. Select the report type
3. Configure any report parameters (e.g., date range, specific site)
4. Click "Generate Report"
5. View the report results in the table

## Advanced Features

### Dashboard Warnings

The dashboard automatically displays warnings about:

1. **Expiring Lots**: Lots that will expire within a defined time period
2. **Low Inventory**: Sites with critically low inventory levels
3. **Slow-Moving Stock**: Lots with unusually low usage rates
4. **High Usage Rate**: Lots being consumed faster than expected

### Inventory Transfer Suggestions

The application analyzes inventory levels and usage rates to suggest optimal inventory transfers between sites.

#### Transfer Suggestion Criteria

Suggestions are based on:
- Current inventory levels at each site
- Historical usage rates
- Predicted run-out dates
- Lot expiration dates

#### Implementing a Transfer

To implement a suggested transfer:

1. Review the transfer suggestion on the dashboard
2. Create a new shipment based on the suggestion details
3. When the transfer is complete, record the shipment arrival

### Usage Analytics

The application tracks and analyzes inventory usage to provide insights.

#### Usage Rate Calculation

Usage rates are calculated based on:
- Historical usage records
- Time period of usage
- Seasonal patterns (if applicable)

#### Predictions

Based on usage rates, the application predicts:
- When inventory will run out at each site
- How much inventory will remain at expiration
- Optimal reorder times

## Keyboard Shortcuts

The application supports the following keyboard shortcuts:

| Key | Function | Description |
|-----|----------|-------------|
| `d` | Toggle Dark Mode | Switch between light and dark display modes |
| `l` | Show Lots | Navigate to the Lots screen |
| `s` | Show Sites | Navigate to the Sites screen |
| `h` | Show Shipments | Navigate to the Shipments screen |
| `i` | Show Inventory | Navigate to the Inventory screen |
| `r` | Show Reports | Navigate to the Reports screen |
| `b` | Back to Dashboard | Return to the main dashboard |
| `q` | Quit | Exit the application |

Additionally, each screen may have its own specific shortcuts for common actions.

## Troubleshooting

### Common Issues and Solutions

#### Database Connection Errors

**Issue**: Unable to connect to the database
**Solution**:
- Ensure the database file exists at the expected location
- Check file permissions on the database file
- If using a network drive, verify network connectivity

#### Display Issues

**Issue**: UI elements appear misaligned or corrupted
**Solution**:
- Ensure your terminal supports TUI applications
- Try resizing your terminal window
- Toggle between light and dark mode with the `d` key

#### Performance Issues

**Issue**: Application becomes slow with large datasets
**Solution**:
- Consider archiving old data that's no longer needed
- Ensure your database file is not excessively large
- If using a network drive, check network performance

### Data Recovery

If you need to recover data from a corrupted database:

1. Make a backup copy of your database file
2. Try using SQLite recovery tools to recover the data
3. If unsuccessful, restore from your most recent backup

### Getting Help

If you encounter issues not covered in this guide:

1. Check for updated documentation on the project GitHub page
2. Submit an issue on the project's issue tracker
3. Include detailed information about your system and the problem you're experiencing