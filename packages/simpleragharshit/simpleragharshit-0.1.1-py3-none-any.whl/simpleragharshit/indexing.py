import numpy as np
import os
import faiss


def create_faiss_index(embeddings):
    """
    Create a FAISS index from the given embeddings.

    Args:
        embeddings (List[List[float]]): List of dense vectors.

    Returns:
        faiss.IndexFlatL2: FAISS index with the embeddings.
    """
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index


def save_faiss_index(index, path):
    """
    Save a FAISS index to the specified file path.
    """
    faiss.write_index(index, path)


def load_faiss_index(path):
    """
    Load a FAISS index from file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No FAISS index found at {path}")
    return faiss.read_index(path)
