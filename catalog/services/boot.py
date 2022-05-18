import logging

from flask import Flask
from dotenv import load_dotenv
load_dotenv()

from .api import api

app = Flask(__name__)


# Join the api module (and loaded services therein) to the wsgi app
logging.info("Initializing...")
api.init_app(app)

if __name__ == '__main__':
    print(app.url_map)
    # To use super fast bjoern
    #import bjoern
    #bjoern.run(app, "0.0.0.0", 5000)
    app.run(debug=True)