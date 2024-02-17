import json
import os
import pandas as pd

from anki_flashcards.create_fashcards import create_flashcards
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

    # # # # SAVING LATEST CLEAN DATAFRAME # # # #
    if os.path.exists("files/twi_vocabulary_df_latest.pkl") and \
            df.equals(pd.read_pickle("files/twi_vocabulary_df_latest.pkl")):
        print("df identical to last run... quitting...")
        return
    df.to_pickle(f"files/twi_vocabulary_df_latest.pkl")

    # TODO fix obvious errors
    # TODO add new audio to database

    # # # # CREATING ANKI FLASHCARDS & UPLOADING THEM # # # #
    create_flashcards(df, "files/public/flashcards.apkg")


if __name__ == '__main__':
    update_everything()

