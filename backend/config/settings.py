import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

APP_NAME = "KnitAgent"
# Create a dictionary of environment variables
config = dict(os.environ)
