import os
import lancedb
import pyarrow as pa
from typing import List, Optional, Dict, Any

DB_URI = "/home/lord-mahonheim/bifrost/tesla/memory/lancedb_buffer"
TABLE_NAME = "rejected_patches"
VECTOR_DIM = 1536

# Define the schema for the Rejected-Edit Buffer
schema = pa.schema([
    pa.field("patch_hash", pa.string()),
    pa.field("patch_content", pa.string()),
    pa.field("fitness_score", pa.float32()),
    pa.field("rejection_reason", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), VECTOR_DIM))
])

def init_db(db_uri: str = DB_URI) -> lancedb.DBConnection:
    """
    Initializes the LanceDB instance for the Rejected-Edit Buffer.
    Creates the table if it does not exist.
    """
    # Ensure the parent directories exist
    os.makedirs(os.path.dirname(db_uri), exist_ok=True)
    
    db = lancedb.connect(db_uri)
    
    # Create the table if it doesn't already exist
    if TABLE_NAME not in db.table_names():
        db.create_table(TABLE_NAME, schema=schema)
        
    return db

def insert_rejected_patch(
    db: lancedb.DBConnection, 
    patch_hash: str, 
    patch_content: str, 
    fitness_score: float, 
    rejection_reason: str, 
    vector: Optional[List[float]] = None
) -> None:
    """
    Inserts a rejected patch into the database.
    If no vector is provided, a dummy vector of zeroes will be used.
    """
    if vector is None:
        vector = [0.0] * VECTOR_DIM
    elif len(vector) != VECTOR_DIM:
        raise ValueError(f"Vector must have dimension {VECTOR_DIM}, got {len(vector)}")
        
    table = db.open_table(TABLE_NAME)
    
    data = [{
        "patch_hash": patch_hash,
        "patch_content": patch_content,
        "fitness_score": fitness_score,
        "rejection_reason": rejection_reason,
        "vector": vector
    }]
    
    table.add(data)

def search_similar_patch(
    db: lancedb.DBConnection, 
    vector: List[float], 
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Searches for similar rejected patches based on the given embedding vector.
    """
    if len(vector) != VECTOR_DIM:
        raise ValueError(f"Vector must have dimension {VECTOR_DIM}, got {len(vector)}")
        
    table = db.open_table(TABLE_NAME)
    results = table.search(vector).limit(limit).to_list()
    return results

if __name__ == "__main__":
    db = init_db()
    print(f"LanceDB successfully initialized at {DB_URI}")
    print(f"Table '{TABLE_NAME}' is ready for operations.")
