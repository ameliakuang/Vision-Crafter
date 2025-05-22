import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from together import Together
from dotenv import load_dotenv

from .logging_configs import setup_logging
from .routes import api_bp


def create_app():
    load_dotenv()
    setup_logging()

    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    app.config.from_mapping(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        TOGETHER_API_KEY=os.getenv("TOGETHER_API_KEY"),
    )
    app.openai_client = OpenAI(api_key=app.config["OPENAI_API_KEY"])
    app.together_client = Together(api_key=app.config["TOGETHER_API_KEY"])

    app.temp_db = {}

    app.register_blueprint(api_bp, url_prefix="/api")
    return app
