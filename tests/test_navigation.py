# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for the navigation between screens."""

from unittest.mock import Mock

from textual.widgets import TabbedContent

from inv.tui.app import InventoryApp


def test_navigation_actions():
    """Test that navigation actions correctly set the active tab."""
    # Create mocks
    mock_tabbed_content = Mock()
    mock_query = Mock(return_value=mock_tabbed_content)

    # Create an instance of the app with mocked query_one
    app = InventoryApp()
    app.query_one = mock_query

    # Test show_lots action
    app.action_show_lots()
    # Assert the query_one was called with the correct ID
    mock_query.assert_called_with("#screen_tabs", TabbedContent)
    # Assert the active tab was set correctly
    assert mock_tabbed_content.active == "lot_tab"

    # Test show_sites action
    app.action_show_sites()
    mock_query.assert_called_with("#screen_tabs", TabbedContent)
    assert mock_tabbed_content.active == "site_tab"

    # Test back_to_dashboard action
    app.action_back_to_dashboard()
    mock_query.assert_called_with("#screen_tabs", TabbedContent)
    assert mock_tabbed_content.active == "dashboard_tab"
