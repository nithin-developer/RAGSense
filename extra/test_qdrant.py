from qdrant_client import QdrantClient

# Test connection
client = QdrantClient(
    url="your_qdrant_url_here",
    api_key="your_qdrant_api_key_here"
)

# List collections
collections = client.get_collections()
print("Connected successfully!")
print(f"Collections: {collections}")