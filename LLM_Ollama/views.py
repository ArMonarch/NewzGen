from flask import Blueprint, request
import requests

# create the blueprint for api
api = Blueprint('api', __name__)

# ----------------------------------------------------------------- #
# Routes / Functionality for the server                             #
# ----------------------------------------------------------------- #


@api.route('/generate/summary', methods=['POST'])
def Generate_Summary():
    return ('Feature Unavailable', 201)

@api.route('llama/generate/summary', methods=['POST'])
def llamaGenerate_Summary():
    return ('Feature Unavailable',201)

@api.route('gemini/generate/summary', methods=['POST'])
def geminiGenerate_Summary():
    return ('Feature Unavailable',201)

@api.route('mistral/generate/summary', methods=['POST'])
def mistralGenerate_Summary():
    return ('Feature Unavailable',201)