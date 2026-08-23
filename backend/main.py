from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from rag import (
    analyze_video,
    ask_question
)



# =========================================================
# CREATE FASTAPI APP
# =========================================================

app = FastAPI(
    title="YouTube RAG API",
    description="RAG based YouTube question answering API",
    version="1.0.0"
)
@app.get("/")
def root():
    return {
        "message": "YouTube RAG API is running"
    }


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class VideoRequest(BaseModel):

    url: str


class QuestionRequest(BaseModel):

    video_id: str

    question: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "YouTube RAG API is running"
    }


# =========================================================
# ANALYZE VIDEO
# =========================================================

@app.post("/api/video/analyze")
def analyze_video_api(
    request: VideoRequest
):

    try:

        result = analyze_video(
            request.url
        )


        return {

            "video_id": result["video_id"],

            "chunks": result["chunks"],

            "title": "YouTube Video"

        }


    except Exception as e:

        print(
            "Analyze error:",
            str(e)
        )


        raise HTTPException(

            status_code=400,

            detail=str(e)
        )


# =========================================================
# ASK QUESTION
# =========================================================

@app.post("/api/video/ask")
def ask_question_api(
    request: QuestionRequest
):

    try:

        answer = ask_question(

            request.video_id,

            request.question
        )


        return {

            "answer": answer

        }


    except Exception as e:

        print(
            "Question error:",
            str(e)
        )


        raise HTTPException(

            status_code=400,

            detail=str(e)
        )