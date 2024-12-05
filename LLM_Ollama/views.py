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
    try:
        if request.method != 'POST':
            raise Exception('METHOD ERROR: route only supports POST method')
        
        # POST data format:
        # model: llama3.1 and llama3.2
        # article: {id, type, topic, title, body}
        
    except Exception as e:
        return dict({'error': {'status_code': 401, 'message': f'{e}'}}, 401)

    finally:
        pass

    DATA : dict = {"model":"llama3.1", "prompt":"Hey Llama3.2!", "stream": False}
    requested = requests.post('http://localhost:11434/api/generate', json=DATA)
    return (f'{requested.text}',201)

@api.route('gemini/generate/summary', methods=['POST'])
def geminiGenerate_Summary():
    return ('Feature Unavailable',201)

@api.route('mistral/generate/summary', methods=['POST'])
def mistralGenerate_Summary():
    return ('Feature Unavailable',201)