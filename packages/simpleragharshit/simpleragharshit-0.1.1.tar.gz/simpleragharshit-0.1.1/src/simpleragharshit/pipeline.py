import argparse
from simpleragharshit.loader import load_pdf
from simpleragharshit.embedding import get_embeddings
from simpleragharshit.indexing import create_faiss_index
from simpleragharshit.retriever import retrieve_top_k
from simpleragharshit.generator import generate_answer
from simpleragharshit.config import cohere_api_key


def run_rag(query, pdf_path, k=5):

    print("[+] Loading PDF...")
    raw_text = load_pdf(pdf_path)
    chunks = raw_text.split(". ")

    print("[+] Generating embeddings...")
    chunk_embeddings = get_embeddings(
        chunks, cohere_api_key, input_type="search_document")

    print("[+] Building FAISS index...")
    index = create_faiss_index(chunk_embeddings)

    print(f"Embedding query with input_type='search_query': {query}")

    print("[+] Embedding query...")
    query_embedding = get_embeddings(
        [query], cohere_api_key, input_type="search_query")[0]

    print("[+] Retrieving relevant chunks...")
    top_indices = retrieve_top_k(index, query_embedding, k=k)
    context = " ".join([chunks[i] for i in top_indices])

    print("[+] Generating answer...\n")
    full_prompt = f"{context}\n\nQuestion: {query}"
    answer = generate_answer(cohere_api_key, full_prompt)
    print("📘 Answer:\n", answer)


def cli():
    parser = argparse.ArgumentParser(
        description="Run simplerag-harshit query on a PDF file.")
    parser.add_argument("--query", type=str, required=True,
                        help="Your question")
    parser.add_argument("--pdf", type=str, required=True,
                        help="Path to the PDF file")
    parser.add_argument("--top_k", type=int, default=5,
                        help="Number of chunks to retrieve")

    args = parser.parse_args()
    run_rag(args.query, args.pdf, args.top_k)


if __name__ == "__main__":
    cli()
