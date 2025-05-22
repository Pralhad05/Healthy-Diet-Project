import os
import shutil

def create_build_directory():
    # Create main build directory
    if not os.path.exists('build'):
        os.makedirs('build')
    
    # Create Netlify-specific directories
    directories = [
        'build/functions',
        'build/static',
        'build/static/uploads',
        'build/templates',
        'build/instance',
        'build/api'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Copy application files
    app_files = {
        'appmy.py': 'build/api/app.py',
        'requirements.txt': 'build/requirements.txt',
        'netlify.toml': 'build/netlify.toml'
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
        f.write('''from flask import Flask, request
from api.app import app as flask_app

def handler(event, context):
    """Handle the incoming request and pass it to Flask."""
    # Convert Netlify event to WSGI environment
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'SCRIPT_NAME': '',
        'PATH_INFO': event.get('path', ''),
        'QUERY_STRING': event.get('queryStringParameters', ''),
        'SERVER_NAME': event.get('headers', {}).get('host', ''),
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': '',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers to environ
    for key, value in event.get('headers', {}).items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

    # Call Flask app
    response = flask_app(environ, lambda status, headers, exc_info=None: None)

    # Convert Flask response to Netlify response
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }
''')
    
    # Create .env file
    with open('build/.env', 'w') as f:
        f.write('''FLASK_APP=api/app.py
FLASK_ENV=production
SECRET_KEY=your_production_secret_key
PYTHONPATH=/opt/python
''')
    
    # Create netlify.toml if it doesn't exist
    if not os.path.exists('netlify.toml'):
        with open('netlify.toml', 'w') as f:
            f.write('''[build]
  command = "pip install -r requirements.txt && python build.py"
  publish = "build"
  functions = "functions"

[build.environment]
  PYTHON_VERSION = "3.9"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[functions]
  directory = "functions"
  node_bundler = "esbuild"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
''')

if __name__ == '__main__':
    create_build_directory()
    print("Build directory created successfully!") 