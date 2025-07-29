# Auto_connect_mongo

A Python package for connecting to MongoDB and performing basic CRUD operations.

---

## Installation

```bash
pip install Auto_connect_mongo
```
Or, to install from source:
```bash
git clone https://github.com/AnandVadgama/my-py-package.git
cd my-py-package
pip install -r requirements.txt
```

---

## Usage

### Connect to MongoDB

```python
from Auto_connect_mongo.mongo_crud import mongo_operation

client_url = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/"
database_name = "my_database"
collection_name = "my_collection"

mongo_op = mongo_operation(client_url, database_name, collection_name)
```

### Insert a Record

```python
record = {"name": "Alice", "age": 30}
mongo_op.insert_record(record, collection_name)
```

### Find Records

```python
query = {"age": {"$gt": 25}}
results = mongo_op.find_record(query, collection_name)
for doc in results:
    print(doc)
```

### Update a Record

```python
query = {"name": "Alice"}
update = {"$set": {"age": 31}}
mongo_op.update_record(query, update, collection_name)
```

### Delete a Record

```python
query = {"name": "Alice"}
mongo_op.delete_record(query, collection_name)
```

---

## Requirements

- Python 3.7+
- MongoDB instance (local or Atlas)

---

## Testing

```bash
pip install -r requirements_dev.txt
pytest
```

---

For more details, see the source code or open an issue on GitHub.