import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, authors, pub_year, img_url, review_count, average_score in reader:
        db.execute("INSERT INTO books(isbn, title, author, pub_year, img_url, average_score, review_count) VALUES(:isbn, :title, :author, :pub_year, :img_url, :average_score, :review_count)",
            {"isbn": isbn, "title": title, "author": authors, "pub_year": pub_year, "img_url": img_url, "average_score": average_score, "review_count": review_count})
        print(f"Added {isbn}, {title}, {authors}, {pub_year}, {img_url}, {review_count}, {average_score} into Book")
    db.commit()

if __name__ == "__main__" :
    main()
