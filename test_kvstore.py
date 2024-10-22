import pytest
import requests
import threading
from time import sleep
from keyvaluestore import run  # Replace with the actual name of your server module

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module", autouse=True)
def start_server():
    # Run the server in a separate thread to allow testing
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()
    sleep(1)  # Give the server some time to start
    yield
    # No explicit shutdown mechanism; server will stop when the test exits due to daemon=True

def test_put_value():
    response = requests.post(f"{BASE_URL}/put/", json={"key": "testKey", "value": "testValue"})
    assert response.status_code == 200
    assert response.json() == {
        "message": "Value inserted/updated successfully",
        "key": "testKey",
        "value": "testValue",
    }

def test_get_value():
    # First, insert a value
    requests.post(f"{BASE_URL}/put/", json={"key": "testKey", "value": "testValue"})
    
    response = requests.get(f"{BASE_URL}/get/testKey")
    assert response.status_code == 200
    assert response.json() == {"key": "testKey", "value": "testValue"}

def test_get_value_not_found():
    response = requests.get(f"{BASE_URL}/get/nonExistentKey")
    assert response.status_code == 404

def test_delete_value():
    # First, insert a value to delete
    requests.post(f"{BASE_URL}/put/", json={"key": "testKey", "value": "testValue"})
    
    response = requests.delete(f"{BASE_URL}/delete/testKey")
    assert response.status_code == 200
    assert response.json() == {"message": "Key 'testKey' deleted successfully"}

def test_delete_value_not_found():
    response = requests.delete(f"{BASE_URL}/delete/nonExistentKey")
    assert response.status_code == 404

def test_show_database():
    # Insert multiple key-value pairs
    requests.post(f"{BASE_URL}/put/", json={"key": "key1", "value": "value1"})
    requests.post(f"{BASE_URL}/put/", json={"key": "key2", "value": "value2"})
    
    response = requests.get(f"{BASE_URL}/showdb/")
    assert response.status_code == 200
    assert response.json() == {
        "database": {
            "key1": "value1",
            "key2": "value2",
        }
    }
