import os
import shutil

def create_build_directory():
    # Create main build directory
    if not os.path.exists('build'):
        os.makedirs('build')
    
    # Create necessary directories
    directories = [
        'build/functions',
        'build/static',
        'build/templates',
        'build/api'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
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
    
    # Copy static and template directories
    if os.path.exists('static'):
        shutil.copytree('static', 'build/static', dirs_exist_ok=True)
    if os.path.exists('templates'):
        shutil.copytree('templates', 'build/templates', dirs_exist_ok=True)
    
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

if __name__ == '__main__':
    create_build_directory()
    print("Build directory created successfully!") 