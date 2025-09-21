#!/usr/bin/env python3
import requests
import json
from requests.auth import HTTPDigestAuth

# Atlas API credentials
PUBLIC_KEY = "rbqfhhol"
PRIVATE_KEY = "d380c0c0-f521-4193-b472-8b233cde15a4"
DATABASE_NAME = "support_bot"
COLLECTION_NAME = "knowledge_base"

def create_vector_index():
    auth = HTTPDigestAuth(PUBLIC_KEY, PRIVATE_KEY)
    
    # Step 1: Get Project ID
    print("Getting project ID...")
    response = requests.get("https://cloud.mongodb.com/api/atlas/v1.0/groups", auth=auth)
    if response.status_code != 200:
        print(f"Error getting projects: {response.status_code}")
        return
    
    project_id = response.json()['results'][0]['id']
    print(f"Project ID: {project_id}")
    
    # Step 2: Get Cluster Name
    print("Getting cluster name...")
    response = requests.get(f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/clusters", auth=auth)
    if response.status_code != 200:
        print(f"Error getting clusters: {response.status_code}")
        return
        
    cluster_name = response.json()['results'][0]['name']
    print(f"Cluster Name: {cluster_name}")
    
    # Step 3: Create Vector Search Index
    print("Creating vector search index...")
    
    index_definition = {
        "database": DATABASE_NAME,
        "collectionName": COLLECTION_NAME,
        "name": "vector_index",
        "type": "vectorSearch",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embeddings",
                    "numDimensions": 1024,
                    "similarity": "cosine"
                },
                {"type": "filter", "path": "type"},
                {"type": "filter", "path": "product"},
                {"type": "filter", "path": "priority"},
                {"type": "filter", "path": "status"},
                {"type": "filter", "path": "category"}
            ]
        }
    }
    
    url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/clusters/{cluster_name}/search/indexes"
    
    response = requests.post(url, json=index_definition, auth=auth, 
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 201:
        result = response.json()
        print("✅ Vector search index created successfully!")
        print(f"Index ID: {result.get('indexID')}")
        print("The index is being built and will be ready shortly.")
    elif response.status_code == 409:
        print("⚠️ Index already exists")
    else:
        print(f"❌ Error creating index: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    create_vector_index()
