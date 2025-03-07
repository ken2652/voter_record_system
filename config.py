import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey@12345')
    
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Test@123')
    MYSQL_DB = os.getenv('MYSQL_DB', 'voter_records')
    
    # Application Configuration
    RECORDS_PER_PAGE = 10
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'} 