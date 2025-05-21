import sys
import os
import tempfile

# Add the project directory to the path
sys.path.insert(0, os.path.abspath('/home/runner/work/inv/inv'))

# Import the necessary modules
from inv.db.models import init_db
from inv.tui.app import InventoryApp

# Test that database initialization uses default path when none is provided
def test_db_initialization_default():
    session_factory = init_db()
    # Get the engine from the session factory
    engine = session_factory.kw["bind"]
    # Check that the default path is being used
    assert str(engine.url) == "sqlite:///inventory.db"
    print("test_db_initialization_default passed")

# Test that database initialization uses custom path when provided
def test_db_initialization_custom():
    custom_path = "sqlite:///custom_inventory.db"
    session_factory = init_db(custom_path)
    # Get the engine from the session factory
    engine = session_factory.kw["bind"]
    # Check that the custom path is being used
    assert str(engine.url) == custom_path
    print("test_db_initialization_custom passed")

# Test that the app uses the provided database path
def test_app_uses_custom_db_path():
    # Use a temporary file for the test
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = f"sqlite:///{tmp.name}"
        print(f"Using temporary file: {tmp.name}")
        app = InventoryApp(db_path=db_path)

        # Get the engine from the session factory
        engine = app.Session.kw["bind"]
        
        # Check that the app is using the provided database path
        assert str(engine.url) == db_path
        print("test_app_uses_custom_db_path passed")

if __name__ == "__main__":
    test_db_initialization_default()
    test_db_initialization_custom()
    test_app_uses_custom_db_path()