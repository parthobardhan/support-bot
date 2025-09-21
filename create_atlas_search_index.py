#!/usr/bin/env python3
import requests
import json
import sys
import os
import time
from requests.auth import HTTPDigestAuth

# Add backend directory to path to import Config
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from config import Config

def create_atlas_search_index():
    """Create Atlas Search index with provided credentials"""
    
    public_key = "rbqfhhol"
    private_key = "d380c0c0-f521-4193-b472-8b233cde15a4"
    
    auth = HTTPDigestAuth(public_key, private_key)
    
    # Step 1: Get Project ID
    print("Getting project ID...")
    response = requests.get("https://cloud.mongodb.com/api/atlas/v1.0/groups", auth=auth)
    if response.status_code != 200:
        print(f"Error getting projects: {response.status_code}")
        print(response.text)
        return False
    
    projects = response.json()['results']
    if not projects:
        print("No projects found")
        return False
        
    project_id = projects[0]['id']
    print(f"Project ID: {project_id}")
    
    # Step 2: Get Cluster Name
    print("Getting cluster name...")
    response = requests.get(f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/clusters", auth=auth)
    if response.status_code != 200:
        print(f"Error getting clusters: {response.status_code}")
        print(response.text)
        return False
        
    clusters = response.json()['results']
    if not clusters:
        print("No clusters found")
        return False
        
    cluster_name = clusters[0]['name']
    print(f"Cluster Name: {cluster_name}")
    
    print("Creating Atlas Search index...")
    
    index_definition = {
        "database": Config.DATABASE_NAME,
        "collectionName": Config.COLLECTION_NAME,
        "name": Config.SEARCH_INDEX_NAME,
        "mappings": {
            "dynamic": False,
            "fields": {
                "title": {
                    "type": "string",
                    "analyzer": "lucene.standard"
                },
                "content": {
                    "type": "string", 
                    "analyzer": "lucene.standard"
                },
                "summary": {
                    "type": "string",
                    "analyzer": "lucene.standard"
                },
                "product": {
                    "type": "string",
                    "analyzer": "lucene.keyword"
                },
                "category": {
                    "type": "string", 
                    "analyzer": "lucene.keyword"
                },
                "tags": {
                    "type": "string",
                    "analyzer": "lucene.standard"
                }
            }
        }
    }
    
    url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/clusters/{cluster_name}/fts/indexes"
    
    response = requests.post(url, json=index_definition, auth=auth, 
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Atlas Search index created successfully!")
        print(f"Index ID: {result.get('indexID')}")
        print("The index is being built and will be ready shortly.")
        
        index_id = result.get('indexID')
        return wait_for_index_ready(project_id, cluster_name, index_id, auth)
        
    elif response.status_code == 409:
        print("⚠️ Index already exists")
        return validate_search_index_exists(project_id, cluster_name, auth)
    else:
        print(f"❌ Error creating index: {response.status_code}")
        print(response.text)
        return False

def wait_for_index_ready(project_id, cluster_name, index_id, auth, max_wait_time=300):
    """Wait for Atlas Search index to be ready"""
    print("Waiting for index to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        response = requests.get(
            f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/clusters/{cluster_name}/fts/indexes/{index_id}",
            auth=auth
        )
        
        if response.status_code == 200:
            index_info = response.json()
            status = index_info.get('status')
            print(f"Index status: {status}")
            
            if status == 'READY':
                print("✅ Atlas Search index is ready!")
                return True
            elif status == 'FAILED':
                print("❌ Atlas Search index creation failed!")
                return False
                
        time.sleep(10)  # Wait 10 seconds before checking again
    
    print("⚠️ Timeout waiting for index to be ready")
    return False

def validate_search_index_exists(project_id, cluster_name, auth):
    """Validate that the search index exists"""
    print("Validating search index exists...")
    
    response = requests.get(
        f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/clusters/{cluster_name}/fts/indexes",
        auth=auth
    )
    
    if response.status_code == 200:
        indexes = response.json()
        search_indexes = [idx for idx in indexes if idx.get('name') == Config.SEARCH_INDEX_NAME]
        
        if search_indexes:
            index = search_indexes[0]
            print(f"✅ Search index '{Config.SEARCH_INDEX_NAME}' exists with status: {index.get('status')}")
            return index.get('status') == 'READY'
        else:
            print(f"❌ Search index '{Config.SEARCH_INDEX_NAME}' not found")
            return False
    else:
        print(f"❌ Error validating index: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    success = create_atlas_search_index()
    if success:
        print("🎉 Atlas Search index setup completed successfully!")
        sys.exit(0)
    else:
        print("💥 Atlas Search index setup failed!")
        sys.exit(1)
