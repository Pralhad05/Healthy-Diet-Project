from flask import Flask
from appmy import app as flask_app

def handler(event, context):
    return flask_app(event, context) 