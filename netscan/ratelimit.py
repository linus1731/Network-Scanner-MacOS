"""
Rate limiting for network scanner using token bucket algorithm.

Provides configurable rate limits to avoid overwhelming networks or
triggering IDS/IPS systems.
"""

import time
import threading
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for network operations.
    
    This implements a token bucket algorithm that allows:
    - Smooth rate limiting over time
    - Burst capacity for short periods
    - Thread-safe operation
    """
    
    def __init__(self, rate: Optional[int] = None, burst: Optional[int] = None):
        """
        Initialize rate limiter.
        
        Args:
            rate: Maximum packets per second (None = unlimited)
            burst: Maximum burst size (default: rate * 2)
        """
        self.rate = rate
        self.burst = burst or (rate * 2 if rate else None)
        
        # Token bucket state
        self.tokens = float(self.burst) if self.burst else float('inf')
        self.max_tokens = float(self.burst) if self.burst else float('inf')
        self.last_update = time.time()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.total_requests = 0
        self.throttled_requests = 0
    
    def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket.
        
        This method will block if insufficient tokens are available,
        waiting until enough tokens are replenished.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            Time waited in seconds (0 if no wait)
        """
        if self.rate is None or self.rate == 0:
            # Unlimited rate
            with self.lock:
                self.total_requests += tokens
            return 0.0
        
        with self.lock:
            self.total_requests += tokens
            
            # Replenish tokens based on time elapsed
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_tokens,
                self.tokens + (elapsed * self.rate)
            )
            self.last_update = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0
            
            # Not enough tokens, need to wait
            self.throttled_requests += 1
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.rate
            
        # Wait outside the lock to allow other threads
        time.sleep(wait_time)
        
        with self.lock:
            # Update tokens after waiting
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_tokens,
                self.tokens + (elapsed * self.rate)
            )
            self.last_update = now
            self.tokens -= tokens
        
        return wait_time
    
    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired, False otherwise
        """
        if self.rate is None or self.rate == 0:
            with self.lock:
                self.total_requests += tokens
            return True
        
        with self.lock:
            self.total_requests += tokens
            
            # Replenish tokens
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_tokens,
                self.tokens + (elapsed * self.rate)
            )
            self.last_update = now
            
            # Try to acquire
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            self.throttled_requests += tokens
            return False
    
    def set_rate(self, rate: Optional[int], burst: Optional[int] = None):
        """
        Update rate limit settings.
        
        Args:
            rate: New rate limit (packets per second)
            burst: New burst size (default: rate * 2)
        """
        with self.lock:
            self.rate = rate
            self.burst = burst or (rate * 2 if rate else None)
            self.max_tokens = float(self.burst) if self.burst else float('inf')
            # Reset tokens to new burst capacity
            self.tokens = float(self.burst) if self.burst else float('inf')
            self.last_update = time.time()
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return {
                'rate': self.rate,
                'burst': self.burst,
                'tokens': self.tokens,
                'total_requests': self.total_requests,
                'throttled_requests': self.throttled_requests,
                'throttle_percentage': (
                    (self.throttled_requests / self.total_requests * 100)
                    if self.total_requests > 0 else 0
                )
            }
    
    def reset_stats(self):
        """Reset statistics counters."""
        with self.lock:
            self.total_requests = 0
            self.throttled_requests = 0


# Global rate limiter instance
_global_limiter: Optional[RateLimiter] = None


def get_global_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter()
    return _global_limiter


def set_global_rate_limit(rate: Optional[int], burst: Optional[int] = None):
    """Set global rate limit."""
    limiter = get_global_limiter()
    limiter.set_rate(rate, burst)
