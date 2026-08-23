from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
import os

load_dotenv()  # Load environment variables from .env file

videoId="PHpsdIHpLUE"  # Replace with your actual video ID

try:
    ytt_api = YouTubeTranscriptApi()

    transcript = ytt_api.fetch(videoId, languages=["en"])

    transcript_text = " ".join(
        snippet.text for snippet in transcript
    )

    #print(transcript_text)

except Exception as e:
    print(f"An error occurred: {e}")
    
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len
)

chunks = splitter.create_documents([transcript_text])

size=len(chunks)  # Print the number of chunks created
print(f"Number of chunks created: {size}")

#create embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

#vector store and store embeddings
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="rag_collection",
    persist_directory="./chroma_db"
)

#reteriver created
retriever = vector_store.as_retriever(search_type="similarity",search_kwargs={"k": 2})

result=retriever.invoke("summary of this video in 2 lines")
print(result)

prompt=PromptTemplate(
    template='You are a helpful assistant. Answer only from the provided transcript. If the answer is not present in the transcript, say "I am sorry, I cannot find the answer in the transcript." Provide the answer in 2 lines. \n\nTranscript: {text}\n\nQuestion: {topic}\n\nAnswer:',  
    input_variables=['topic', 'text']
)

llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    max_new_tokens=512,
    temperature=0.7
)
print("Token loaded:", os.getenv("HF_TOKEN") is not None)
model=ChatHuggingFace(llm=llm)

question="is the topic alien sightings discussed in this video?"
reteriver_result=retriever.invoke(question)

context_text=" ".join([doc.page_content for doc in reteriver_result])
final_result=prompt.invoke({'topic':question,'text':context_text})

answer=model.invoke(final_result)
print(answer.content)
