# In src/open_llm_vtuber/config_manager.py
class Config:
    _instance = None

    def __init__(self):
        self.current_language = "en-US"  # default value

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance
