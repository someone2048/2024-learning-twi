import json
from datetime import datetime
from pandas import DataFrame

from anki_flashcards.create_fashcards import create_flashcards
from common.drive_upload import gdrive_update_file, gdrive_authenticate
from common.read_db_notion import fetch_notion_db
from common.enhace_notion_db import verify_database


def update_everything():
    # # # # FETCHING DF & FILTERING OUT ROWS WITH ISSUES # # # #
    with open("files/secrets/notion_secrets.json") as f:
        j = json.load(f)
        notion_token = j["notion_token"]
        notion_db = j["notion_db"]
    df = fetch_notion_db(notion_db, notion_token)
    issue_log = verify_database(df)
    if len(issue_log) > 0:
        print("The following rows will be skipped:")
        for row, issue_desc in sorted(list(issue_log.items()), key=lambda x: x[0]):
            print(f"{row:4d}: {issue_desc}")

        # ignoring rows with issues
        df.drop(df.index[list(issue_log.keys())], inplace=True)
        df.reset_index(drop=True, inplace=True)
        assert len(verify_database(df)) == 0

    # TODO fix obvious errors
    # TODO add new words to database

    # # # # CREATING ANKI FLASHCARDS & UPLOADING THEM # # # #
    create_flashcards(df, "files/flashcards.apkg")
    gdrive = gdrive_authenticate("files/secrets/gdrive_secrets.json",
                                 "files/secrets/client_secrets.json")
    gdrive_update_file(gdrive,
                       "1nSz20dpnDIetmNATmfs-es25ZA8N3xTx",
                       "files/flashcards.apkg",
                       f"flashcards-v{datetime.now().strftime('%Y%m%d')}.apkg")


if __name__ == '__main__':
    update_everything()

