class Bus:
    """
    Sistema de suscripción/publicación (PubSub) para que las 
    features se comuniquen de forma reactiva.
    """
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_name: str, callback):
        """Una feature se suscribe a un evento."""
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        cls._subscribers[event_name].append(callback)
        """
        LOAD_ROOT : [callback1, callback2, callback3]
        """

    @classmethod
    def unsubscribe(cls, event_name: str, callback):
        if event_name in cls._subscribers:
            try:
                cls._subscribers[event_name].remove(callback)
            except ValueError:
                pass
            
    @classmethod
    def emit(cls, event_name: str, **kwargs):
        """Una feature lanza un evento con datos."""
        if event_name in cls._subscribers:
            for callback in cls._subscribers[event_name]:
                callback(**kwargs)
        """
        event_name ?= LOAD_ROOT
        for [callback1, callback3, callback3] in LOAD_ROOT(**KWARGS)
        """

    

    @classmethod
    def clear(cls):
        """Limpia todas las suscripciones (útil para tests)."""
        cls._subscribers = {}