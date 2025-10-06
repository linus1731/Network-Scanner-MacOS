#!/usr/bin/env python3
"""Unit tests for rate limiting module."""

import unittest
import time
import threading
from netscan.ratelimit import RateLimiter


class TestRateLimiter(unittest.TestCase):
    """Test the RateLimiter class."""
    
    def test_basic_acquire(self):
        """Test basic token acquisition."""
        limiter = RateLimiter(rate=10, burst=10)
        
        # Should acquire immediately (burst available)
        start = time.time()
        limiter.acquire(5)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.1, "Should acquire from burst without delay")
    
    def test_rate_limiting(self):
        """Test that rate limiting actually slows down requests."""
        limiter = RateLimiter(rate=5, burst=5)  # 5 req/s
        
        # First 5 should be instant (burst)
        start = time.time()
        for _ in range(5):
            limiter.acquire(1)
        burst_time = time.time() - start
        self.assertLess(burst_time, 0.1, "Burst should be instant")
        
        # Next 5 should take ~1 second (rate limited)
        start = time.time()
        for _ in range(5):
            limiter.acquire(1)
        limited_time = time.time() - start
        
        # Should take approximately 1 second (5 tokens at 5/sec)
        self.assertGreater(limited_time, 0.8, "Should be rate limited")
        self.assertLess(limited_time, 1.3, "Should not be too slow")
    
    def test_try_acquire_success(self):
        """Test non-blocking acquire when tokens available."""
        limiter = RateLimiter(rate=10, burst=10)
        
        # Should succeed without waiting
        result = limiter.try_acquire(5)
        self.assertTrue(result, "Should succeed when tokens available")
    
    def test_try_acquire_fail(self):
        """Test non-blocking acquire when tokens unavailable."""
        limiter = RateLimiter(rate=5, burst=5)
        
        # Consume all burst tokens
        limiter.acquire(5)
        
        # Try to acquire more without waiting - should fail
        result = limiter.try_acquire(1)
        self.assertFalse(result, "Should fail when tokens unavailable")
    
    def test_set_rate(self):
        """Test dynamic rate adjustment."""
        limiter = RateLimiter(rate=10, burst=10)
        
        # Change rate
        limiter.set_rate(20, 20)
        
        # Should now allow 20 tokens/second
        start = time.time()
        for _ in range(20):
            limiter.acquire(1)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.2, "Should acquire burst quickly at new rate")
    
    def test_get_stats(self):
        """Test statistics tracking."""
        limiter = RateLimiter(rate=5, burst=5)
        
        # Make some requests
        limiter.acquire(3)
        
        stats = limiter.get_stats()
        
        self.assertEqual(stats['rate'], 5)
        self.assertEqual(stats['burst'], 5)
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['throttled_requests'], 0)
        self.assertIn('tokens', stats)  # Fixed: was 'current_tokens'
    
    def test_thread_safety(self):
        """Test that RateLimiter is thread-safe."""
        limiter = RateLimiter(rate=50, burst=50)
        results = []
        
        def worker():
            for _ in range(10):
                limiter.acquire(1)
                results.append(1)
        
        # Spawn 10 threads, each acquiring 10 tokens
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Should have 100 total acquisitions
        self.assertEqual(len(results), 100)
        
        # Check stats
        stats = limiter.get_stats()
        self.assertEqual(stats['total_requests'], 100)
    
    def test_zero_rate_unlimited(self):
        """Test that zero rate means unlimited."""
        limiter = RateLimiter(rate=0, burst=1)
        
        # Should acquire many tokens instantly
        start = time.time()
        for _ in range(1000):
            result = limiter.try_acquire(1)
            self.assertTrue(result, "Should always succeed with zero rate")
        
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.5, "Should be instant with unlimited rate")
    
    def test_burst_larger_than_rate(self):
        """Test burst size larger than rate."""
        limiter = RateLimiter(rate=5, burst=20)
        
        # Should be able to acquire burst immediately
        start = time.time()
        limiter.acquire(20)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.1, "Should acquire full burst quickly")
    
    def test_multiple_acquire(self):
        """Test acquiring multiple tokens at once."""
        limiter = RateLimiter(rate=10, burst=10)
        
        # Acquire 5 tokens at once
        start = time.time()
        limiter.acquire(5)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.1, "Should acquire multiple tokens from burst")
        
        stats = limiter.get_stats()
        self.assertEqual(stats['total_requests'], 5)
    
    def test_refill_over_time(self):
        """Test that tokens refill over time."""
        limiter = RateLimiter(rate=10, burst=10)
        
        # Consume all burst
        limiter.acquire(10)
        
        # Wait for some tokens to refill (0.5s = 5 tokens at 10/s)
        time.sleep(0.5)
        
        # Should be able to acquire ~5 tokens without much delay
        start = time.time()
        limiter.acquire(5)
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 0.2, "Tokens should have refilled")
    
    def test_stats_throttled_requests(self):
        """Test that throttled requests are tracked."""
        limiter = RateLimiter(rate=5, burst=5)
        
        # Consume burst
        limiter.acquire(5)
        
        # These should be throttled
        limiter.acquire(3)
        
        stats = limiter.get_stats()
        self.assertGreater(stats['throttled_requests'], 0, "Should track throttled requests")
    
    def test_large_burst(self):
        """Test acquiring more tokens than burst size."""
        limiter = RateLimiter(rate=10, burst=5)
        
        # Try to acquire more than burst - should wait
        start = time.time()
        limiter.acquire(10)
        elapsed = time.time() - start
        
        # Should take at least 0.5s to get the extra 5 tokens
        self.assertGreater(elapsed, 0.4, "Should wait for tokens beyond burst")


if __name__ == "__main__":
    unittest.main()
