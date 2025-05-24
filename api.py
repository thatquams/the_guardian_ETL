import requests
import pandas as pd
import psycopg2
from datetime import datetime 

API_KEY = "b76da5b0-6b4d-4862-8349-2639101a1847"

def ApiConnection(endPoint, q_tag):
    """
    Connects to The Guardian Open Platform API and retrieves article data related to a specific keyword/tag.

    Parameters
    ----------
    endPoint : str
        The endpoint to query (e.g., "search").
    q_tag : str
        The keyword or tag to search for in the API query.

    Returns
    -------
    dict
        A dictionary containing lists of article metadata fields such as article ID, section ID, 
        URL, section name, headline, and publication date.
    
    Notes
    -----
    - Currently set to retrieve only the first 2 pages of results. To fetch more pages, modify `num_of_pages`
      or uncomment the line that sets it dynamically from the API response.
    - Requires a valid `API_KEY` to be defined in the global scope.
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
    Retrieves article data related to the keyword 'nigeria' from The Guardian API and converts it to a DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing article metadata such as ID, section, URL, headline, and publication date.
    
    Notes
    -----
    - Calls the `ApiConnection()` function with a hardcoded keyword ('nigeria').
    - Can be extended to allow user-defined keywords or export to CSV.
    """
    data = ApiConnection("search", "nigeria")
    df = pd.DataFrame(data)
    
    df["publication date"] = pd.to_datetime(df["publication date"], errors="coerce")
    # df.to_csv("THE_GUARDIAN_API.csv")
    return df

def connectToPostgres(data, db_host, dbname, db_user, db_password, db_port):
    
    
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
