"""Loads the configuration from the environment."""
import os

def load_from_env():
    """Loads the configuration variables from the enviroment."""
    config = {"API_KEY" : os.getenv("API_KEY", "RGAPI-008f6402-5ce2-4f9a-96ec-b73d5a8e6737"),
              "PORT" : os.getenv("PORT", 4555),
              "HOST" : os.getenv("HOST", "0.0.0.0")}
    return config
