# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT
import os
import tempfile

import pytest
from sqlalchemy.engine.base import Engine

from inv.db.models import init_db
from inv.tui.app import InventoryApp


def test_db_initialization_default():
    """Test that database initialization uses default path when none is provided."""
    session_factory = init_db()
    # Get the engine from the session factory
    engine = session_factory.kw["bind"]
    # Check that the default path is being used
    assert str(engine.url) == "sqlite:///inventory.db"


def test_db_initialization_custom():
    """Test that database initialization uses custom path when provided."""
    custom_path = "sqlite:///custom_inventory.db"
    session_factory = init_db(custom_path)
    # Get the engine from the session factory
    engine = session_factory.kw["bind"]
    # Check that the custom path is being used
    assert str(engine.url) == custom_path


def test_app_uses_custom_db_path():
    """Test that the app uses the provided database path."""
    # Use a temporary file to ensure we don't affect real database files
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = f"sqlite:///{tmp.name}"
        app = InventoryApp(db_path=db_path)
        
        # Get the engine from the session factory
        engine = app.Session.kw["bind"]
        
        # Check that the app is using the provided database path
        assert str(engine.url) == db_path