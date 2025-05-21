import tempfile
import os
import sqlite3

# Test 1: With context manager - this will fail on Windows
print("Test 1: With context manager")
try:
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        print(f"Created temp file: {tmp.name}")
        # Try to open the file with sqlite3
        conn = sqlite3.connect(tmp.name)
        print("Successfully opened database with sqlite3")
        conn.close()
except Exception as e:
    print(f"Error: {e}")

# Test 2: With delete=False - this should work on all platforms
print("\nTest 2: With delete=False")
try:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_path = tmp.name
    print(f"Created temp file: {tmp_path}")
    tmp.close()  # Close the file handle explicitly
    
    # Try to open the file with sqlite3
    conn = sqlite3.connect(tmp_path)
    print("Successfully opened database with sqlite3")
    conn.close()
    
    # Clean up
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
        print(f"Deleted temp file: {tmp_path}")
except Exception as e:
    print(f"Error: {e}")