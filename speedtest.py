"""
python3 -m pytest speedtest.py -s

first version 22.10
Inserting 1000 key-value pairs took 0.7074 seconds.
Retrieving 1000 key-value pairs took 0.5389 seconds.
Deleting 1000 key-value pairs took 0.6929 seconds.

"""

import pytest
import time
from fastapi.testclient import TestClient
from keyvaluestore import app, store  # Replace 'keyvaluestore' with your actual Python file name

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
    # Clear the store before each test
    store.store.clear()
    store._save()

def test_speed_of_inserts():
    num_operations = 1000  # Adjust this value based on the performance you'd like to measure
    start_time = time.time()
    
    # Insert a large number of key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        value = f"value{i}"
        response = client.post("/put/", json={"key": key, "value": value})
        assert response.status_code == 200
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Inserting {num_operations} key-value pairs took {elapsed_time:.4f} seconds.")
    assert elapsed_time < 5.0  # Set an appropriate time threshold for your use case

def test_speed_of_retrievals():
    num_operations = 1000
    # First, insert the key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        value = f"value{i}"
        client.post("/put/", json={"key": key, "value": value})

    start_time = time.time()
    
    # Retrieve all key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        response = client.get(f"/get/{key}")
        assert response.status_code == 200
        assert response.json()["value"] == f"value{i}"
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Retrieving {num_operations} key-value pairs took {elapsed_time:.4f} seconds.")
    assert elapsed_time < 5.0  # Set an appropriate time threshold

def test_speed_of_deletes():
    num_operations = 1000
    # First, insert the key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        value = f"value{i}"
        client.post("/put/", json={"key": key, "value": value})

    start_time = time.time()
    
    # Delete all key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        response = client.delete(f"/delete/{key}")
        assert response.status_code == 200
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Deleting {num_operations} key-value pairs took {elapsed_time:.4f} seconds.")
    assert elapsed_time < 5.0  # Set an appropriate time threshold
