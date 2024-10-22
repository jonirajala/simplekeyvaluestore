import pytest
from fastapi.testclient import TestClient
from keyvaluestore import app, store  # Replace 'your_filename' with your actual Python file name
import time

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
    # Clear the store before each test
    store.store.clear()
    store._save()

def test_put_value():
    response = client.post("/put/", json={"key": "testKey", "value": "testValue"})
    assert response.status_code == 200
    assert response.json() == {
        "message": "Value inserted/updated successfully",
        "key": "testKey",
        "value": "testValue",
    }

def test_get_value():
    # First, insert the key-value pair
    client.post("/put/", json={"key": "testKey", "value": "testValue"})
    
    # Now, retrieve the value
    response = client.get("/get/testKey")
    assert response.status_code == 200
    assert response.json() == {"key": "testKey", "value": "testValue"}

def test_get_value_not_found():
    # Try to get a key that doesn't exist
    response = client.get("/get/nonExistentKey")
    assert response.status_code == 404

def test_delete_value():
    # First, insert a key-value pair
    client.post("/put/", json={"key": "testKey", "value": "testValue"})
    
    # Now, delete the key
    response = client.delete("/delete/testKey")
    assert response.status_code == 200
    assert response.json() == {"message": "Key 'testKey' deleted successfully"}

def test_delete_value_not_found():
    # Try to delete a non-existent key
    response = client.delete("/delete/nonExistentKey")
    assert response.status_code == 404

def test_show_database():
    # First, insert a couple of key-value pairs
    client.post("/put/", json={"key": "key1", "value": "value1"})
    client.post("/put/", json={"key": "key2", "value": "value2"})
    
    # Now, retrieve the entire database
    response = client.get("/showdb/")
    assert response.status_code == 200
    assert response.json() == {
        "database": {
            "key1": "value1",
            "key2": "value2",
        }
    }
