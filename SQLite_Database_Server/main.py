import sqlite3
from flask import Flask
from SQLCommands import CREATE_ARTICLE_TABLE, CREATE_ARTICLE_SUMMARY_TABLE
from config import DATABASE_PATH
from views import api

app = Flask("Sqlite3 Database Server")

# register the Blueprint
app.register_blueprint(blueprint=api, url_prefix='/api')

def main() -> None:

    try:
        connect = sqlite3.connect(DATABASE_PATH)
        cursor = connect.cursor()

        cursor.execute(CREATE_ARTICLE_TABLE)
        cursor.execute(CREATE_ARTICLE_SUMMARY_TABLE)

        cursor.close()
        connect.close()
    
    except sqlite3.Error as e:
        print("An error occured during Database Connection or Table Creation", str(e))
    
    return

if __name__ == "__main__":

    main()
    app.run(port=9200,debug=True)