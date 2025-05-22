from flask import Flask
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