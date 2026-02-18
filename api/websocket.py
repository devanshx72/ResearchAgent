"""
WebSocket endpoint for real-time task updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.task_manager import task_manager


router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/research/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time research task updates.
    
    Connects to a specific task and receives updates as the agent pipeline progresses.
    
    Message format:
    {
        "task_id": "...",
        "event_type": "node_complete" | "status_update" | "error" | "hitl_checkpoint",
        "data": {...}
    }
    """
    await websocket.accept()
    
    # Check if task exists
    task = await task_manager.get_task(task_id)
    if not task:
        await websocket.send_json({
            "task_id": task_id,
            "event_type": "error",
            "data": {"message": f"Task {task_id} not found"}
        })
        await websocket.close()
        return
    
    # Add subscriber
    await task_manager.add_subscriber(task_id, websocket)
    
    # Send initial status
    await websocket.send_json({
        "task_id": task_id,
        "event_type": "connected",
        "data": {
            "status": task["status"],
            "current_node": task.get("current_node"),
            "message": "Connected to task updates"
        }
    })
    
    try:
        # Keep connection alive and handle any client messages
        while True:
            # Wait for messages from client (e.g., ping/pong)
            data = await websocket.receive_text()
            
            # Echo back as pong
            if data == "ping":
                await websocket.send_json({
                    "task_id": task_id,
                    "event_type": "pong",
                    "data": {}
                })
    
    except WebSocketDisconnect:
        # Remove subscriber on disconnect
        await task_manager.remove_subscriber(task_id, websocket)
