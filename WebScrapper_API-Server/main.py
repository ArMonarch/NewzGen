from flask import Flask
from views import api

app = Flask('News Scrapper')

# register the blueprint
app.register_blueprint(blueprint=api, url_prefix='/api')

def main() -> None:
    return

if __name__ == "__main__":
    main()
    app.run(port='9100',debug=True)