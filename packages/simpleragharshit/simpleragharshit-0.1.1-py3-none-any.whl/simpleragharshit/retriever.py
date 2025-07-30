import numpy as np


def retrieve_top_k(index, query_embedding, k=5):
    """
    Retrieve top-k most similar chunks using FAISS.

    Args:
        index (faiss.Index): The FAISS index.
        query_embedding (List[float]): The embedding of the query.
        k (int): Number of similar chunks to retrieve.

    Returns:
        List[int]: Indices of the top-k closest chunks in the original chunk list.
    """
    query_vector = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_vector, k)
    return indices[0]
