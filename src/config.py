"""Loads the configuration from the environment."""
import os

def load_from_env():
    """Loads the configuration variables from the enviroment."""
    config = {"API_KEY" : os.getenv("API_KEY")}
    return config
