from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")  # Connect to MongoDB server

db = client["FinSight"]  # Access the 'finsight' database

companies_collection = db["companies"]  # Access the 'companies' collection

articles_collection = db["articles"]
articles_collection.create_index("url", unique=True)  # duplicate news nahi aayegi