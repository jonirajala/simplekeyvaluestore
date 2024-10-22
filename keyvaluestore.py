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
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading 
import hashlib

def hash_key(key, num_shards):
        # Use a hash function to determine which shard to use
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % num_shards

class KVStore:
    def __init__(self, shard_id, shard_dir='shards', num_shards=4):
        self.shard_id = shard_id
        self.shard_dir = shard_dir
        self.num_shards = num_shards
        self.lock = threading.Lock()

        if not os.path.exists(self.shard_dir):
            os.makedirs(self.shard_dir)
        self.filename = f"{self.shard_dir}/shard_{self.shard_id}.pkl"

        try:
            self._load()
            print(f"Shard {self.shard_id} loaded successfully from {self.filename}")
        except:
            self.store = {}
            self._save()
            print(f"Shard {self.shard_id} created with new file {self.filename}")

    

    def put(self, key, val):
        shard_id = hash_key(key, self.num_shards)
        if shard_id == self.shard_id:  # Only write to this shard if it matches
            with self.lock:
                self.store[key] = val
                self._save()

    def get(self, key):
        shard_id = hash_key(key, self.num_shards)
        if shard_id == self.shard_id:
            with self.lock:
                if key not in self.store:
                    raise KeyError(f"Key {key} not found.")
                return self.store[key]
        else:
            raise KeyError(f"Key {key} not found in this shard.")

    def delete(self, key):
        shard_id = hash_key(key, self.num_shards)
        if shard_id == self.shard_id:
            with self.lock:
                if key not in self.store:
                    raise KeyError(f"Key {key} not found.")
                del self.store[key]
                self._save()

    def get_all(self):
        with self.lock:
            return self.store

    def _save(self):
        with open(self.filename, 'wb') as handle:
            pickle.dump(self.store, handle)

    def _load(self):
        with open(self.filename, 'rb') as handle:
            self.store = pickle.load(handle)


shards = [KVStore(i) for i in range(4)]  # Assuming 4 shards

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if os.getenv('DISABLE_LOGS') == '1':
            return
        super().log_message(format, *args)

    def _send_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path.startswith("/get/"):
            key = self.path.split("/get/")[1]
            try:
                shard_id = hash_key(key, len(shards))
                value = shards[shard_id].get(key)
                self._send_response(200, {"key": key, "value": value})
            except KeyError as e:
                self._send_response(404, {"error": str(e)})
        elif self.path == "/showdb/":
            all_data = {}
            for shard in shards:
                all_data.update(shard.get_all())
            self._send_response(200, {"database": all_data})
        else:
            self._send_response(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/put/":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            key = data.get("key")
            value = data.get("value")
            shard_id = int(hashlib.md5(key.encode()).hexdigest(), 16) % 4
            shards[shard_id].put(key, value)
            self._send_response(200, {"message": "Value inserted/updated successfully", "key": key, "value": value})

    def do_DELETE(self):
        if self.path.startswith("/delete/"):
            key = self.path.split("/delete/")[1]
            shard_id = int(hashlib.md5(key.encode()).hexdigest(), 16) % 4
            try:
                shards[shard_id].delete(key)
                self._send_response(200, {"message": f"Key '{key}' deleted successfully"})
            except KeyError as e:
                self._send_response(404, {"error": str(e)})

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()