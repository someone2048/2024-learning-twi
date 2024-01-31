import json
import pandas as pd
from notion_client import Client
from datetime import datetime

from utils import preprocess_twi


with open("notion_secrets.json") as f:
    j = json.load(f)
    NOTION_TOKEN = j["notion_token"]
    NOTION_DB = j["notion_db"]


def fetch_notion_db(db_url, access_token):
    notion = Client(auth=access_token)
    db_query = notion.databases.query(db_url)

    header = ["id"] + list(db_query['results'][0]['properties'].keys())
    database = [header]
    while True:
        for notion_row in db_query['results']:
            row = [notion_row['id']]
            for column in header[1:]:
                field = notion_row['properties'][column]
                if field['type'] in ('rich_text', 'title'):
                    if not field[field['type']]:
                        value = ""
                    else:
                        value = ''.join([rt['plain_text'] for rt in field[field['type']]])
                elif field['type'] == 'select':
                    if not field['select']:
                        value = ""
                    else:
                        value = field['select']['name']
                elif field['type'] == 'relation':
                    value = [r['id'] for r in field['relation']]
                elif field['type'] == 'checkbox':
                    value = field['checkbox']
                elif field['type'] == 'last_edited_time':
                    value = datetime.fromisoformat(field['last_edited_time'][:-1])
                else:
                    raise TypeError("Unexpected field type")
                row.append(value)
            database.append(row)
        if not db_query['has_more']:
            break
        db_query = notion.databases.query(db_url, start_cursor=db_query['next_cursor'])

    database = preprocess_twi(database)
    return pd.DataFrame(database[1:], columns=database[0])


if __name__ == "__main__":
    df = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    print(f"Retrieved {len(df)} rows!\n")
    print(df)

