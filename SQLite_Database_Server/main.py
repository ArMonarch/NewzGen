import sqlite3
from flask import Flask
from query import CREATE_NEWS_TABLE, CREATE_NEWS_SUMMARY_TABLE

app = Flask("Sqlite3 Database Server")

def main() -> None:
    connect = sqlite3.connect("./data/NewzData.db")
    cursor = connect.cursor()

    try:
        cursor.execute(CREATE_NEWS_TABLE)
        cursor.execute(CREATE_NEWS_SUMMARY_TABLE)
    
    except:
        print("An error occured during Table Creation")
    
    return

if __name__ == "__main__":

    main()
    # app.run(port='9000',debug=True)