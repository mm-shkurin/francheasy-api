import uuid
import json
import redis
from typing import Dict, Optional
from app.core.config import RedisSettings

redis_settings = RedisSettings()

class PKCEService:
    def __init__(self):
        redis_params = {
            'host': redis_settings.redis_network_name,
            'port': redis_settings.redis_port,
            'decode_responses': True
        }
        
        if redis_settings.redis_password:
            redis_params['password'] = redis_settings.redis_password
        
        if redis_settings.redis_user and redis_settings.redis_user_password:
            redis_params['username'] = redis_settings.redis_user
            redis_params['password'] = redis_settings.redis_user_password
        
        try:
            self.redis_client = redis.Redis(**redis_params)
            self.redis_client.ping()
        except redis.exceptions.ConnectionError as e:
            raise Exception(f"Failed to connect to Redis: {e}")
        except redis.exceptions.AuthenticationError as e:
            raise Exception(f"Redis authentication failed: {e}")
    
    async def store_pkce_pair(self, code_verifier: str, code_challenge: str, ttl: int = 300) -> str:
        session_id = str(uuid.uuid4())

        pkce_data = {
            "verifier": code_verifier,
            "challenge": code_challenge,
        }    

        try:
            self.redis_client.setex(
                f"pkce:{session_id}",
                ttl,
                json.dumps(pkce_data)
            )
        except redis.exceptions.RedisError as e:
            raise Exception(f"Failed to store PKCE pair in Redis: {e}")

        return session_id
    
    async def get_pkce_pair(self, session_id: str) -> Optional[Dict[str, str]]:
        try:
            data = self.redis_client.get(f"pkce:{session_id}")
            if data:
                return json.loads(data)
            return None
        except redis.exceptions.RedisError as e:
            raise Exception(f"Failed to get PKCE pair from Redis: {e}")

    async def delete_pkce_pair(self, session_id: str) -> bool:
        try:
            result = self.redis_client.delete(f"pkce:{session_id}")
            return result > 0
        except redis.exceptions.RedisError as e:
            raise Exception(f"Failed to delete PKCE pair from Redis: {e}")