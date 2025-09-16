import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # IPFS Configuration
    IPFS_HOST = os.getenv('IPFS_HOST', '127.0.0.1')
    IPFS_PORT = int(os.getenv('IPFS_PORT', 5001))
    
    # Blockchain Configuration
    DIFFICULTY = int(os.getenv('DIFFICULTY', 4))  # Number of leading zeros required for PoW
    
    # File Storage
    UPLOAD_FOLDER = 'uploads'
    DOWNLOAD_FOLDER = 'downloads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')