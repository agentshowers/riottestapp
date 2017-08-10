"""Loads the configuration from the environment."""
import os

def load_from_env():
    """Loads the configuration variables from the enviroment."""
    config = {"API_KEY" : os.getenv("API_KEY", "RGAPI-b55dda10-a748-460e-92c3-d0d9afea3c25"),
              "PORT" : os.getenv("PORT", 4555),
              "HOST" : os.getenv("HOST", "0.0.0.0")}
    return config
