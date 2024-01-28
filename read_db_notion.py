from notion_client import Client


NOTION_DB = "e51c23449ac34ecaa9f6e2702dc2524f"
with open("secrets.txt") as f:
    NOTION_TOKEN = f.read().strip()


def fetch_notion_db(db_url, access_token):
    notion = Client(auth=access_token)
    db_query = notion.databases.query(db_url)

    header = ["id"] + list(db_query['results'][0]['properties'].keys())
    database = [header]
    assert db_query['has_more'] == False
    for notion_row in db_query['results'][1:]:
        row = [notion_row['id']]
        for column in header[1:]:
            field = notion_row['properties'][column]
            if field['type'] in ('rich_text', 'title'):
                value = ''.join([rt['plain_text'] for rt in field[field['type']]])
            elif field['type'] == 'select':
                value = field['select']['name']
            elif field['type'] == 'relation':
                value = [r['id'] for r in field['relation']]
            else:
                raise TypeError("Unexpected field type")
            row.append(value)
        database.append(row)
    return database


if __name__ == "__main__":
    db = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    for r in db:
        print(",".join([str(i) for i in r]))
