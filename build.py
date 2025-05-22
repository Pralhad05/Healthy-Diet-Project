import os
import shutil
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def create_build_directory():
    try:
        # Create main build directory
        if not os.path.exists('build'):
            os.makedirs('build')
            logging.info("Created build directory")
        
        # Create necessary directories
        directories = [
            'build/functions',
            'build/static',
            'build/templates',
            'build/api'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Created directory: {directory}")
        
        # Copy application files
        app_files = {
            'appmy.py': 'build/api/app.py',
            'requirements.txt': 'build/requirements.txt',
            'netlify.toml': 'build/netlify.toml',
            'runtime.txt': 'build/runtime.txt'
        }
        
        for src, dest in app_files.items():
            if os.path.exists(src):
                shutil.copy2(src, dest)
                logging.info(f"Copied {src} to {dest}")
            else:
                logging.warning(f"Source file not found: {src}")
        
        # Copy static and template directories
        if os.path.exists('static'):
            shutil.copytree('static', 'build/static', dirs_exist_ok=True)
            logging.info("Copied static directory")
        else:
            logging.warning("Static directory not found")
            
        if os.path.exists('templates'):
            shutil.copytree('templates', 'build/templates', dirs_exist_ok=True)
            logging.info("Copied templates directory")
        else:
            logging.warning("Templates directory not found")
        
        # Create serverless function
        with open('build/functions/flask_app.py', 'w') as f:
            f.write('''from flask import Flask
from api.app import app as flask_app

def handler(event, context):
    """Handle the incoming request and pass it to Flask."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': flask_app(event, context)
    }
''')
        logging.info("Created serverless function")
        
        # Create a simple index.html if it doesn't exist
        if not os.path.exists('build/static/index.html'):
            with open('build/static/index.html', 'w') as f:
                f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Healthy Diet Project</title>
    <meta http-equiv="refresh" content="0;url=/.netlify/functions/flask_app">
</head>
<body>
    <p>Redirecting to application...</p>
</body>
</html>''')
            logging.info("Created index.html")
        
        logging.info("Build directory created successfully!")
        return True
        
    except Exception as e:
        logging.error(f"Error during build: {str(e)}")
        return False

if __name__ == '__main__':
    success = create_build_directory()
    if not success:
        sys.exit(1) 