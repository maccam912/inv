# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for the inventory screen."""

from contextlib import contextmanager
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session
from textual.widgets import DataTable

from inv.db.models import Inventory
from inv.tui.inventory_screen import InventoryScreen


@pytest.fixture
def mock_session():
    """Create a mock session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_session_factory(mock_session):
    """Create a mock session factory."""

    @contextmanager
    def _session_factory():
        yield mock_session

    return _session_factory


@pytest.fixture
def mock_inventories():
    """Create mock inventory data."""
    inventory1 = MagicMock(spec=Inventory)
    inventory1.inventory_id = 1
    inventory1.lot_number = "LOT-001"
    inventory1.site_name = "SITE-A"
    inventory1.current_quantity = 100
    inventory1.last_updated_date = date(2023, 5, 15)

    inventory2 = MagicMock(spec=Inventory)
    inventory2.inventory_id = 2
    inventory2.lot_number = "LOT-002"
    inventory2.site_name = "SITE-B"
    inventory2.current_quantity = 50
    inventory2.last_updated_date = date(2023, 6, 20)

    return [inventory1, inventory2]


def test_inventory_screen_refresh(mock_session_factory, mock_session, mock_inventories):
    """Test that the inventory screen refreshes correctly."""
    # Setup
    mock_session.query.return_value.all.return_value = mock_inventories
    with patch(
        "inv.tui.inventory_screen.read_inventories", return_value=mock_inventories
    ):
        # Create the screen
        screen = InventoryScreen(mock_session_factory)

        # Mock DataTable
        mock_table = MagicMock(spec=DataTable)
        screen.inventory_table = mock_table
        screen.query_one = MagicMock(return_value=mock_table)

        # Call the refresh method
        screen.refresh_inventory()

        # Assertions
        mock_table.clear.assert_called_once()
        expected_row_count = len(mock_inventories)
        assert mock_table.add_row.call_count == expected_row_count

        # Check the data in the rows
        mock_table.add_row.assert_any_call(
            "LOT-001",
            "SITE-A",
            "100",
            "2023-05-15",
            key="LOT-001-SITE-A",
        )
        mock_table.add_row.assert_any_call(
            "LOT-002",
            "SITE-B",
            "50",
            "2023-06-20",
            key="LOT-002-SITE-B",
        )
