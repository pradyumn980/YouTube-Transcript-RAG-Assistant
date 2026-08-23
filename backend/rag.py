from dotenv import load_dotenv

load_dotenv()

import os
import re

from youtube_transcript_api import YouTubeTranscriptApi

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

from langchain_chroma import Chroma

from langchain_huggingface import (
    HuggingFaceEmbeddings,
    ChatHuggingFace,
    HuggingFaceEndpoint,
)

# =========================================================
# ENVIRONMENT
# =========================================================

HF_TOKEN = os.getenv("HF_TOKEN")

print("Token loaded:", HF_TOKEN is not None)

if not HF_TOKEN:
    raise ValueError(
        "HUGGINGFACEHUB_API_TOKEN not found in .env"
    )


# =========================================================
# EMBEDDING MODEL
# =========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# LLM
# =========================================================

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=512,
    temperature=0.7,
)

model = ChatHuggingFace(
    llm=llm
)


# =========================================================
# PROMPT
# =========================================================

prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Answer only from the provided transcript.

If the answer is not present in the transcript, say:

"I am sorry, I cannot find the answer in the transcript."

Provide the answer in 2 lines.

Transcript:
{text}

Question:
{topic}

Answer:
""",

    input_variables=[
        "topic",
        "text"
    ]
)


# =========================================================
# EXTRACT YOUTUBE VIDEO ID
# =========================================================

def extract_video_id(url):

    patterns = [

        r"(?:v=)([a-zA-Z0-9_-]{11})",

        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",

        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",

        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            url
        )

        if match:
            return match.group(1)

    return None


# =========================================================
# ANALYZE VIDEO
# =========================================================

def analyze_video(url):

    # -----------------------------------------
    # Extract video ID
    # -----------------------------------------

    video_id = extract_video_id(url)

    if not video_id:

        raise ValueError(
            "Invalid YouTube URL"
        )


    print(
        f"Processing video: {video_id}"
    )


    # -----------------------------------------
    # Get transcript
    # -----------------------------------------

    ytt_api = YouTubeTranscriptApi()

    transcript = ytt_api.fetch(
        video_id,
        languages=["en","hi"]
    )


    transcript_text = " ".join(
        snippet.text
        for snippet in transcript
    )


    if not transcript_text:

        raise ValueError(
            "Transcript not available"
        )


    # -----------------------------------------
    # Split transcript
    # -----------------------------------------

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,

        chunk_overlap=100,

        length_function=len
    )


    chunks = splitter.create_documents(
        [transcript_text]
    )


    print(
        f"Number of chunks created: {len(chunks)}"
    )


    # -----------------------------------------
    # Create collection name
    # -----------------------------------------

    collection_name = (
        f"rag_{video_id}"
    )


    # -----------------------------------------
    # Create Chroma vector store
    # -----------------------------------------

    vector_store = Chroma.from_documents(

        documents=chunks,

        embedding=embeddings,

        collection_name=collection_name,

        persist_directory="./chroma_db"
    )


    print(
        f"Vector store created: {collection_name}"
    )


    return {

        "video_id": video_id,

        "chunks": len(chunks),

        "collection_name": collection_name
    }


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(
    video_id,
    question
):

    # -----------------------------------------
    # Collection name
    # -----------------------------------------

    collection_name = (
        f"rag_{video_id}"
    )


    print(
        f"Loading collection: {collection_name}"
    )


    # -----------------------------------------
    # Load existing Chroma vector store
    # -----------------------------------------

    vector_store = Chroma(

        collection_name=collection_name,

        embedding_function=embeddings,

        persist_directory="./chroma_db"
    )


    # -----------------------------------------
    # Create retriever
    # -----------------------------------------

    retriever = vector_store.as_retriever(

        search_type="similarity",

        search_kwargs={
            "k": 2
        }
    )


    # -----------------------------------------
    # Retrieve relevant documents
    # -----------------------------------------

    retrieved_documents = retriever.invoke(
        question
    )


    print(
        f"Retrieved documents: {len(retrieved_documents)}"
    )


    # -----------------------------------------
    # Create context
    # -----------------------------------------

    context_text = " ".join(

        doc.page_content

        for doc in retrieved_documents
    )


    # -----------------------------------------
    # Create prompt
    # -----------------------------------------

    final_result = prompt.invoke({

        "topic": question,

        "text": context_text
    })


    # -----------------------------------------
    # Generate answer
    # -----------------------------------------

    answer = model.invoke(
        final_result
    )


    return answer.content