import cohere


def generate_answer(api_key, prompt, model="command-r-plus", temperature=0.3):
    """
    Generate a response from Cohere's chat model given a prompt.

    Args:
        api_key (str): Cohere API key.
        prompt (str): The context + question input.
        model (str): Model name to use (default is "command-r-plus").
        temperature (float): Sampling temperature for creativity.

    Returns:
        str: The model's response text.
    """
    co = cohere.Client(api_key)

    response = co.chat(
        message=prompt,
        model=model,
        temperature=temperature,
        chat_history=[],
    )

    return response.text
