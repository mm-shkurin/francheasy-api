import secrets
from typing import Set

class SessionService:
    def __init__(self):
        self.active_sessions: Set[str] = set()
    
    def create_session_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def is_valid_session(self, session_token: str) -> bool:
        return session_token in self.active_sessions
    
    def add_session(self, session_token: str):
        self.active_sessions.add(session_token)
    
    def remove_session(self, session_token: str):
        self.active_sessions.discard(session_token)

session_service = SessionService()