"""
Memory management for StateCall library.
Handles conversation history storage and retrieval.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


# File paths for storage
HISTORY_FILE = ".statecall_history.json"
SESSIONS_FILE = ".statecall_sessions.json"


def _ensure_storage_files():
    """Ensure storage files exist with proper structure."""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'w') as f:
            json.dump({"sessions": []}, f)


def _load_history_data() -> Dict[str, Any]:
    """Load history data from file."""
    _ensure_storage_files()
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_history_data(data: Dict[str, Any]):
    """Save history data to file."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def _load_sessions_data() -> Dict[str, Any]:
    """Load sessions data from file."""
    _ensure_storage_files()
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"sessions": []}


def _save_sessions_data(data: Dict[str, Any]):
    """Save sessions data to file."""
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def append_to_history(session_id: str, role: str, content: str) -> None:
    """
    Add a message to the conversation history.
    
    Args:
        session_id: Unique identifier for the conversation session
        role: Message role ("user" or "assistant")
        content: Message content
    """
    if role not in ["user", "assistant"]:
        raise ValueError("Role must be 'user' or 'assistant'")
    
    history_data = _load_history_data()
    
    if session_id not in history_data:
        history_data[session_id] = []
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    history_data[session_id].append(message)
    _save_history_data(history_data)
    
    # Update sessions list
    sessions_data = _load_sessions_data()
    if session_id not in sessions_data["sessions"]:
        sessions_data["sessions"].append(session_id)
        _save_sessions_data(sessions_data)


def get_session_history(session_id: str) -> List[Dict[str, str]]:
    """
    Get raw conversation history for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of message dictionaries with role and content
    """
    history_data = _load_history_data()
    
    if session_id not in history_data:
        return []
    
    # Return only role and content for LLM API compatibility
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history_data[session_id]
    ]


def load_context(session_id: str) -> List[Dict[str, str]]:
    """
    Load conversation history in the format expected by most LLM APIs.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of message dictionaries with "role" and "content" keys
    """
    return get_session_history(session_id)


def clear_session(session_id: str) -> None:
    """
    Clear all history for a specific session.
    
    Args:
        session_id: Session identifier
    """
    history_data = _load_history_data()
    
    if session_id in history_data:
        del history_data[session_id]
        _save_history_data(history_data)
    
    # Remove from sessions list
    sessions_data = _load_sessions_data()
    if session_id in sessions_data["sessions"]:
        sessions_data["sessions"].remove(session_id)
        _save_sessions_data(sessions_data)


def list_sessions() -> List[str]:
    """
    Get a list of all active session IDs.
    
    Returns:
        List of session IDs
    """
    sessions_data = _load_sessions_data()
    return sessions_data.get("sessions", [])


def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with session information or None if not found
    """
    history_data = _load_history_data()
    
    if session_id not in history_data:
        return None
    
    messages = history_data[session_id]
    
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "created_at": messages[0]["timestamp"] if messages else None,
        "last_updated": messages[-1]["timestamp"] if messages else None,
        "user_messages": len([m for m in messages if m["role"] == "user"]),
        "assistant_messages": len([m for m in messages if m["role"] == "assistant"])
    } 