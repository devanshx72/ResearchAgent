# Agentic Research & Article Generation System

A multi-agent pipeline built with **LangGraph** and powered by **Mistral AI** that transforms a single user query into a fully researched, human-reviewed, publication-ready article.

## Features

- **Autonomous Research**: Breaks topics into sub-questions, searches the web, grades results
- **Self-Correction**: Automatically rewrites poor queries and improves article quality
- **Multi-Agent Pipeline**: 9 specialized agents working in orchestrated sequence
- **Human-in-the-Loop (HITL)**: Pause for human review before publishing
- **Quality Assurance**: Scores articles on coverage, accuracy, structure, and tone
- **Multiple Export Formats**: Markdown, DOCX, and Notion (will be added)
- **REST API + WebSocket**: Full async API with real-time progress streaming

## Architecture

```
User Query → Query Analyzer → Web Search → Result Grader
                                              ↓
                                    Query Rewriter (if needed)
                                              ↓
              Research Synthesizer → Article Writer
                                              ↓
                    Quality Checker → HITL Checkpoint
                                              ↓
                      Publisher → Final Article (.md/.docx)
```

## Prerequisites

- Python 3.11+
- Mistral AI API key
- Tavily Search API key

---

## Quick Start

### 1. Clone and Setup

```bash
cd /path/to/Agents
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.template .env
```

Edit `.env` and add your keys:

```
MISTRAL_API_KEY=your_mistral_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the Application

**Option A: FastAPI Server (Recommended)**

```bash
# Development
uvicorn app:app --reload --port 8000

# Production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Interactive docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Option B: CLI Mode**

```bash
python main.py \
  --query "Impact of AI on healthcare in 2025" \
  --export-format markdown \
  --tone professional \
  --word-count 1500
```

### 4. Handle HITL Checkpoint

When the pipeline pauses for human review, choose one of:

```bash
# Approve and publish
python resume_hitl.py --thread-id default --decision approve

# Request edits
python resume_hitl.py --thread-id default --decision edit \
  --feedback "Add more statistics about AI adoption rates"

# Reject and restart
python resume_hitl.py --thread-id default --decision reject \
  --feedback "Focus more on challenges than benefits"
```

---

## Project Structure

```
.
├── app.py                      # FastAPI application
├── main.py                     # CLI entry point
├── resume_hitl.py              # CLI HITL resume script
├── requirements.txt
├── .env                        # API keys (create from .env.template)
├── api/
│   ├── endpoints.py            # REST API endpoints
│   ├── websocket.py            # WebSocket endpoint
│   ├── task_manager.py         # Task state manager
│   └── research_executor.py    # Graph executor
├── models/
│   └── schemas.py              # Pydantic models
├── graph/
│   ├── state.py                # ResearchState definition
│   ├── graph_builder.py        # LangGraph orchestration
│   └── nodes/                  # Agent implementations
│       ├── query_analyzer.py
│       ├── web_search.py
│       ├── result_grader.py
│       ├── query_rewriter.py
│       ├── synthesizer.py
│       ├── writer.py
│       ├── quality_checker.py
│       ├── hitl.py
│       └── publisher.py
├── tools/
│   └── tavily_search.py        # Tavily API wrapper
├── prompts/
│   └── templates.py            # LLM prompt templates
└── outputs/                    # Generated articles
```

---

## Configuration Options

| Argument | Default | Options | Description |
|---|---|---|---|
| `--query` | Required | Any string | Research topic or question |
| `--export-format` | `markdown` | `markdown`, `docx`, `notion` | Output format |
| `--tone` | `professional` | `professional`, `casual`, `technical` | Article tone |
| `--word-count` | `1000` | `500–2000` | Target word count |
| `--thread-id` | `default` | Any string | Session ID for state persistence |

---

## Agents

| Agent | Role | Model |
|---|---|---|
| **Query Analyzer** | Breaks query into 3–5 sub-questions | mistral-large-latest |
| **Web Search** | Searches Tavily API for each sub-question | N/A (API) |
| **Result Grader** | Scores results 1–5 on relevance | mistral-large-latest |
| **Query Rewriter** | Reformulates poor queries (max 3 iterations) | mistral-large-latest |
| **Synthesizer** | Aggregates results into structured notes | mistral-large-latest |
| **Article Writer** | Generates full article from notes | mistral-large-latest |
| **Quality Checker** | Scores article 0–100 on 4 dimensions | mistral-large-latest |
| **HITL Checkpoint** | Pauses for human review | N/A (interrupt) |
| **Publisher** | Exports to `.md` / `.docx` / Notion | N/A (I/O) |

## Quality Metrics

Articles are scored on four dimensions (25 pts each, 100 total):

| Dimension | Description |
|---|---|
| **Coverage** | Comprehensiveness of research notes |
| **Factual Consistency** | Accuracy and proper citations |
| **Structure** | Organization and flow |
| **Tone** | Appropriateness and consistency |

**Passing threshold**: 70 / 100

---

## API Reference

