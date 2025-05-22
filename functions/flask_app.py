from flask import Flask, request
from appmy import app as flask_app

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