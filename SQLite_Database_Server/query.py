CREATE_NEWS_TABLE = '''
    CREATE TABLE IF NOT EXISTS News (
        Id TEXT NOT NULL PRIMARY KEY,
        Type TEXT,
        Authors TEXT,
        Title TEXT,
        Topics TEXT,
        Discription TEXT,
        PublishedDate TEXT,
        Source TEXT
    );
'''

CREATE_NEWS_SUMMARY_TABLE = '''
    CREATE TABLE IF NOT EXISTS Newz_Summaries (
    Id INTEGER,
    News_Id TEXT NOT NULL,
    LLM_Used TEXT,
    Generated_Summary TEXT,
    PRIMARY KEY (News_Id),
    FOREIGN KEY (News_Id)
        REFERENCES News (Id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    );
'''