Base URL: `http://localhost:8000`

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/research` | Create a new research task |
| `GET` | `/api/research/{task_id}` | Get task status & progress |
| `POST` | `/api/research/{task_id}/resume` | Resume from HITL checkpoint |
| `GET` | `/api/research/{task_id}/result` | Get final article & metadata |
| `DELETE` | `/api/research/{task_id}` | Delete a task |
| `GET` | `/health` | Health check |
| `WS` | `/ws/research/{task_id}` | Real-time WebSocket updates |

---

### POST `/api/research` — Create Task

**Request:**
```json
{
  "query": "Impact of AI on healthcare in 2025",
  "export_format": "markdown",
  "tone": "professional",
  "word_count": 1500
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Research task created successfully."
}
```

---

### GET `/api/research/{task_id}` — Task Status

**Response (processing):**
```json
{
  "task_id": "550e8400-...",
  "status": "processing",
  "current_node": "web_search",
  "progress": {
    "sub_questions": ["Q1", "Q2", "Q3"],
    "search_results_count": 15,
    "graded_results_count": 12,
    "iteration_count": 0,
    "write_iteration_count": 0
  },
  "article_draft": null,
  "quality_score": null,
  "sources": [],
  "error": null
}
```

**Response (at HITL checkpoint):**
```json
{
  "task_id": "550e8400-...",
  "status": "hitl_review",
  "current_node": "hitl",
  "article_draft": "# Article Title\n\nContent...",
  "quality_score": 85.0,
  "sources": ["https://example.com/1"]
}
```

---

### POST `/api/research/{task_id}/resume` — Resume from HITL

**Decision options:** `approve` · `edit` · `reject`

```json
{
  "decision": "edit",
  "feedback": "Add more statistics about hospital adoption rates"
}
```

**Response:**
```json
{
  "task_id": "550e8400-...",
  "status": "processing",
  "message": "Task resumed with decision: edit"
}
```

---

### GET `/api/research/{task_id}/result` — Final Result

```json
{
  "task_id": "550e8400-...",
  "status": "completed",
  "final_article": "# Article Title\n\nFull content...",
  "export_path": "outputs/Impact_of_AI_on_healthcare_20260217_140530.md",
  "sources": ["https://example.com/source1"],
  "quality_score": 92.0
}
```

---

### WS `/ws/research/{task_id}` — Real-Time Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/research/<task_id>');

ws.onmessage = (event) => {
  const { event_type, data } = JSON.parse(event.data);
  console.log(event_type, data);
};

// Keep-alive
setInterval(() => ws.send('ping'), 30000);
```

**Event types:** `connected` · `node_complete` · `status_update` · `hitl_checkpoint` · `error`

**HITL checkpoint event:**
```json
{
  "task_id": "550e8400-...",
  "event_type": "hitl_checkpoint",
  "data": {
    "status": "hitl_review",
    "message": "Human review required",
    "article_draft": "# Article...",
    "quality_score": 85.0,
    "sources": ["https://..."]
  }
}
```

---

### HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad Request (e.g., task not at HITL checkpoint) |
| `404` | Task Not Found |
| `500` | Internal Server Error |

---

## Client Examples

### Python (polling)

```python
import requests, time

BASE_URL = "http://localhost:8000"

task = requests.post(f"{BASE_URL}/api/research", json={
    "query": "Future of renewable energy",
    "export_format": "markdown",
    "tone": "professional",
    "word_count": 1200
}).json()
task_id = task["task_id"]

while True:
    status = requests.get(f"{BASE_URL}/api/research/{task_id}").json()
    print(f"Status: {status['status']}")

    if status["status"] == "hitl_review":
        requests.post(f"{BASE_URL}/api/research/{task_id}/resume",
                      json={"decision": "approve"})

    elif status["status"] == "completed":
        result = requests.get(f"{BASE_URL}/api/research/{task_id}/result").json()
        print(f"Saved to: {result['export_path']}")
        break

    elif status["status"] == "failed":
        print(f"Error: {status['error']}")
        break

    time.sleep(5)
```

### JavaScript (WebSocket)

```javascript
const BASE_URL = 'http://localhost:8000';

async function runResearch() {
  const { task_id } = await fetch(`${BASE_URL}/api/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'Future of renewable energy',
                           export_format: 'markdown', tone: 'professional', word_count: 1200 })
  }).then(r => r.json());

  const ws = new WebSocket(`ws://localhost:8000/ws/research/${task_id}`);

  ws.onmessage = async ({ data }) => {
    const { event_type, data: d } = JSON.parse(data);

    if (event_type === 'hitl_checkpoint') {
      await fetch(`${BASE_URL}/api/research/${task_id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: 'approve' })
      });
    }

    if (event_type === 'status_update' && d.status === 'completed') {
      const result = await fetch(`${BASE_URL}/api/research/${task_id}/result`).then(r => r.json());
      console.log('Saved to:', result.export_path);
      ws.close();
    }
  };
}

runResearch();
```

---

## Example Queries

- "Impact of artificial intelligence on healthcare in 2025"
- "Climate change effects on coastal cities"
- "Future of quantum computing and its applications"
- "Pros and cons of remote work in tech companies"
- "Latest developments in renewable energy technologies"

---

## Development

```bash
# Run tests
pytest tests/ -v
```

Use [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio) to visualize the agent graph. Full state is logged at each node transition for debugging.

## Contributing

Feel free to extend this project with:
- Additional export formats (PDF, HTML)
- More sophisticated quality checks
- Fact-checking agents
- Multi-language support
- Web UI for HITL

## License

MIT License — see `LICENSE` for details.

## Built With

- [LangGraph](https://github.com/langchain-ai/langgraph) — Agent orchestration
- [Mistral AI](https://mistral.ai/) — LLM provider
- [Tavily](https://tavily.com/) — Agent-optimized search API
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
