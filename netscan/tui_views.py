"""
TUI View System - Multiple view support for the network scanner TUI.

Provides a framework for switching between different views:
- Dashboard: Network overview with statistics
- Host List: Traditional scrollable host table
- Detail View: Deep dive into a single host
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict, Any
import curses

if TYPE_CHECKING:
    from typing import Protocol
    
    class AppState(Protocol):
        """Type hint for app state"""
        pass


class View(ABC):
    """Base class for all TUI views."""
    
    def __init__(self, name: str):
        """
        Initialize view.
        
        Args:
            name: Unique identifier for this view
        """
        self.name = name
        self.active = False
    
    @abstractmethod
    def draw(self, stdscr, app_state: Any) -> None:
        """
        Draw the view to the screen.
        
        Args:
            stdscr: Curses window object
            app_state: Application state object
        """
        pass
    
    @abstractmethod
    def handle_input(self, ch: int, app_state: Any) -> bool:
        """
        Handle keyboard input for this view.
        
        Args:
            ch: Character code from getch()
            app_state: Application state object
            
        Returns:
            True if input was handled, False to pass to global handlers
        """
        pass
    
    def on_enter(self, app_state: Any) -> None:
        """
        Called when switching TO this view.
        
        Args:
            app_state: Application state object
        """
        self.active = True
    
    def on_exit(self, app_state: Any) -> None:
        """
        Called when switching FROM this view.
        
        Args:
            app_state: Application state object
        """
        self.active = False
    
    def get_title(self) -> str:
        """Get the display title for this view."""
        return self.name.title()


class ViewManager:
    """
    Manages multiple views and handles switching between them.
    """
    
    def __init__(self):
        """Initialize the view manager."""
        self.views: Dict[str, View] = {}
        self.current_view: Optional[str] = None
        self.view_history: list[str] = []
    
    def register_view(self, view: View) -> None:
        """
        Register a view.
        
        Args:
            view: View instance to register
        """
        self.views[view.name] = view
        
        # Set first view as current
        if self.current_view is None:
            self.current_view = view.name
            view.on_enter(None)
    
    def switch_to(self, view_name: str, app_state: Any) -> bool:
        """
        Switch to a different view.
        
        Args:
            view_name: Name of the view to switch to
            app_state: Application state object
            
        Returns:
            True if switch succeeded, False if view not found
        """
        if view_name not in self.views:
            return False
        
        if view_name == self.current_view:
            return True  # Already on this view
        
        # Exit current view
        if self.current_view:
            old_view = self.views[self.current_view]
            old_view.on_exit(app_state)
            self.view_history.append(self.current_view)
        
        # Enter new view
        self.current_view = view_name
        new_view = self.views[view_name]
        new_view.on_enter(app_state)
        
        return True
    
    def go_back(self, app_state: Any) -> bool:
        """
        Go back to previous view.
        
        Args:
            app_state: Application state object
            
        Returns:
            True if went back, False if no history
        """
        if not self.view_history:
            return False
        
        previous = self.view_history.pop()
        return self.switch_to(previous, app_state)
    
    def cycle_next(self, app_state: Any) -> None:
        """
        Cycle to the next view.
        
        Args:
            app_state: Application state object
        """
        view_names = list(self.views.keys())
        if not view_names:
            return
        
        try:
            current_idx = view_names.index(self.current_view)
            next_idx = (current_idx + 1) % len(view_names)
            self.switch_to(view_names[next_idx], app_state)
        except ValueError:
            # Current view not found, go to first
            self.switch_to(view_names[0], app_state)
    
    def cycle_prev(self, app_state: Any) -> None:
        """
        Cycle to the previous view.
        
        Args:
            app_state: Application state object
        """
        view_names = list(self.views.keys())
        if not view_names:
            return
        
        try:
            current_idx = view_names.index(self.current_view)
            prev_idx = (current_idx - 1) % len(view_names)
            self.switch_to(view_names[prev_idx], app_state)
        except ValueError:
            # Current view not found, go to last
            self.switch_to(view_names[-1], app_state)
    
    def draw(self, stdscr, app_state: Any) -> None:
        """
        Draw the current view.
        
        Args:
            stdscr: Curses window object
            app_state: Application state object
        """
        if self.current_view and self.current_view in self.views:
            view = self.views[self.current_view]
            view.draw(stdscr, app_state)
    
    def handle_input(self, ch: int, app_state: Any) -> bool:
        """
        Handle input for current view.
        
        Args:
            ch: Character code from getch()
            app_state: Application state object
            
        Returns:
            True if input was handled, False otherwise
        """
        if self.current_view and self.current_view in self.views:
            view = self.views[self.current_view]
            return view.handle_input(ch, app_state)
        return False
    
    def get_current_view(self) -> Optional[View]:
        """Get the currently active view."""
        if self.current_view and self.current_view in self.views:
            return self.views[self.current_view]
        return None
    
    def get_view_tabs(self) -> str:
        """
        Get a string showing all views as tabs.
        
        Returns:
            Tab bar string like "[F1] Dashboard  [F2] Hosts  [F3] Details"
        """
        tabs = []
        fkey_map = {
            'dashboard': 'F1',
            'hosts': 'F2',
            'details': 'F3',
        }
        
        for name, view in self.views.items():
            fkey = fkey_map.get(name, '')
            if fkey:
                active = "●" if name == self.current_view else "○"
                tabs.append(f"[{fkey}] {active} {view.get_title()}")
        
        return "  ".join(tabs)
