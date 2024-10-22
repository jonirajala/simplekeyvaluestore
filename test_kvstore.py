import pytest
from fastapi.testclient import TestClient
from keyvaluestore import app, store

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
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
    client.post("/put/", json={"key": "testKey", "value": "testValue"})
    
    response = client.get("/get/testKey")
    assert response.status_code == 200
    assert response.json() == {"key": "testKey", "value": "testValue"}

def test_get_value_not_found():
    response = client.get("/get/nonExistentKey")
    assert response.status_code == 404

def test_delete_value():
    client.post("/put/", json={"key": "testKey", "value": "testValue"})
    
    response = client.delete("/delete/testKey")
    assert response.status_code == 200
    assert response.json() == {"message": "Key 'testKey' deleted successfully"}

def test_delete_value_not_found():
    response = client.delete("/delete/nonExistentKey")
    assert response.status_code == 404

def test_show_database():
    client.post("/put/", json={"key": "key1", "value": "value1"})
    client.post("/put/", json={"key": "key2", "value": "value2"})
    
    response = client.get("/showdb/")
    assert response.status_code == 200
    assert response.json() == {
        "database": {
            "key1": "value1",
            "key2": "value2",
        }
    }
