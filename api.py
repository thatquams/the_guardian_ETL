import requests
import pandas as pd
import psycopg2
from datetime import datetime 

API_KEY = "b76da5b0-6b4d-4862-8349-2639101a1847"

def ApiConnection(endPoint, q_tag):
    
    """
    Connects to The Guardian Open Platform API and retrieves article data for a given endpoint and keyword/tag.

    Parameters
    ----------
    endPoint : str
        The API endpoint to query (e.g., "search").
    q_tag : str
        The keyword or tag to filter articles.

    Returns
    -------
    dict
        A dictionary with keys representing article metadata fields
        ('article_id', 'section_id', 'article_url', 'section_name', 'Headlines', 'publication date'),
        each mapped to a list of corresponding values.

    Notes
    -----
    - Fetches up to `num_of_pages` pages of results (default 500).
    - Handles HTTP request exceptions gracefully.
    - Requires a valid global `API_KEY`.
    """
    current_page = 1
    num_of_pages = 500

    allRecords = {
        "article_id": [], "section_id": [], "article_url": [],
        "section_name": [], "Headlines": [], "publication date": []
    }

    try:
        while current_page <= num_of_pages:
            
            apiRequest = requests.get(
                f"https://content.guardianapis.com/{endPoint}?show-tags={q_tag}&page={current_page}&q={q_tag}&api-key={API_KEY}"
            )

            if apiRequest.status_code == 200:
                # Optional: Uncomment to fetch total pages dynamically
                # num_of_pages = apiRequest.json()['response']["pages"]

                requestResults = apiRequest.json()['response']['results']

                for record in requestResults:
                    allRecords['article_id'].append(record['id'])
                    allRecords['section_id'].append(record['sectionId'])
                    allRecords['article_url'].append(record['webUrl'])
                    allRecords['section_name'].append(record['sectionName'])
                    allRecords['Headlines'].append(record['webTitle'])
                    allRecords['publication date'].append(record['webPublicationDate'])

                print(f"Page : {current_page}")
                current_page += 1
    except requests.exceptions.RequestException as err:
        print(f"Can't Connect to This API {apiRequest} : \n {err}")

    # print(f"\nTHE '{q_tag.upper()}' KEYWORD APPEARED {len(allRecords['article_id'])} TIMES.\n")
    return allRecords


def convertToDataframe():
    """
    Retrieves articles related to the keyword 'nigeria' using the Guardian API and converts them into a pandas DataFrame.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing columns: article_id, section_id, article_url, section_name, Headlines, publication date (as datetime).

    Notes
    -----
    - Internally calls ApiConnection with hardcoded keyword 'nigeria'.
    - Converts publication dates to pandas datetime format.
    - Can be extended for other keywords or output formats.
    """
    
    data = ApiConnection("search", "nigeria")
    df = pd.DataFrame(data)
    
    df["publication date"] = pd.to_datetime(df["publication date"], errors="coerce")
    # df.to_csv("THE_GUARDIAN_API.csv")
    return df

def connectToPostgres(data, db_host, dbname, db_user, db_password, db_port):
    
    """
    Connects to a PostgreSQL database, creates a table if it doesn't exist,
    and inserts article metadata from a pandas DataFrame into the table.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing article data to be inserted.
    db_host : str
        Hostname or IP address of the PostgreSQL server.
    dbname : str
        Name of the PostgreSQL database.
    db_user : str
        Username for database authentication.
    db_password : str
        Password for database authentication.
    db_port : int
        Port number on which PostgreSQL server is listening.

    Returns
    -------
    pandas.DataFrame
        The same input DataFrame is returned after insertion for further use if needed.

    Raises
    ------
    psycopg2.OperationalError
        If the database connection fails.
    Exception
        For other errors during database operations.

    Notes
    -----
    - Uses parameterized queries to prevent SQL injection.
    - Uses context managers to handle connection and cursor lifecycle.
    - Commits changes automatically when context manager exits.
    """
    try:
        connection = psycopg2.connect(host = db_host, dbname = dbname, user = db_user, password = db_password, port = db_port)
        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                            CREATE TABLE IF NOT EXISTS the_guardians_data (
                                    article_id VARCHAR(500) NOT NULL,
                                    section_id VARCHAR(500) NOT NULL,
                                    article_url VARCHAR(500) NOT NULL,
                                    section_name VARCHAR(500) NOT NULL,
                                    Headlines VARCHAR(1000) NOT NULL,
                                    publication_date TIMESTAMP
                    )""")
                

                for _, row in data.iterrows():
                    cursor.execute("""
                                INSERT INTO the_guardians_data (article_id, section_id, article_url, section_name, Headlines, publication_date) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,  
                                (row['article_id'], 
                                row['section_id'], 
                                row['article_url'], 
                                row['section_name'], 
                                row['Headlines'], 
                                row['publication date'])
                                )
        
        
            
    except psycopg2.OperationalError as err:
        print(f"Cannot Connect to Database : \n {err}")
        
    except Exception as err:
        print(f"An Error Occured {err}")
        
    finally:
        return data
    #     connection.close()
        
start_time = datetime.now()
result = connectToPostgres(convertToDataframe(), db_host="127.0.0.1", db_user="postgres", db_password="Lifeofnvestor01", dbname="test", db_port=5433)
end_time = datetime.now()

print(result)

print(f"It took {end_time - start_time} execution time")
