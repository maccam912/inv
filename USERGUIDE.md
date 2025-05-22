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

### Key Benefits

- **Centralized Tracking**: Manage all your inventory information in one place
- **Lot-Based Management**: Track products by lot numbers with associated expiration dates
- **Multi-Site Support**: Monitor inventory across different physical locations
- **Proactive Warnings**: Get alerts about expiring products or low inventory levels
- **Optimization Suggestions**: Receive recommendations for inventory transfers to maximize efficiency
- **Usage Analytics**: Understand consumption patterns and predict future needs
- **Terminal-Based Interface**: Operate efficiently with keyboard shortcuts in a lightweight interface
- **Data Persistence**: Store all inventory data securely in a SQLite database

### Ideal Use Cases

- **Laboratory Supply Management**: Track reagents and materials with expiration dates
- **Food Distribution**: Monitor perishable items across multiple locations
- **Medical Supply Tracking**: Ensure critical supplies are available where needed
- **Retail Inventory**: Manage stock levels across multiple store locations
- **Small Warehouse Operations**: Track incoming and outgoing shipments

Whether you're managing a small warehouse, distributing products across retail locations, or tracking laboratory supplies, `inv` provides the tools you need to maintain optimal inventory levels and reduce waste from expired products.

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

#### Database Path Format

The database path follows SQLAlchemy's connection string format:

- **Local SQLite database**: `sqlite:///inventory.db` (default, relative path)
- **Absolute path**: `sqlite:////absolute/path/to/inventory.db` (note the four slashes)
- **In-memory database** (for testing): `sqlite:///:memory:`
- **Network drive**: `sqlite:////server/share/path/to/inventory.db`

#### Current Configuration Methods

Currently, the application initializes the database with this default location. To change it, you have these options:

1. **Custom Implementation**: Fork the repository and modify the `init_db()` call in `app.py`
2. **Environment Variable**: Future versions may support configuration via environment variables
3. **Command Line Arguments**: Future versions may add command-line options for database configuration

**Note**: When using a network drive, ensure all users have appropriate permissions to read and write to the database file.

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

### Advanced Usage Patterns

#### Multi-Site Inventory Management

For organizations managing inventory across multiple locations:

1. **Centralized Distribution**: Set up a main warehouse as a central site, with smaller satellite sites
2. **Transfer Workflow**: 
   - Create shipments from the central site to satellite sites based on needs
   - Record arrivals at destination sites
   - Monitor inventory levels at all sites from the dashboard

#### Lot Batch Tracking

For products with critical expiration management:

1. **FIFO Implementation**: Use the expiration date and lot information to ensure First In, First Out usage
2. **Expiration Monitoring**: Regularly check the dashboard for expiration warnings
3. **Strategic Transfers**: Transfer lots approaching expiration to high-usage sites

#### Inventory Optimization

For minimizing waste and maximizing availability:

1. **Usage Pattern Analysis**: Use the reports screen to identify usage patterns
2. **Strategic Distribution**: Distribute inventory based on usage rates at different sites
3. **Just-In-Time Inventory**: Use run-out predictions to time new shipments to arrive just before stock depletion

## Keyboard Shortcuts

The application provides efficient keyboard navigation with the following global shortcuts:

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

### Screen-Specific Actions

Each screen in the application may also support these common actions:

- **Add/Create**: Add a new record (lot, site, shipment, etc.)
- **Edit/Update**: Modify an existing record
- **Delete**: Remove a record
- **Filter/Search**: Filter or search through records
- **Sort**: Change the sorting of displayed data
- **Refresh**: Refresh data display

### Form Navigation

When working with forms:

- **Tab**: Move to the next field
- **Shift+Tab**: Move to the previous field
- **Enter**: Submit the form (when on a submit button)
- **Escape**: Cancel and close the form

### Table Navigation

When working with data tables:

- **Up/Down Arrow Keys**: Navigate between rows
- **Enter/Double-click**: Select a row for detailed view or editing
- **Page Up/Page Down**: Scroll through larger datasets

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