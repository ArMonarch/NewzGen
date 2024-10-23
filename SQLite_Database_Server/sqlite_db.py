import sqlite3

class Sqlite3:
    def __init__(self):
        self.app = None
        self.connection = None
    
    def init_db(self, app):
        self.app = app
        self.connect()
    
    def connect(self):
        self.connection = sqlite3.connect("/home/frenzfries/dev/NewzGen_News-Scrapper-Summarization/SQLite_Database_Server/data/NewzData.db")
        return self.connection
    
    def get_db(self):
        if not self.connection:
            return self.connect()
        else:
            return self.connection
        
    def __del__(self):
        if self.connection:
            self.connection.close()