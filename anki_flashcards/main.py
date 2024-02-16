from common.read_db_notion import NOTION_DB, NOTION_TOKEN, fetch_notion_db
from create_fashcards import create_flashcards
from common.drive_upload import update_fash_cards_gdrive

if __name__ == '__main__':
    print("fetching notion database")
    df = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    df.to_pickle("twi_vocabulary_df.pkl")
    count = create_flashcards(df, "flashcards.apkg")
    print(f"created {count} flashcards")
    print("uploading flashcards")
    update_fash_cards_gdrive()
    print("done!")
