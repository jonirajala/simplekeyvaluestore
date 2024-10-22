import pytest
import time
import requests
import threading
from time import sleep
from keyvaluestore import run  # Replace with the actual name of your server module
import os

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module", autouse=True)
def start_server():
    os.environ['DISABLE_LOGS'] = '1'
  # Run the server in a separate thread to allow testing
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()
    sleep(1)  # Give the server some time to start
    yield
    # No explicit shutdown mechanism; server will stop when the test exits due to daemon=True

  
@pytest.fixture(autouse=True)
def clear_store():
    # Assuming your server has an endpoint to clear the store. If not, you'll need to implement it.
    response = requests.get(f"{BASE_URL}/showdb/")
    data = response.json()
    for key in data.get("database", {}):
        requests.delete(f"{BASE_URL}/delete/{key}")

def test_speed_of_inserts():
    num_operations = 1000  # Adjust this value based on the performance you'd like to measure
    start_time = time.time()
    
    # Insert a large number of key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        value = f"value{i}"
        response = requests.post(f"{BASE_URL}/put/", json={"key": key, "value": value})
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
        requests.post(f"{BASE_URL}/put/", json={"key": key, "value": value})

    start_time = time.time()
    
    # Retrieve all key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        response = requests.get(f"{BASE_URL}/get/{key}")
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
        requests.post(f"{BASE_URL}/put/", json={"key": key, "value": value})

    start_time = time.time()
    
    # Delete all key-value pairs
    for i in range(num_operations):
        key = f"key{i}"
        response = requests.delete(f"{BASE_URL}/delete/{key}")
        assert response.status_code == 200
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Deleting {num_operations} key-value pairs took {elapsed_time:.4f} seconds.")
    assert elapsed_time < 5.0  # Set an appropriate time threshold
