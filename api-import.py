import requests as req
import json, xmltodict, csv

def xmltoJson(xml):
    jsonString = json.dumps(xmltodict.parse(xml), indent=4)
    return json.loads(jsonString)

def extrachData(data):
    isbn = data["GoodreadsResponse"]["book"]["isbn"]
    title = data["GoodreadsResponse"]["book"]["title"]
    pub_year = data["GoodreadsResponse"]["book"]["publication_year"]
    img_url = data["GoodreadsResponse"]["book"]["image_url"]
    reviews_count = data["GoodreadsResponse"]["book"]["work"]["reviews_count"]["#text"]
    average_rating = data["GoodreadsResponse"]["book"]["average_rating"]

    if type(data["GoodreadsResponse"]["book"]["authors"]["author"]) == list:
        authors = ''
        for i, obj in enumerate(data["GoodreadsResponse"]["book"]["authors"]["author"]):
            authors += data["GoodreadsResponse"]["book"]["authors"]["author"][i]["name"] + ", "
        # Git rid of the last comma
        authors = authors[:-2]
    else:
        authors = data["GoodreadsResponse"]["book"]["authors"]["author"]["name"]

    return isbn, title, authors, pub_year, img_url, reviews_count, average_rating

def csvWrite(isbn, title, authors, pub_year, img_url, reviews_count, average_rating):
    with open('book.csv', 'a') as writeFile:
        writer = csv.writer(writeFile)
        row = [[isbn, title, authors, pub_year, img_url, reviews_count, average_rating]]
        writer.writerows(row)


if __name__ == "__main__":
        for i in range(1, 7001):
            try:

                resp = req.get("https://www.goodreads.com/book/show/", params={"id": i, "key": "lonX17oExm7QpKV87R0tw"})
                jsonText = xmltoJson(resp.text)

                isbn, title, authors, pub_year, img_url, reviews_count, average_rating = extrachData(jsonText)
                if len(isbn) != 0 and len(title) != 0 and len(authors) != 0 and len(pub_year) != 0:
                    print(isbn, title, authors, pub_year, img_url, reviews_count,average_rating)
                    csvWrite(isbn, title, authors, pub_year, img_url, reviews_count, average_rating)
            except:
                print("ERROR OCCURED")
