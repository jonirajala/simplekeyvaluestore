# Simple Key-value store

## Usage

Start server
```
python3 -m uvicorn keyvaluestore:app --reload
```

Talk with db
```
curl -X 'POST' \
 'http://127.0.0.1:8000/put/' \
 -H 'Content-Type: application/json' \
 -d '{
"key": "exampleKey",
"value": "exampleValue"
}'
```
```
curl -X 'GET' \
 'http://127.0.0.1:8000/get/exampleKey'
```
```
curl -X 'DELETE' \
 'http://127.0.0.1:8000/delete/exampleKey'
```
```
curl -X 'GET' \
 'http://127.0.0.1:8000/showdb/'
```
## Testing

Speed test
```
python3 -m pytest speedtest.py -s
```
Basic tests
```
python3 -m pytest test_kvstore.py
```
## Current performance

- Inserting 1000 key-value pairs took 0.7074 seconds.
- Retrieving 1000 key-value pairs took 0.5389 seconds.
- Deleting 1000 key-value pairs took 0.6929 seconds.
