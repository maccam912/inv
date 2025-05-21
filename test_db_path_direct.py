# Direct test script for database path configuration feature
import os
import tempfile

from inv.db.models import init_db
from inv.tui.app import InventoryApp


def main():
    """Test the database path configuration feature directly."""
    print("Testing database path configuration feature...")

    # Test default path
    print("Testing default path initialization...")
    session_factory = init_db()
    engine = session_factory.kw["bind"]
    print(f"Default database path: {engine.url}")
    assert str(engine.url) == "sqlite:///inventory.db"
    print("Default path test passed!")

    # Test custom path
    print("\nTesting custom path initialization...")
    custom_path = "sqlite:///custom_inventory.db"
    session_factory = init_db(custom_path)
    engine = session_factory.kw["bind"]
    print(f"Custom database path: {engine.url}")
    assert str(engine.url) == custom_path
    print("Custom path test passed!")

    # Test InventoryApp with custom path
    print("\nTesting InventoryApp with custom path...")
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = f"sqlite:///{tmp.name}"
        app = InventoryApp(db_path=db_path)
        engine = app.Session.kw["bind"]
        print(f"App database path: {engine.url}")
        assert str(engine.url) == db_path
    print("InventoryApp test passed!")

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()