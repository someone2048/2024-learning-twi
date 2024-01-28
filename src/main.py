from read_db_notion import NOTION_DB, NOTION_TOKEN, fetch_notion_db
from create_fashcards import create_flashcards
from utils import preprocess_twi

if __name__ == '__main__':
    db = fetch_notion_db(NOTION_DB, NOTION_TOKEN)
    db = preprocess_twi(db)
    create_flashcards(db, "../flashcards.apkg")
