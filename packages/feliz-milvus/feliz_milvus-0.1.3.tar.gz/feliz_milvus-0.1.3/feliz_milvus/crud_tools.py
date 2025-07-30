from pymilvus import connections, db, Collection, list_collections

from enum import Enum
import logging
import numpy as np

class CONNECTION_STATUS(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class MilvusSearchLimit(Enum):
    MAX_SEARCH_LIMIT = 16384
    MIN_SEARCH_LIMIT = 1

    @staticmethod
    def check_search_limit(limit):
        return limit < MilvusSearchLimit.MAX_SEARCH_LIMIT.value and limit > MilvusSearchLimit.MIN_SEARCH_LIMIT.value


class MilvusCatchError:
    """
    Decorator to catch error and return a dict with indicator and message.
    """
    def milvus_catch_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"[MilvusHandler] {func.__name__} failed: \n** {e} **")
                return {"indicator": False, "message": str(e)}
        return wrapper


class MilvusHandler:
    """
    MilvusHandler is the class to handle the Milvus database.

    Args:
        alias (str): The alias of the connection.
        host (str): The host of the database.
        port (int): The port of the database.
        database (str): The database name.
        username (str): The username of the database.
        password (str): The password of the database.
        connect_timeout (int, optional): The timeout of the connection.
    """
    def __init__(self, *, database: str, alias: str, host: str, port: int, username: str, password: str, **kwargs):
        self.db_type = "milvus"
        self.database = database
        self.alias = alias
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection_status = CONNECTION_STATUS.DISCONNECTED
        self.collection = {}
        self.keywords = kwargs

        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO)

        self.connect()
        self.disconnect()

    @MilvusCatchError.milvus_catch_error
    def connect(self):
        connections.connect(alias=self.alias, host=self.host,db_name=self.database, port=self.port, user=self.username, password=self.password, **self.keywords)
        self.connection_status = CONNECTION_STATUS.CONNECTED

    @MilvusCatchError.milvus_catch_error
    def disconnect(self):
        connections.disconnect(self.alias)
        self.connection_status = CONNECTION_STATUS.DISCONNECTED
    
    @MilvusCatchError.milvus_catch_error
    def get_collection(self, collection_name: str, **kwargs):
        """
        create a collection if it does not exist, and set the collection to the class.

        Args:
            - collection_name (str) : The name of the collection.
        Returns:
            - Collection : The collection object.
        """
        if collection_name not in self.collection:
            collection = Collection(name=collection_name, using=self.alias, **kwargs)
            self.collection[collection_name] = collection
        return self.collection[collection_name]
    
    @MilvusCatchError.milvus_catch_error
    def add_data(self, collection_name: str, data, **kwargs):
        """
        Args:
            - collection_name (str) : The name of the collection.
            - data (list) : The data to be inserted.
                The data should be a list of dictionaries, pandas.DataFrame, list of rows or just a row ( list of dictionaries )
        Returns:
            - {"indicator": bool, "message": msg}
        data: 
            - A list of columns
            pymilvus >= v2.3.x :
            - A pandas.DataFrame
            - A list of rows or just a row ( list of dictionaries )
            - Each row is a dictionary that represents an entity.
        """
        collection:Collection = self.get_collection(collection_name)
        collection.insert(data=data, **kwargs)
        collection.flush()

        return {"indicator": True, "message": f"Data inserted into {collection_name} successfully."}
    
    @MilvusCatchError.milvus_catch_error
    def search_data(self, collection_name, data, anns_field, param, limit=1, expression="", output_fields=[], format_data=True, **kwargs):
        """
        This operation conducts a vector similarity search with an optional scalar filtering expression.
        Args:
            - collection_name (str): The name of the collection.
            - data (list[list[float]]): The data to be searched.
                The data should be a list of vectors.
            - anns_field (str): The name of the field to be searched.
            - param (dict): The parameters for the search.
                - metric_type (str): The metric type for the search.
                - params (dict): The parameters for the search.
            - limit (int): The number of results to be returned. it should be in range [1, 16384]
            - expression (str): The expression to filter the results.
            - output_fields (list): The fields to be returned in the results.
            - format_data (bool): Whether to format the data.
            - kwargs (dict): The parameters for the search.
        Returns:
            - idicator (bool): Whether the operation was successful.
            - message (str): The message of the operation.
            - data (SearchResult) 
                format_data = True (list of dictionaries): The data will be formatted to a list of dictionaries.
                format_data = False (SearchResult): The data will be returned as is.
        Example:
            data = [[0.1]*128],
            anns_field = "embedding",
            param = {"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit = 10,
            expression = "id > 0",
            output_fields = ["field1", "field2"],
        """
        if not MilvusSearchLimit.check_search_limit(limit):
            return {"indicator": False, "message": f"Limit should be in range [{MilvusSearchLimit.MIN_SEARCH_LIMIT.value}, {MilvusSearchLimit.MAX_SEARCH_LIMIT.value}]"}
        
        collection:Collection = self.get_collection(collection_name)
        collection.load()
        
        results = collection.search(
            data=data,
            anns_field=anns_field,
            param=param,
            limit=limit,
            expr=expression,
            output_fields=output_fields,
            **kwargs
        )
        if format_data:
            all_hits_json = []
            for hits in results[0]:
                hits_list = dict(hits)
                all_hits_json.append(hits_list)
            
            return {"indicator": True ,"message": "success get data", "data": all_hits_json}
        else:
            return {"indicator": True ,"message": "success get data", "data": results}
    
    @MilvusCatchError.milvus_catch_error
    def search_iterator_data(self, collection_name, data, anns_field, param, batch_size=1000, expression="", output_fields=[], **kwargs):
        """
        This operation conducts a vector similarity search with an optional scalar filtering expression.
        Args:
            - collection_name (str): The name of the collection.
            - batch_size (int): The batch size for the search.
            - data (list[list[float]]): The data to be searched.
                The data should be a list of vectors.
            - anns_field (str): The name of the field to be searched.
            - param (dict): The parameters for the search.
                - metric_type (str): The metric type for the search.
                - params (dict): The parameters for the search.
            - limit (int): The number of results to be returned. it should be in range [1, 16384]
            - expression (str): The expression to filter the results.
            - output_fields (list): The fields to be returned in the results.
            - kwargs (dict): The parameters for the search.
        Returns:
            - indicator (bool): Whether the operation was successful.
            - message (str): The message of the operation.
            - data (SearchIterator): SearchIterator is an iterator for accessing results, but it cannot be used directly in a for loop.
                example:
                    all_data = []
                    while True:
                        res = iterator.next()
                        if not res:
                            iterator.close()
                            break
                        all_data.extend(list(res))
                    print(all_data)
        Example:
            data = [[0.1]*128],
            anns_field = "embedding",
            param = {"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit = 10,
            expression = None,
            output_fields = ["field1", "field2"],
        """
        collection:Collection = self.get_collection(collection_name)
        
        collection.load()
        results = collection.search_iterator(
            batch_size=batch_size,
            data=data,
            anns_field=anns_field,
            param=param,
            expr=expression,
            output_fields=output_fields,
            **kwargs
        )
        
        return {"indicator": True ,"message": "success get data", "data": results}

    @MilvusCatchError.milvus_catch_error
    def query_data(self, collection_name, expression, output_fields=None, format_data=True, **kwargs):
        """
        This operation conducts a scalar filtering with a specified boolean expression.
        Args:
            - collection_name (str): The name of the collection.
            - expression (str): The expression to filter the results.
            - output_fields (list): The fields to be returned in the results.
            - format_data (bool): Whether to format the data.
            - kwargs (dict): The parameters for the search.
        Returns:
            - indicator (bool): Whether the operation was successful.
            - message (str): The message of the operation.
            - data (list): 
                format_data = True (list of dictionaries) : The data will be formatted to a list of dictionaries.
                format_data = False (list of dictionaries): The data will be returned as is. 
                    If your output_fields include a vector field,
                    the vector field will be returned as a `pymilvus.client.types.ExtraList`.
                    It will be like this:
                        data: ["{'create_at': '2025-05-08 17:54:50', 
                        'embedding': [np.float32(0.6563757), np.float32(0.3761659), np.float32(0.1093178)], 
                        '_id': 457840961114819610}"]
        """
        collection:Collection = self.get_collection(collection_name)
        collection.load()
        
        results = collection.query(expr=expression, output_fields=output_fields, **kwargs)

        if format_data:
            formatted_data = []
            vector_fields = []
            for field in results[0]:
                data = results[0][field]
                if isinstance(data, list) and all(isinstance(x, np.float32) for x in data):
                    vector_fields.append(field)
            for hits in results:
                for field in vector_fields:
                    hits[field] = [float(i) for i in hits[field]]
                formatted_data.append(hits)
            return {"indicator": True ,"message": "success get formatted data", "data": formatted_data}
        else:
            return {"indicator": True ,"message": "success get data", "data": results}

    @MilvusCatchError.milvus_catch_error
    def query_iterator_data(self, collection_name, expression, batch_size, output_fields=None, **kwargs):
        """
        This operation conducts a scalar filtering with a specified boolean expression.
        Args:
            - collection_name (str): The name of the collection.
            - expression (str): The expression to filter the results.
            - batch_size (int): The batch size for the search.
            - output_fields (list): The fields to be returned in the results.
            - kwargs (dict): The parameters for the search.
        Returns:
            - {"indicator": bool, "message": msg, "data": QueryIterator}
            - QueryIterator is an iterator for accessing results, but it cannot be used directly in a for loop.
            Example:
                while True:
                    try:
                        data = QueryIterator.next()
                    except TypeError:
                        logging.error("**TypeError: results is None**")
                        break
                    if not data:
                        QueryIterator.close()
                        break
                    for i,res in enumerate(data):
                        print(f'data {i} : {res}')        
            
        """
        collection:Collection = self.get_collection(collection_name)
        collection.load()
        
        results = collection.query_iterator(batch_size=batch_size, expr=expression, output_fields=output_fields, **kwargs)
        
        return {"indicator": True, "message": "success get data", "data": results}

    @MilvusCatchError.milvus_catch_error
    def delete_data(self, collection_name, expression):
        """
        Args:
            - collection_name (str): The name of the collection.
            - expression (str): The expression to filter the results.
        Returns:
            - {"indicator": bool, "message":msg}
        """
        collection:Collection = self.get_collection(collection_name)
        collection.load()
        collection.delete(expr=expression)
        collection.flush()

        return {"indicator": True, "message": f"Data deleted from {collection_name} successfully."}

    @MilvusCatchError.milvus_catch_error
    def get_collection_describe(self, collection_name):
        """
        Args:
            - collection_name (str): The name of the collection.
        Returns:
            - {"indicator": bool, "message":msg}
        """
        collection:Collection = self.get_collection(collection_name)
        return {"indicator": True, "message": f"Collection {collection_name} describe successfully.", "data": collection.describe()}
    
    @MilvusCatchError.milvus_catch_error
    def get_collection_index(self, collection_name):
        """
        Args:
            - collection_name (str): The name of the collection.
        Returns:
            - {"indicator": bool, "message":msg}
        """
        collection:Collection = self.get_collection(collection_name)
        if not collection.has_index():
            return {"indicator": False, "message": f"Collection {collection_name} has no index."}
        return {"indicator": True, "message": f"Collection {collection_name} index successfully.", "data": collection.indexes}
    
    @MilvusCatchError.milvus_catch_error
    def get_database_list(self):
        """
        This function is used to get the database list.
        Returns:
            - {"indicator": bool, "message":msg, "data": []}
        """
        return {"indicator": True, "message": f"Database list in {self.alias} successfully.", "data": db.list_database(using=self.alias)}

    @MilvusCatchError.milvus_catch_error
    def get_connection_list(self):
        """
        This function is used to get the connection list.
        Returns:
            - {"indicator": bool, "message":msg, "data": []}
        """
        return {"indicator": True, "message": f"Connection list in {self.alias} successfully.", "data": connections.list_connections()}

    @MilvusCatchError.milvus_catch_error
    def get_collection_list(self):
        """
        This function is used to get the collection list.
        Returns:
            - {"indicator": bool, "message":msg, "data": []}
        """
        return {"indicator": True, "message": f"Collection list in {self.database} successfully.", "data": list_collections(using=self.alias)}
    
    @MilvusCatchError.milvus_catch_error
    def delete_database(self):
        """
        will delete all collections before deleting the database.
        Returns:
            - {"indicator": bool, "message":msg, "data": []}
        """
        self.__delete_all_collection()
        db.drop_database(self.database, using=self.alias)
        return {"indicator": True, "message": f"Database {self.database} deleted successfully."}
    
    def __delete_all_collection(self):
        collection_list = list_collections(using=self.alias)
        for collection_name in collection_list:
            collection:Collection = self.get_collection(collection_name)
            collection.drop()

    @MilvusCatchError.milvus_catch_error
    def delete_collection(self, collection_name):
        """
        Args:
            - collection_name (str) : The name of the collection.
        Returns:
            - {"indicator": bool, "message":msg}
        """
        collection:Collection = self.get_collection(collection_name)
        collection.drop()
        return {"indicator": True, "message": f"Collection {collection_name} deleted successfully."}

    @MilvusCatchError.milvus_catch_error
    def delete_index(self, collection_name):
        """
        Args:
            - collection_name (str) : The name of the collection.
        Returns:
            - {"indicator": bool, "message":msg}
        """
        collection:Collection = self.get_collection(collection_name)
        if collection.has_index():
            collection.drop_index()
        else:
            return {"indicator": False, "message": f"Collection {collection_name} has no index to drop."}
        return {"indicator": True, "message": f"Index on {collection_name} deleted successfully."}
        
    @MilvusCatchError.milvus_catch_error
    def create_index(self, collection_name, field_name, index_params):
        """
        Args:
            - collection_name (str) : The name of the collection.
            - field_name (str) : The name of the field to be indexed.
            - index_params (dict) : The parameters for the index.
        Returns:
            - {"indicator": bool, "message":msg}
        """
        collection:Collection = self.get_collection(collection_name)
        if not collection.has_index():
            collection.create_index(field_name, index_params)
        else:
            return {"indicator": False, "message": f"Collection {collection_name} already has an index on {field_name}."}
        return {"indicator": True, "message": f"Index on {field_name} created successfully."}
    
    @MilvusCatchError.milvus_catch_error
    def set_properties(self, collection_name, properties):
        """
        Args:
            - collection_name (str) : The name of the collection.
            - properties (dict) : A dictionary of properties to set for the collection.
                For example: {"collection.ttl.seconds": 3600}
        Returns:
            - {"indicator": bool, "message": msg}
        """
        collection:Collection = self.get_collection(collection_name)
        collection.set_properties(properties)
        return {"indicator": True, "message": "properties created successfully."}