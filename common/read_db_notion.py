import json
import pandas as pd
from notion_client import Client
from datetime import datetime

from common.utils import preprocess_twi


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
                match field['type']:
                    case 'rich_text' | 'title':
                        if field[field['type']]:
                            value = ''.join([rt['plain_text'] for rt in field[field['type']]])
                        else:
                            value = ""
                    case 'select':
                        if field['select']:
                            value = field['select']['name']
                        else:
                            value = ""
                    case 'relation':
                        value = [r['id'] for r in field['relation']]
                    case 'checkbox':
                        value = field['checkbox']
                    case 'last_edited_time':
                        value = datetime.fromisoformat(field['last_edited_time'][:-1])
                    case 'files':
                        if field['files']:
                            value = ""  # TODO
                            # raise NotImplementedError("Downloading files is not yet implemented")
                        else:
                            value = []
                    case 'multi_select':
                        value = field['multi_select']
                        if len(value) > 0:
                            value = [t['name'] for t in field['multi_select']]
                    case _:
                        raise TypeError("Unexpected field type")
                row.append(value)
            database.append(row)
        if not db_query['has_more']:
            break
        db_query = notion.databases.query(db_url, start_cursor=db_query['next_cursor'])

    database = preprocess_twi(database)
    return pd.DataFrame(database[1:], columns=database[0])


if __name__ == "__main__":
    with open("../files/secrets/notion_secrets.json") as f:
        j = json.load(f)
        notion_token = j["notion_token"]
        notion_db = j["notion_db"]
        
    df = fetch_notion_db(notion_db, notion_token)
    print(f"Retrieved {len(df)} rows!\n")
    print(df)

