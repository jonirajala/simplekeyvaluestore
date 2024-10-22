"""
Operations are typically limited to put (set), get, and delete:

5. Concurrency Control
If multiple clients or threads can access the store simultaneously, you'll need to ensure thread safety:
Locks: Use mutexes or other locking mechanisms to prevent race conditions when multiple clients access or modify the store concurrently.
Optimistic Concurrency Control: Instead of locking, allow concurrent access and use a versioning mechanism to detect conflicts.


6. Data Serialization
When persisting data to disk or sending it over a network, you’ll need to convert the in-memory data (e.g., hash maps or trees) into a storable or transmittable format:
Serialization Formats: Choose a format like JSON, XML, or binary for converting your key-value pairs to a byte stream.
Deserialization: Implement the reverse process, where data is read back from disk and converted into the in-memory representation.

7. Implement Eviction Policies (Optional)
If your key-value store needs to manage memory usage (e.g., in an in-memory store like Redis), you’ll need an eviction policy to remove old or unused entries:
Least Recently Used (LRU): Evict the least recently accessed items when memory limits are reached.
Least Frequently Used (LFU): Evict the least frequently accessed items.
Time-to-Live (TTL): Expire keys after a predefined time.


8. Sharding and Scaling (Advanced)
As your store grows, a single server may not be sufficient to handle all the data. To scale, you can implement:
Sharding: Partition the key-value pairs across multiple machines. You can use consistent hashing to distribute the keys evenly across servers.
Replication: Store copies of data on multiple machines to improve fault tolerance and read performance.


10. Logging and Monitoring
Implement logging for tracking operations, especially when dealing with failures. You’ll need to log key actions (put, get, delete) as well as any errors or exceptional situations.
Monitoring tools should be added to track the performance of the key-value store, such as response times, memory usage, and the rate of key-value operations.

when to store in to storage instead of in memeoryu
Key Considerations:
Durability: Ensuring that data is not lost in the event of a system crash or failure.
Performance: Minimizing the performance overhead introduced by persisting data to disk.
Latency: The time delay between writing data and it being safely stored.
Consistency: Ensuring that what’s stored in memory matches what’s on disk at any given time.

Start with basic filesystem and move to a more effiecient one later
- start with pickle

### GOAL IS TO HAVE ZERO DEPENDENCIES

"""
import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class KVStore:
    def __init__(self, filename=None):
        self.filename = filename
        try:
            self._load()
            print(f"{self.filename} loaded successfully")
        except FileNotFoundError:
            self.store = {}
            self._save()
            print(f"{self.filename} not found. New file created.")
        
    def put(self, key, val):
        # Insert or update a value associated with a key
        self.store[key] = val
        self._save()

    def get(self, key):
        # Retrieve a value by its key
        if not key in self.store:
            raise KeyError(f"Key {key} not found.")  # Update the error message format

        return self.store[key]

    def delete(self, key):
        # Remove a key-value pair
        if not key in self.store:
            raise KeyError(f"Key {key} not found.")  # Update the error message format
        del self.store[key]
        self._save()
    
    def get_all(self):
        # Return all key-value pairs
        return self.store

    def _save(self):
        with open(self.filename, 'wb') as handle:
            pickle.dump(self.store, handle)
    
    def _load(self):
        with open(self.filename, 'rb') as handle:
            self.store = pickle.load(handle)



app = FastAPI()

store = KVStore("kvstore.pkl")

class PutRequest(BaseModel):
    key: str
    value: str

@app.get("/get/{key}")
async def get_value(key: str):
    try:
        value = store.get(key)
        return {"key": key, "value": value}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/put/")
async def put_value(request: PutRequest):
    store.put(request.key, request.value)
    return {"message": "Value inserted/updated successfully", "key": request.key, "value": request.value}

@app.delete("/delete/{key}")
async def delete_value(key: str):
    try:
        store.delete(key)
        return {"message": f"Key '{key}' deleted successfully"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/showdb/")
async def show_database():
    return {"database": store.get_all()}