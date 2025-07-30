import cohere


def get_embeddings(texts, api_key, model="embed-english-v3.0", input_type="search_document"):
    """
    Generate embeddings using Cohere's API.

    Args:
        texts (List[str]): The text chunks or queries.
        api_key (str): Your Cohere API key.
        model (str): The embedding model to use.
        input_type (str): Must be either "search_document" or "search_query".

    Returns:
        List[List[float]]: Embedding vectors.
    """
    co = cohere.Client(api_key)
    print("🧪 Embedding Params:")
    print(f"  Model: {model}")
    print(f"  Input Type: {input_type}")
    print(f"  Number of Inputs: {len(texts)}")
    print(f"  Sample Text: {texts[0][:100]}")
    response = co.embed(
        texts=texts,
        model=model,
        input_type=input_type,
    )
    return response.embeddings
