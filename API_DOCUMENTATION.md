# FastAPI Application - API Documentation

## Running the Server

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn app:app --reload --port 8000

# Or using the app directly
python app.py
```

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## REST API

### 1. Create Research Task

**Endpoint:** `POST /api/research`

**Description:** Starts a new research task and begins processing in the background.

**Request Body:**
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
  "message": "Research task created successfully. Task ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

**Example cURL:**
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

---

### 2. Get Task Status

**Endpoint:** `GET /api/research/{task_id}`

**Description:** Retrieves the current status and progress of a research task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
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

**When at HITL Checkpoint:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "hitl_review",
  "current_node": "hitl",
  "article_draft": "# Article Title\n\nArticle content here...",
  "quality_score": 85.0,
  "sources": ["https://example.com/1", "https://example.com/2"]
}
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/api/research/550e8400-e29b-41d4-a716-446655440000"
```

---

### 3. Resume from HITL Checkpoint

**Endpoint:** `POST /api/research/{task_id}/resume`

**Description:** Resumes a paused task from the HITL checkpoint with human decision.

**Request Body:**
```json
{
  "decision": "approve",
  "feedback": null
}
```

**Decision Options:**
- `approve` - Publish the article as is
- `edit` - Send back to writer with feedback
- `reject` - Restart from the beginning with feedback

**Request Body (with feedback):**
```json
{
  "decision": "edit",
  "feedback": "Add more statistics about hospital adoption rates"
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Task resumed with decision: approve"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/research/550e8400-e29b-41d4-a716-446655440000/resume" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve"
  }'
```

---

### 4. Get Task Result

**Endpoint:** `GET /api/research/{task_id}/result`

**Description:** Retrieves the final article and metadata for a completed task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "final_article": "# Article Title\n\nFull article content...",
  "export_path": "outputs/Impact_of_AI_on_healthcare_20260217_140530.md",
  "sources": [
    "https://example.com/source1",
    "https://example.com/source2"
  ],
  "quality_score": 92.0
}
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/api/research/550e8400-e29b-41d4-a716-446655440000/result"
```

---

### 5. Delete Task

**Endpoint:** `DELETE /api/research/{task_id}`

**Description:** Deletes a task and its associated data.

**Response:**
```json
{
  "message": "Task 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

**Example cURL:**
```bash
curl -X DELETE "http://localhost:8000/api/research/550e8400-e29b-41d4-a716-446655440000"
```

---

## WebSocket API

### Real-Time Task Updates

**Endpoint:** `WS /ws/research/{task_id}`

**Description:** Opens a WebSocket connection for real-time updates on task progress.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/research/550e8400-e29b-41d4-a716-446655440000');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
};

// Keep-alive ping
setInterval(() => {
  ws.send('ping');
}, 30000);
```

**Message Types:**

1. **Connected**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "connected",
  "data": {
    "status": "processing",
    "current_node": "query_analyzer",
    "message": "Connected to task updates"
  }
}
```

2. **Node Complete**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "node_complete",
  "data": {
    "node": "web_search",
    "state_keys": ["search_results"]
  }
}
```

3. **Status Update**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "status_update",
  "data": {
    "status": "processing",
    "message": "Starting research pipeline"
  }
}
```

4. **HITL Checkpoint**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
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

5. **Error**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "error",
  "data": {
    "status": "failed",
    "error": "Error message here"
  }
}
```

---

## Complete Workflow Example

### Python Client

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Create research task
response = requests.post(f"{BASE_URL}/api/research", json={
    "query": "Future of renewable energy",
    "export_format": "markdown",
    "tone": "professional",
    "word_count": 1200
})
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# 2. Poll for status
while True:
    status_response = requests.get(f"{BASE_URL}/api/research/{task_id}")
    status_data = status_response.json()
    
    print(f"Status: {status_data['status']}")
    
    if status_data["status"] == "hitl_review":
        print("HITL checkpoint reached!")
        print(f"Quality Score: {status_data['quality_score']}")
        
        # 3. Resume with approval
        resume_response = requests.post(
            f"{BASE_URL}/api/research/{task_id}/resume",
            json={"decision": "approve"}
        )
        print("Task resumed")
        
    elif status_data["status"] == "completed":
        print("Task completed!")
        
        # 4. Get final result
        result_response = requests.get(f"{BASE_URL}/api/research/{task_id}/result")
        result = result_response.json()
        
        print(f"Export Path: {result['export_path']}")
        print(f"Sources: {len(result['sources'])}")
        break
        
    elif status_data["status"] == "failed":
        print(f"Task failed: {status_data['error']}")
        break
    
    time.sleep(5)
```

### JavaScript Client (with WebSocket)

```javascript
const BASE_URL = 'http://localhost:8000';

async function runResearchTask() {
  // 1. Create task
  const response = await fetch(`${BASE_URL}/api/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: 'Future of renewable energy',
      export_format: 'markdown',
      tone: 'professional',
      word_count: 1200
    })
  });
  
  const { task_id } = await response.json();
  console.log('Task ID:', task_id);
  
  // 2. Connect WebSocket for real-time updates
  const ws = new WebSocket(`ws://localhost:8000/ws/research/${task_id}`);
  
  ws.onmessage = async (event) => {
    const message = JSON.parse(event.data);
    console.log('Event:', message.event_type, message.data);
    
    if (message.event_type === 'hitl_checkpoint') {
      console.log('HITL checkpoint - Quality Score:', message.data.quality_score);
      
      // 3. Approve the article
      await fetch(`${BASE_URL}/api/research/${task_id}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: 'approve' })
      });
    }
    
    if (message.event_type === 'status_update' && message.data.status === 'completed') {
      // 4. Get final result
      const resultResponse = await fetch(`${BASE_URL}/api/research/${task_id}/result`);
      const result = await resultResponse.json();
      
      console.log('Article saved to:', result.export_path);
      ws.close();
    }
  };
}

runResearchTask();
```

---

## Status Codes

- `200` - Success
- `400` - Bad Request (e.g., task not at HITL checkpoint)
- `404` - Task Not Found
- `500` - Internal Server Error

---

## Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Agentic Research System",
  "version": "1.0.0"
}
```
