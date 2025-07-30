# Milvus Tools
### Initializaion
```python
from feliz_milvus.crud_tools import MilvusHandler

configs = {
    "alias": "connection_alias",
    "host": "localhost",
    "port": 19530,
    "database": "milvus",
    "username": "milvus",
    "password": "milvus"
}

DH = MilvusHandler(**configs)
```


Users can use the `add_data`, `search_data`, `search_iterator_data`, `query_data`, `query_iterator_data`, `delete_data` methods to add, delete and get data from a collection



### Add data

#### list of columns
```python
DH.add_data(
    collection_name="collection_name", 
    data=[
        [0,1,2],                         # id
        [                                    # vector
            [0.1,0.2,-0.3],
            [0.3,-0.1,-0.2],
            [-0.6,-0.3,0.2]
        ]
    ]
)
```

#### data frame
```python
DH.add_data(
    collection_name="collection_name", 
    data=pd.DataFrame({
        "id": [0,1,2],
        "vector": [
            [0.1,0.2,-0.3],
            [0.3,-0.1,-0.2],
            [-0.6,-0.3,0.2]
        ]
    })
)
```
#### list of dictionaries
```python
DH.add_data(
    collection_name="collection_name", 
    data=[
        {"id": 0, "vector": [0.1,0.2,-0.3]},
        {"id": 1, "vector": [0.3,-0.1,-0.2]},
        {"id": 2, "vector": [-0.6,-0.3,0.2]}
    ]
)
```
#### dictionary
```python
DH.add_data(
    collection_name="collection_name", 
    data={"id": 0, "vector": [0.1,0.2,-0.3]}
)
```
### Get data
#### search
This operation conducts a vector similarity search with an optional scalar filtering expression.
```python
DH.search_data(
    collection_name: str,
    data: list[list[float]],
    anns_field: str,
    param: dict,
    limit: int,
    expression: str | None,
    partition_names: list[str] | None,
    output_fields: list[str] | None,
    timeout: float | None,
    round_decimal: int,
    format_data: bool
)
```
#### search_iterator
This operation returns a Python iterator for you to iterate over the search results.
```python
DH.search_iterator_data(
    collection_name: str,
    batch_size: int, 
    data: list[list[float]], 
    anns_field: str, 
    param: dict, 
    limit: int, 
    expression: str | None, 
    partition_names: list[str] | None, 
    output_fields: list[str] | None, 
    timeout: float | None, 
    round_decimal: int
)

```
#### query
This operation conducts a scalar filtering with a specified boolean expression.
```python
DH.query_data(
    collection_name: str,
    expression: str, 
    output_fields: list[str] | None, 
    partition_names: list[str] | None, 
    timeout: float | None,
    format_data: bool
)
```
#### query_iterator
This operation returns a Python iterator for you to iterate over the query results.
```python
DH.query_iterator_data(
    collection_name: str,
    batch_size: int,
    limit: int,
    expression: str | None,
    output_fields: list[str] | None,
    partition_names: list[str] | None,
    timeout: float | None
)
```
### Delete data
```python
DH.delete_data(
    collection_name: str, 
    expression: str | None
)
```

## MilvusModelHandler & MilvusField

### Define a collection schema
User can create a model by inheriting the `MilvusModelHandler` class and defining the fields by `MilvusField` class.

```python
from feliz_milvus.collection_tools import MilvusCollectionHandler, MilvusField

class TestCollection(MilvusCollectionHandler):
    _id = MilvusField(dtype=DataType.INT64, is_primary=True, auto_id=True)
    embedding = MilvusField(
        dtype=DataType.FLOAT_VECTOR, 
        dim=128,
        description="128-d vector",
        index_params={
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
        }
    )
    timestamp_ms = MilvusField(dtype=DataType.INT64, description="timestamp in ms")
    create_at = MilvusField(dtype=DataType.VARCHAR, description="create_at", max_length=64)

    ttl_seconds = 1800

    meta = {
        "alias" : "connection_alias",
        "collection" : "TestCollection"
    }
```
### Create a collection
```python
configs = {
    "alias": "alias",
    "host": "localhost",
    "port": 19530,
    "database": "milvus",
    "username": "milvus",
    "password": "milvus"
}

DH = MilvusHandler(**configs)
TestCollection.create_collection(DH)
```
## Expression rule
- Comparison Operators: ==, !=, >, <, >=, and <= allow filtering based on numeric or text fields.

- Range Filters: IN and LIKE help match specific value ranges or sets.

- Arithmetic Operators: +, -, *, /, %, and ** are used for calculations involving numeric fields.

- Logical Operators: AND, OR, and NOT combine multiple conditions into complex expressions.
