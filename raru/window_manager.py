class WindowManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WindowManager()
        return cls._instance
    
    def __init__(self):
        self.current_window = None
        
    def switch_to_window(self, window_class, *args, **kwargs):
        new_window = window_class(*args, **kwargs)
        if self.current_window:
            self.current_window.close()
        self.current_window = new_window
        self.current_window.show()
        return new_window
