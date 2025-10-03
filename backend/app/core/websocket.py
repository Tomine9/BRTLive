from fastapi import WebSocket
from typing import List
import asyncio

class WebSocketManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send to one client"""
        try:
            await websocket.send_json(message)
        except (asyncio.CancelledError, ConnectionError, TimeoutError) as e:
            self.disconnect(websocket)
            return f"Error sending message to {websocket}: {e}"

    async def broadcast(self, message: dict):
        """Send to all connected clients"""
        if not self.active_connections:
            return
        
        # Send to all clients concurrently
        tasks = [
            self._safe_send(conn, message) 
            for conn in self.active_connections.copy()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_send(self, websocket: WebSocket, message: dict):
        """Send message with error handling"""
        try:
            await websocket.send_json(message)
        except (asyncio.CancelledError, ConnectionError, TimeoutError) as e:
            self.disconnect(websocket)
            return f"Error sending message to {websocket}: {e}"
    
    async def broadcast_all(self, message: dict):
        """Alias for broadcast"""
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

# Global instance
manager = WebSocketManager()
websocket_manager = manager  # Alias for compatibility
