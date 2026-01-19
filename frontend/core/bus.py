class Bus:
    """
    Subscription/publishing system so that 
    features are communicated reactively.
    """
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_name: str, callback):
        """Subscribe a function to a specific event."""
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        cls._subscribers[event_name].append(callback)

    @classmethod
    def unsubscribe(cls, event_name: str, callback):
        """Remove a function from an event's subscriber list."""
        if event_name in cls._subscribers:
            try:
                cls._subscribers[event_name].remove(callback)
            except ValueError:
                pass
            
    @classmethod
    def emit(cls, event_name: str, **kwargs):
        """Trigger an event and send data to all its subscribers."""
        if event_name in cls._subscribers:
            for callback in cls._subscribers[event_name]:
                callback(**kwargs)

    @classmethod
    def clear(cls):
        """Remove all subscriptions."""
        cls._subscribers = {}