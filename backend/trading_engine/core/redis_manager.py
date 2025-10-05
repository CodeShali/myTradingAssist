"""
Redis connection and caching management.
"""
import json
from typing import Any, Optional, Dict, List
from datetime import timedelta
import redis
from loguru import logger

from config import settings


class RedisManager:
    """Redis connection and operations manager."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_keepalive=True,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check Redis connection."""
        try:
            self.client.ping()
            logger.info("Redis connection established")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def set(self, key: str, value: Any, expiration: Optional[int] = None) -> bool:
        """
        Set a value in Redis.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expiration: Expiration time in seconds
            
        Returns:
            True if successful
        """
        try:
            serialized_value = json.dumps(value)
            if expiration:
                return self.client.setex(key, expiration, serialized_value)
            else:
                return self.client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on a key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful
        """
        try:
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2
    
    def keys(self, pattern: str) -> List[str]:
        """
        Get all keys matching a pattern.
        
        Args:
            pattern: Key pattern (e.g., "user:*")
            
        Returns:
            List of matching keys
        """
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []
    
    def flush_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Key pattern
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis FLUSH error for pattern {pattern}: {e}")
            return 0
    
    # Hash operations
    def hset(self, name: str, key: str, value: Any) -> bool:
        """Set hash field."""
        try:
            serialized_value = json.dumps(value)
            return bool(self.client.hset(name, key, serialized_value))
        except Exception as e:
            logger.error(f"Redis HSET error for {name}:{key}: {e}")
            return False
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        """Get hash field."""
        try:
            value = self.client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis HGET error for {name}:{key}: {e}")
            return None
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all hash fields."""
        try:
            data = self.client.hgetall(name)
            return {k: json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Redis HGETALL error for {name}: {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        try:
            return self.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis HDEL error for {name}: {e}")
            return 0
    
    # List operations
    def lpush(self, key: str, *values: Any) -> int:
        """Push values to list (left)."""
        try:
            serialized_values = [json.dumps(v) for v in values]
            return self.client.lpush(key, *serialized_values)
        except Exception as e:
            logger.error(f"Redis LPUSH error for {key}: {e}")
            return 0
    
    def rpush(self, key: str, *values: Any) -> int:
        """Push values to list (right)."""
        try:
            serialized_values = [json.dumps(v) for v in values]
            return self.client.rpush(key, *serialized_values)
        except Exception as e:
            logger.error(f"Redis RPUSH error for {key}: {e}")
            return 0
    
    def lpop(self, key: str) -> Optional[Any]:
        """Pop value from list (left)."""
        try:
            value = self.client.lpop(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis LPOP error for {key}: {e}")
            return None
    
    def rpop(self, key: str) -> Optional[Any]:
        """Pop value from list (right)."""
        try:
            value = self.client.rpop(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis RPOP error for {key}: {e}")
            return None
    
    def lrange(self, key: str, start: int, end: int) -> List[Any]:
        """Get range of list values."""
        try:
            values = self.client.lrange(key, start, end)
            return [json.loads(v) for v in values]
        except Exception as e:
            logger.error(f"Redis LRANGE error for {key}: {e}")
            return []
    
    # Pub/Sub operations
    def publish(self, channel: str, message: Any) -> int:
        """
        Publish message to channel.
        
        Args:
            channel: Channel name
            message: Message to publish
            
        Returns:
            Number of subscribers that received the message
        """
        try:
            serialized_message = json.dumps(message)
            return self.client.publish(channel, serialized_message)
        except Exception as e:
            logger.error(f"Redis PUBLISH error for channel {channel}: {e}")
            return 0
    
    def subscribe(self, *channels: str):
        """
        Subscribe to channels.
        
        Args:
            channels: Channel names to subscribe to
            
        Returns:
            PubSub object
        """
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            logger.error(f"Redis SUBSCRIBE error: {e}")
            return None
    
    # Utility methods
    def ping(self) -> bool:
        """Check if Redis is responsive."""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False
    
    def flushdb(self) -> bool:
        """Flush current database (use with caution!)."""
        try:
            return self.client.flushdb()
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    def info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        try:
            return self.client.info()
        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            return {}


# Cache key builders
class CacheKeys:
    """Cache key builders for consistent naming."""
    
    @staticmethod
    def market_data(symbol: str, data_type: str) -> str:
        """Market data cache key."""
        return f"market_data:{symbol}:{data_type}"
    
    @staticmethod
    def options_chain(symbol: str) -> str:
        """Options chain cache key."""
        return f"options_chain:{symbol}"
    
    @staticmethod
    def news_sentiment(symbol: str) -> str:
        """News sentiment cache key."""
        return f"news_sentiment:{symbol}"
    
    @staticmethod
    def user_config(user_id: str) -> str:
        """User configuration cache key."""
        return f"user_config:{user_id}"
    
    @staticmethod
    def pending_signals(user_id: str) -> str:
        """Pending signals cache key."""
        return f"pending_signals:{user_id}"
    
    @staticmethod
    def open_positions(user_id: str) -> str:
        """Open positions cache key."""
        return f"open_positions:{user_id}"
    
    @staticmethod
    def portfolio_greeks(user_id: str) -> str:
        """Portfolio Greeks cache key."""
        return f"portfolio_greeks:{user_id}"
    
    @staticmethod
    def rate_limit(service: str, identifier: str) -> str:
        """Rate limit cache key."""
        return f"rate_limit:{service}:{identifier}"
    
    @staticmethod
    def session(session_id: str) -> str:
        """Session cache key."""
        return f"session:{session_id}"


# Global Redis manager instance
redis_manager = RedisManager()
