"""
Task manager for handling async research tasks.
"""

import uuid
import asyncio
from typing import Dict, Optional
from datetime import datetime
from models.schemas import TaskStatus, ResearchRequest


class TaskManager:
    """Manages research task state and execution."""
    
    def __init__(self):
        """Initialize task manager."""
        self.tasks: Dict[str, dict] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(self, request: ResearchRequest) -> str:
        """
        Create a new research task.
        
        Args:
            request: Research request parameters
            
        Returns:
            task_id: Unique task identifier
        """
        task_id = str(uuid.uuid4())
        
        async with self._lock:
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": TaskStatus.pending,
                "request": request.dict(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "current_node": None,
                "state": {},
                "result": None,
                "error": None,
                "subscribers": set()  # WebSocket connections
            }
        
        return task_id
    
    async def get_task(self, task_id: str) -> Optional[dict]:
        """Get task by ID."""
        async with self._lock:
            return self.tasks.get(task_id)
    
    async def update_task(self, task_id: str, updates: dict):
        """
        Update task fields.
        
        Args:
            task_id: Task identifier
            updates: Dictionary of fields to update
        """
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(updates)
                self.tasks[task_id]["updated_at"] = datetime.utcnow().isoformat()
    
    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        current_node: Optional[str] = None
    ):
        """Update task status and optionally current node."""
        updates = {"status": status}
        if current_node:
            updates["current_node"] = current_node
        
        await self.update_task(task_id, updates)
    
    async def update_state(self, task_id: str, state: dict):
        """Update task state."""
        await self.update_task(task_id, {"state": state})
    
    async def set_result(self, task_id: str, result: dict):
        """Set final task result."""
        await self.update_task(task_id, {
            "result": result,
            "status": TaskStatus.completed
        })
    
    async def set_error(self, task_id: str, error: str):
        """Set task error."""
        await self.update_task(task_id, {
            "error": error,
            "status": TaskStatus.failed
        })
    
    async def add_subscriber(self, task_id: str, websocket):
        """Add WebSocket subscriber for task updates."""
        task = await self.get_task(task_id)
        if task:
            task["subscribers"].add(websocket)
    
    async def remove_subscriber(self, task_id: str, websocket):
        """Remove WebSocket subscriber."""
        task = await self.get_task(task_id)
        if task and websocket in task["subscribers"]:
            task["subscribers"].remove(websocket)
    
    async def broadcast_update(self, task_id: str, message: dict):
        """Broadcast update to all subscribers of a task."""
        task = await self.get_task(task_id)
        if task and task["subscribers"]:
            import json
            message_str = json.dumps(message)
            
            # Send to all subscribers
            disconnected = set()
            for websocket in task["subscribers"]:
                try:
                    await websocket.send_text(message_str)
                except Exception:
                    disconnected.add(websocket)
            
            # Remove disconnected subscribers
            for ws in disconnected:
                task["subscribers"].discard(ws)


# Global task manager instance
task_manager = TaskManager()
