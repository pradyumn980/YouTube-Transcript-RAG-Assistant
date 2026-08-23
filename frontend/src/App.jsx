import { useState } from "react";
import {
  Send,
  Sparkles,
  Loader2,
  MessageCircle,
  FileText,
  Database,
  Play,
} from "lucide-react";

function App() {
  const [url, setUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [video, setVideo] = useState(null);
  const [answer, setAnswer] = useState("");
  const [loadingVideo, setLoadingVideo] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [error, setError] = useState("");

  const analyzeVideo = async () => {
    if (!url.trim()) return;

    setLoadingVideo(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch("http://localhost:8000/api/video/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("Unable to analyze video");
      }

      const data = await response.json();

console.log("BACKEND RESPONSE:", data);

setVideo(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingVideo(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim() || !video) return;

    setLoadingAnswer(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/video/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_id: video.video_id,
          question,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to generate answer");
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAnswer(false);
    }
  };

  const videoId = video?.video_id;

  return (
    <div className="min-h-screen bg-[#09090b] text-white">
      {/* Navbar */}
      <nav className="border-b border-zinc-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-red-600 p-2">
              <Play  size={22} />
            </div>

            <div>
              <h1 className="text-lg font-semibold">YouTube RAG</h1>
              <p className="text-xs text-zinc-500">
                Ask anything about a video
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-zinc-800 px-4 py-2 text-sm text-zinc-400">
            <Sparkles size={15} />
            AI Powered
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-6 py-12">
        {/* Hero */}
        <section className="mx-auto max-w-3xl text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-400">
            <Sparkles size={15} />
            Retrieval Augmented Generation
          </div>

          <h2 className="text-4xl font-bold tracking-tight md:text-5xl">
            Chat with any
            <span className="text-red-500"> YouTube video</span>
          </h2>

          <p className="mt-5 text-zinc-400">
            Paste a YouTube URL, process its transcript, and ask questions
            using AI-powered semantic search.
          </p>
        </section>

        {/* URL Input */}
        <section className="mx-auto mt-10 max-w-3xl">
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-2">
            <div className="flex flex-col gap-2 sm:flex-row">
              <div className="flex flex-1 items-center gap-3 px-4">
                <Play  className="text-red-500" size={20} />

                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") analyzeVideo();
                  }}
                  placeholder="Paste YouTube video URL..."
                  className="w-full bg-transparent py-3 outline-none placeholder:text-zinc-600"
                />
              </div>

              <button
                onClick={analyzeVideo}
                disabled={loadingVideo}
                className="flex items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 font-medium transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loadingVideo ? (
                  <>
                    <Loader2 className="animate-spin" size={18} />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Analyze Video
                  </>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/40 p-4 text-sm text-red-400">
              {error}
            </div>
          )}
        </section>

        {/* Video Information */}
        {video && (
          <section className="mt-12 grid gap-6 md:grid-cols-3">
            {/* Video */}
            <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900 md:col-span-2">
              <div className="aspect-video bg-black">
                <iframe
                  className="h-full w-full"
                  src={`https://www.youtube.com/embed/${videoId}`}
                  title="YouTube video"
                  allowFullScreen
                />
              </div>

              <div className="p-5">
                <h3 className="font-semibold">
                  {video.title || "YouTube Video"}
                </h3>

                <p className="mt-2 text-sm text-zinc-500">
                  Video ID: {videoId}
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
              <h3 className="font-semibold">Video Information</h3>

              <div className="mt-6 space-y-4">
                <InfoCard
                  icon={<Play size={18} />}
                  title="Transcript"
                  value="Loaded"
                />

                <InfoCard
                  icon={<FileText size={18} />}
                  title="Chunks"
                  value={video.chunks || "—"}
                />

                <InfoCard
                  icon={<Database size={18} />}
                  title="Vector Store"
                  value="Chroma"
                />
              </div>
            </div>
          </section>
        )}

        {/* Question */}
        {video && (
          <section className="mx-auto mt-10 max-w-4xl">
            <div className="mb-4 flex items-center gap-2">
              <MessageCircle className="text-red-500" size={20} />
              <h3 className="text-xl font-semibold">
                Ask about this video
              </h3>
            </div>

            <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-2">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") askQuestion();
                  }}
                  placeholder="e.g. Is attention mechanism discussed?"
                  className="flex-1 bg-transparent px-4 py-3 outline-none placeholder:text-zinc-600"
                />

                <button
                  onClick={askQuestion}
                  disabled={loadingAnswer}
                  className="rounded-xl bg-white p-3 text-black transition hover:bg-zinc-200 disabled:opacity-50"
                >
                  {loadingAnswer ? (
                    <Loader2 className="animate-spin" size={19} />
                  ) : (
                    <Send size={19} />
                  )}
                </button>
              </div>
            </div>

            {/* Answer */}
            {answer && (
              <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900 p-6">
                <div className="mb-4 flex items-center gap-2">
                  <div className="rounded-lg bg-red-600/10 p-2 text-red-500">
                    <Sparkles size={18} />
                  </div>

                  <span className="font-semibold">AI Answer</span>
                </div>

                <p className="leading-7 text-zinc-300">{answer}</p>
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="border-t border-zinc-800 py-6 text-center text-sm text-zinc-600">
        Built with React • LangChain • Chroma • HuggingFace
      </footer>
    </div>
  );
}

function InfoCard({ icon, title, value }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-zinc-950 p-4">
      <div className="flex items-center gap-3">
        <div className="text-red-500">{icon}</div>
        <span className="text-sm text-zinc-400">{title}</span>
      </div>

      <span className="text-sm font-medium">{value}</span>
    </div>
  );
}

export default App;