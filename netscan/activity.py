"""
Activity Feed - Track and display network scanning events.
"""

import time
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Event:
    """An activity event."""
    
    timestamp: float
    event_type: str  # 'scan', 'host_up', 'host_down', 'port_scan', 'export', 'cache', 'profile'
    message: str
    ip: Optional[str] = None
    severity: str = 'info'  # 'info', 'warning', 'error', 'success'
    
    def age_str(self) -> str:
        """Get human-readable age string."""
        age = time.time() - self.timestamp
        
        if age < 60:
            return f"{int(age)}s"
        elif age < 3600:
            return f"{int(age / 60)}m"
        elif age < 86400:
            return f"{int(age / 3600)}h"
        else:
            return f"{int(age / 86400)}d"
    
    def format(self, include_time: bool = True) -> str:
        """Format event for display."""
        icon = {
            'info': '•',
            'success': '✓',
            'warning': '⚠',
            'error': '✗',
        }.get(self.severity, '•')
        
        if include_time:
            return f"{icon} {self.message} ({self.age_str()})"
        return f"{icon} {self.message}"


class ActivityFeed:
    """
    Track network scanning activity events.
    """
    
    def __init__(self, max_events: int = 100):
        """
        Initialize activity feed.
        
        Args:
            max_events: Maximum number of events to keep
        """
        self.events: List[Event] = []
        self.max_events = max_events
    
    def add(
        self,
        event_type: str,
        message: str,
        ip: Optional[str] = None,
        severity: str = 'info'
    ) -> None:
        """
        Add a new event to the feed.
        
        Args:
            event_type: Type of event
            message: Event message
            ip: Related IP address (optional)
            severity: Event severity level
        """
        event = Event(
            timestamp=time.time(),
            event_type=event_type,
            message=message,
            ip=ip,
            severity=severity
        )
        
        self.events.append(event)
        
        # Trim if too many
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def get_recent(self, n: int = 10, event_type: Optional[str] = None) -> List[Event]:
        """
        Get recent events.
        
        Args:
            n: Number of events to return
            event_type: Filter by type (optional)
            
        Returns:
            List of recent events (newest first)
        """
        if event_type:
            filtered = [e for e in self.events if e.event_type == event_type]
            return list(reversed(filtered[-n:]))
        
        return list(reversed(self.events[-n:]))
    
    def get_by_ip(self, ip: str, n: int = 10) -> List[Event]:
        """
        Get events related to a specific IP.
        
        Args:
            ip: IP address to filter by
            n: Maximum number of events
            
        Returns:
            List of events for this IP (newest first)
        """
        filtered = [e for e in self.events if e.ip == ip]
        return list(reversed(filtered[-n:]))
    
    def get_errors(self, n: int = 10) -> List[Event]:
        """Get recent error events."""
        errors = [e for e in self.events if e.severity == 'error']
        return list(reversed(errors[-n:]))
    
    def get_warnings(self, n: int = 10) -> List[Event]:
        """Get recent warning events."""
        warnings = [e for e in self.events if e.severity == 'warning']
        return list(reversed(warnings[-n:]))
    
    def clear(self) -> None:
        """Clear all events."""
        self.events.clear()
    
    def clear_old(self, max_age_seconds: float = 3600) -> int:
        """
        Clear events older than specified age.
        
        Args:
            max_age_seconds: Maximum age to keep
            
        Returns:
            Number of events removed
        """
        cutoff = time.time() - max_age_seconds
        original_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp >= cutoff]
        return original_count - len(self.events)
    
    def count_by_type(self) -> dict[str, int]:
        """Get count of events by type."""
        counts: dict[str, int] = {}
        for event in self.events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts
    
    def count_by_severity(self) -> dict[str, int]:
        """Get count of events by severity."""
        counts: dict[str, int] = {}
        for event in self.events:
            counts[event.severity] = counts.get(event.severity, 0) + 1
        return counts
