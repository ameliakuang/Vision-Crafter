import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from together import Together
from dotenv import load_dotenv

from backend.prompt_generator import PromptGenerator
from backend.style_extraction_agent import StyleExtractionAgent
from backend.prompt_generation_pipline import PromptGenerationPipeline
from backend.logging_configs import setup_logging
from backend.routes import api_bp


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

     # --- Initialize pipeline components and attach to app ---
    app.style_agent = StyleExtractionAgent(app.openai_client)
    app.prompt_generator = PromptGenerator(app.openai_client) # PromptGenerator also needs openai_client
    app.pipeline = PromptGenerationPipeline(
        app.prompt_generator, # Pass the initialized generator
        app.style_agent     # Pass the initialized style agent
    )

    app.temp_db = {}

    app.register_blueprint(api_bp, url_prefix="/api")
    return app
