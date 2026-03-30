# Knowledge Directory

This directory contains the knowledge base files used by the RAG system.

The RAG pipeline's actual knowledge base consists of **46 AI/ML textbooks** 
stored in the `data/` directory (SQLite chunks.db + ChromaDB vector store),
which is served by the FastAPI backend on the Windows PC.

The `ollama_publisher` ROS 2 node queries this backend via HTTP rather than
loading local text files directly, enabling the robot to leverage the full
RAG pipeline (BM25 + vector retrieval + Ollama generation).

## Architecture

```
[Loaner Laptop - Ubuntu/ROS2]          [Windows PC]
                                         
  recording_publisher                    FastAPI Backend (:8000)
       │ (recording)                       ├── RAG Engine
       ▼                                   │   ├── SQLite (chunks.db)
  words_publisher (Whisper)                │   ├── ChromaDB (vectors)
       │ (words)                           │   └── Ollama (qwen2.5:0.5b)
       ▼                                   │
  ollama_publisher ──── HTTP POST ────────►/api/search
       │ (ollama_reply)                    
       ▼                                   
  speak_client ──► speak service (gTTS)
```

## Usage

```bash
# On the Windows PC, start the FastAPI backend:
python -m uvicorn backend.api.server:app --host 0.0.0.0 --port 8000

# On the loaner laptop, run the ROS 2 nodes:
ros2 run aisd_hearing ollama_publisher \
  --ros-args \
  -p api_url:=http://<WINDOWS_IP>:8000/api/search \
  -p model:=qwen2.5:0.5b \
  -p top_k:=3
```
