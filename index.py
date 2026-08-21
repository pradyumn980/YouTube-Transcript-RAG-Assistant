from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate


videoId="LPZh9BOjkQs"  # Replace with your actual video ID

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

