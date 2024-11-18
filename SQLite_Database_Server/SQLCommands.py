    # Id TEXT NOT NULL, the id obtained from BBC is Text
    # Type TEXT, Value(Article,Blog,News)
    # Authors TEXT, Name of author
    # Title TEXT, Title of the article
    # Topics TEXT, Which topic does this belongs to
    # Body TEXT, the body of the news article
    # PublishedDate TEXT, date published
    # Source TEXT, website the news is scrapped from
    # Summarized? BOOL is the news summarized

CREATE_ARTICLE_TABLE = '''
    CREATE TABLE IF NOT EXISTS Articles (
        Id INTEGER PRIMARY KEY,
        Type TEXT,
        Authors TEXT,
        Title TEXT,
        Topics TEXT,
        Body TEXT,
        PublishedDate TEXT,
        Source TEXT,
        Url TEXT,
        Summarized_Status TEXT
    );
'''

CREATE_ARTICLE_SUMMARY_TABLE = '''
    CREATE TABLE IF NOT EXISTS Articlez_Summaries (
    Id INTEGER PRIMARY KEY,
    Article_Id TEXT NOT NULL,
    LLM_Used TEXT NOT NULL,
    Generated_Summary TEXT NOT NULL,
    
    FOREIGN KEY (Article_Id)
        REFERENCES Article (Id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    );
'''

INSERT_ARTICLE_WITH_ID = '''
    INSERT INTO Articles (id, Type, Authors, Title, Topics, Body, PublishedDate, Source, Summarized_Status)
    VALUES (:id, :type, :authors, :title, :topics, :body, :publisheddate, :source, :summarized_status);
'''

INSERT_ARTICLE_WITHOUT_ID = '''
    INSERT INTO Articles (Type, Authors, Title, Topics, Body, PublishedDate, Source, Url, Summarized_Status)
    VALUES (:type, :authors, :title, :topics, :body, :publisheddate, :source, :url, :summarized_status);
'''

GET_ARTICLE_WITH_ID = '''
    SELECT Id, Type, Authors, Title, Topics, Body, PublishedDate, Source, Url, Summarized_Status
    FROM Articles
    WHERE Id = :article_id;
'''

GET_ARTICLE_WITH_TITLE = '''
    SELECT Id, Type, Authors, Title, Topics, Body, PublishedDate, Source , Url, Summarized_Status
    FROM Articles
    WHERE Title = :title;
'''

INSERT_SUMMARY_WITH_ID = '''
    INSERT INTO Articlez_Summaries (Id, Article_Id, LLM_Used, Generated_Summary)
    VALUES (:id, :article_id, :llm_used, :generaed_summary);
'''

INSERT_SUMMARY_WITHOUT_ID = '''
    INSERT INTO Articlez_Summaries (Article_Id, LLM_Used, Generated_Summary)
    VALUES (:article_id, :llm_used, :generaed_summary);
'''

GET_SUMMARY_WITH_ID = '''
    SELECT Id, Article_Id, LLM_Used, Generated_Summary
    FROM Articlez_Summaries
    WHERE Id = :summary_id;
'''

GET_SUMMARY_WITH_ARTICLEID = '''
    SELECT Id, Article_Id, LLM_Used, Generated_Summary
    FROM Articlez_Summaries
    WHERE Article_Id = :article_id;
'''