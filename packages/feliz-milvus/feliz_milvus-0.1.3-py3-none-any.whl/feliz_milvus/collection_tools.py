from .crud_tools import MilvusCatchError, CONNECTION_STATUS

from pymilvus import db, FieldSchema, CollectionSchema, utility, Collection
import logging


class MilvusField:
    """
    This is the class to define the postgres field.

    Args:
        dtype (str): The type of the field.
        is_primary (bool): Whether the field is a primary key.
        auto_id (bool): Whether the field is an auto-incrementing primary key.
        dim (int): The dimension of the vector field.
        description (str): The description of the field.
        index_params (dict): The parameters for the index.
        max_length (int): The maximum length of the field.
    """
    def __init__(self, *, dtype, is_primary=False, auto_id=False, dim=None, description=None, index_params=None, max_length=None):
        self.dtype = dtype
        self.is_primary = is_primary
        self.auto_id = auto_id
        self.dim = dim
        self.description = description
        self.index_params = index_params
        self.max_length = max_length


class MilvusMeta(type):
    """
    Metaclass to check the meta of the class.
    """
    META_REQUIRED = ["alias", "collection"]
    @staticmethod
    def lack_inspector(name, meta, required_list):
        lack_list = []
        for key in required_list:
            if key not in meta:
                lack_list.append(key)
        if len(lack_list) > 0:
            raise ValueError(f"( {name} ) Lack of meta: {', '.join(lack_list)}")
        
    def __new__(metacls, name, bases, classdict):
        new_class = super().__new__(metacls, name, bases, classdict)
        meta = {}
        if "meta" in classdict and isinstance(classdict["meta"], dict):
            meta.update(classdict["meta"])
            metacls.lack_inspector(name, meta, metacls.META_REQUIRED)
            
            collection = meta["collection"]
            alias = meta["alias"]

            if type(collection) == str:
                meta["collection"] = [collection]
            elif type(collection) == list:
                if len(collection) == 0:
                    raise ValueError(f"( {name} ) collection should not be empty if init_type is table")
            else:
                raise TypeError(f"( {name} ) collection should be string or list")

            if type(alias) == str:
                meta["alias"] = [alias]
            elif type(alias) == list:
                if len(alias) == 0:
                    raise ValueError(f"( {name} ) alias should not be empty if init_type is table")
            else:
                raise TypeError(f"( {name} ) alias should be string or list")
            new_class.meta = meta
        return new_class


class MilvusCollectionHandler(metaclass=MilvusMeta):
    """
    The class to define the Milvus collection schema and set the index.

    Required meta:
        - alias (str): The alias of the connection.
        - collection (str): The name of the collection.
    Args:
        - db_obj (MilvusHandler): The MilvusHandler object.
    """
    @classmethod
    def _build_field_schemas(cls):
        fields = []
        index_list = []
        ttl_seconds = 0
        for name, val in cls.__dict__.items():
            if isinstance(val, MilvusField):
                field_kwargs = {
                    "name" : name,
                    "dtype" : val.dtype,
                    "is_primary" : val.is_primary,
                    "auto_id" : val.auto_id,
                    "max_length" : val.max_length
                }
                index_kwargs = {
                    "name" : name,
                    "index_params" : val.index_params
                }
                if val.dim is not None:
                    field_kwargs["dim"] = val.dim
                if val.description is not None:
                    field_kwargs["description"] = val.description
                if val.index_params is not None:
                    index_list.append(index_kwargs)

                fields.append(FieldSchema(**field_kwargs))

            elif name == "ttl_seconds":
                ttl_seconds = val
                
        return fields, index_list, ttl_seconds

    @classmethod
    @MilvusCatchError.milvus_catch_error
    def create_collection(cls, db_obj):
        if cls.meta["alias"][0] != db_obj.alias:
            raise ValueError(f"Alias mismatch: collection '{cls.meta['collection']}'.meta['alias']({cls.meta['alias'][0]}) != database.ini ({db_obj.alias})")
        
        if db_obj.connection_status == CONNECTION_STATUS.DISCONNECTED:
            db_obj.connect()
            logging.info(f"[MilvusHandler] Connect to {db_obj.database} successfully.")

        if db_obj.database not in db.list_database(db_obj.alias):
            db.create_database(db_obj.database, using=db_obj.alias)
        db.using_database(db_obj.database, using=db_obj.alias)
        
        if not utility.has_collection(cls.meta["collection"][0], using=db_obj.alias):
            fields, index_list, ttl_seconds = cls._build_field_schemas()
            schema = CollectionSchema(fields)
            collection_name = cls.meta["collection"][0]
            collection:Collection = db_obj.get_collection(collection_name, schema=schema)
            for index in index_list:
                collection.create_index(index['name'],index['index_params'])
            if ttl_seconds != 0:
                collection.set_properties(properties={"collection.ttl.seconds":ttl_seconds})