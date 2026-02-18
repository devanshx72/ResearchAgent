# Agentic Research & Article Generation System

A multi-agent pipeline built with **LangGraph** and powered by **Mistral AI** that transforms a single user query into a fully researched, human-reviewed, publication-ready article.

## Features

- **Autonomous Research**: Breaks topics into sub-questions, searches the web, grades results
- **Self-Correction**: Automatically rewrites poor queries and improves article quality
- **Multi-Agent Pipeline**: 9 specialized agents working in orchestrated sequence
- **Human-in-the-Loop**: Pause for human review before publishing
- **Quality Assurance**: Scores articles on coverage, accuracy, structure, and tone
- **Multiple Export Formats**: Markdown, DOCX, and Notion (upcoming)

## 🏗️ Architecture

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

## Quick Start

### 1. Clone and Setup

```bash
cd /Users/devansh/Coding/Agents
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file from the template:

```bash
cp .env.template .env
```

Edit `.env` and add your API keys:

```
MISTRAL_API_KEY=your_mistral_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run the Application

**Option A: FastAPI Server (Recommended)**

Start the server:
```bash
uvicorn app:app --reload --port 8000
```

Access the interactive API documentation:
```
http://localhost:8000/docs
```

Create a research task using the REST API (see [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details):
```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Impact of AI on healthcare in 2025",
    "export_format": "markdown",
    "tone": "professional",
    "word_count": 1500
  }'
```

**Option B: CLI Mode**

```bash
python main.py --query "Impact of AI on healthcare in 2025" --export-format markdown
```

Additional options:

```bash
python main.py \
  --query "Your research topic" \
  --export-format markdown \
  --tone professional \
  --word-count 1500
```

### 4. Handle HITL Checkpoint

When the system pauses for human review, you'll see the article draft in your terminal. To resume:

**Option 1: Approve**
```bash
python resume_hitl.py --thread-id default --decision approve
```

**Option 2: Request Edits**
```bash
python resume_hitl.py \
  --thread-id default \
  --decision edit \
  --feedback "Add more statistics about AI adoption rates"
```

**Option 3: Reject and Restart**
```bash
python resume_hitl.py \
  --thread-id default \
  --decision reject \
  --feedback "Focus more on challenges than benefits"
```

## Project Structure

```
.
├── app.py                      # FastAPI application
├── main.py                     # CLI entry point
├── resume_hitl.py              # CLI HITL resume script
├── requirements.txt            # Dependencies
├── .env                        # API keys (create from .env.template)
├── API_DOCUMENTATION.md        # FastAPI usage guide
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

## Configuration Options

| Argument | Default | Options | Description |
|----------|---------|---------|-------------|
| `--query` | Required | Any string | Research topic or question |
| `--export-format` | markdown | markdown, docx, notion | Output format |
| `--tone` | professional | professional, casual, technical | Article tone |
| `--word-count` | 1000 | 500-2000 | Target word count |
| `--thread-id` | default | Any string | Session ID for state persistence |

## Agent Descriptions

| Agent | Role | Model |
|-------|------|-------|
| **Query Analyzer** | Breaks query into 3-5 sub-questions | mistral-large-latest |
| **Web Search** | Searches Tavily API for each sub-question | N/A (API) |
| **Result Grader** | Scores results 1-5 on relevance | mistral-large-latest |
| **Query Rewriter** | Reformulates poor queries (max 3 iterations) | mistral-large-latest |
| **Synthesizer** | Aggregates results into structured notes | mistral-large-latest |
| **Article Writer** | Generates full article from notes | mistral-large-latest |
| **Quality Checker** | Scores article 0-100 on 4 dimensions | mistral-large-latest |
| **HITL Checkpoint** | Pauses for human review | N/A (interrupt) |
| **Publisher** | Exports to .md/.docx/Notion | N/A (I/O) |

## Quality Metrics

Articles are scored on:
- **Coverage** (0-25): Comprehensiveness of research notes
- **Factual Consistency** (0-25): Accuracy and proper citations
- **Structure** (0-25): Organization and flow
- **Tone** (0-25): Appropriateness and consistency

**Passing threshold**: 70/100

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Graph Visualization

Use [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio) to visualize the agent graph:

```bash
# Install LangGraph Studio, then open the project directory
```

### Logging

Full state is logged at each node transition for debugging.

## Example Queries

- "Impact of artificial intelligence on healthcare in 2025"
- "Climate change effects on coastal cities"
- "Future of quantum computing and its applications"
- "Pros and cons of remote work in tech companies"
- "Latest developments in renewable energy technologies"

## Contributing

This is a demonstration project for agentic AI concepts. Feel free to extend it with:
- Additional export formats (PDF, HTML)
- More sophisticated quality checks
- Fact-checking agents
- Multi-language support
- Web UI for HITL

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration framework
- [Mistral AI](https://mistral.ai/) - LLM provider
- [Tavily](https://tavily.com/) - Agent-optimized search API

---

**Note**: This system is designed for demonstration purposes. For production use, add appropriate error handling, rate limiting, and monitoring.
