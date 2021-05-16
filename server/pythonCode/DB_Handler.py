from pymongo import MongoClient
import ssl

url = "mongodb+srv://admin:1234@stockpredict.n45hq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
class DBHandler:
    def __init__(self):
        self.client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)

    def insert_item(self, data, db_name=None, collection_name=None):
        return self.client[db_name][collection_name].insert_one(data).inserted_id

    def find_item(self, condition=None, db_name=None, collection_name=None):
        return self.client[db_name][collection_name].find_one(condition)

    def update_item(self, condition=None, update_value=None, db_name=None, collection_name=None):
        return self.client[db_name][collection_name].update_one(filter=condition, update=update_value, upsert=True)

    def delete_item(self, condition=None, db_name=None, collection_name=None):
        return self.client[db_name][collection_name].delete_many(condition)
