from flask import Flask
from views import api

# initialize the FLASK app
app = Flask('Ollama Server')

# register the api blueprint
app.register_blueprint(blueprint=api, url_prefix='/api')

def main() -> None:
    return

if __name__ == "__main__":

    main()
    app.run(port=9100,debug=True)
