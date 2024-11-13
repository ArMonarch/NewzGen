import sqlite3
# from extension import sqlite3 as sq
from flask import Flask
from SQLCommands import CREATE_ARTICLE_TABLE, CREATE_ARTICLE_SUMMARY_TABLE
from views import api

# import views

app = Flask("Sqlite3 Database Server")
# sq.init_db(app)

# register the Blueprint
app.register_blueprint(api, url_prefix='/api')

def main() -> None:

    try:
        connect = sqlite3.connect("/home/frenzfries/dev/NewzGen_News-Scrapper-Summarization/SQLite_Database_Server/data/NewzData.db")
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
    app.run(port='9200',debug=True)