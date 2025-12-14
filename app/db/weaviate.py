import weaviate
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

class WeaviateClient:
    def __init__(self):
        self.client = weaviate.connect_to_custom(
            http_host="weaviate",
            http_port=8080,
            http_secure=False,
            grpc_host="weaviate", 
            grpc_port=50051,
            grpc_secure=False
        )

    def init_schema(self):
        # Weaviate v4 client style
        try:
            if not self.client.collections.exists("Chunk"):
                logger.info("creating_weaviate_schema")
                self.client.collections.create(
                    name="Chunk",
                    properties=[
                        weaviate.classes.config.Property(name="text", data_type=weaviate.classes.config.DataType.TEXT),
                        weaviate.classes.config.Property(name="document_id", data_type=weaviate.classes.config.DataType.UUID),
                        weaviate.classes.config.Property(name="chunk_index", data_type=weaviate.classes.config.DataType.INT),
                    ],
                    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none()  # We push vectors manually
                )
                logger.info("weaviate_schema_created")
            else:
                logger.info("weaviate_schema_exists")
        except Exception as e:
            logger.error("weaviate_schema_init_error", error=str(e))

    def insert_chunk(self, chunk_text: str, vector: list[float], document_id: str, chunk_index: int):
        try:
            chunks_collection = self.client.collections.get("Chunk")
            chunks_collection.data.insert(
                properties={
                    "text": chunk_text,
                    "document_id": document_id,
                    "chunk_index": chunk_index
                },
                vector=vector
            )
        except Exception as e:
            logger.error("weaviate_insert_error", error=str(e))
            raise e

    def search(self, vector: list[float], limit: int = 5):
        try:
            chunks_collection = self.client.collections.get("Chunk")
            # Using simple near_vector search
            response = chunks_collection.query.near_vector(
                near_vector=vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            return response.objects
        except Exception as e:
            logger.error("weaviate_search_error", error=str(e))
            return []
            
    def close(self):
        self.client.close()

# We need a predictable client instance or way to create it.
# Since weaviate connection might fail if container isn't up, we'll instantiate lazily or in calling code.
def get_weaviate_client():
    return WeaviateClient()
