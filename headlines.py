from flask import Flask
import feedparser

app = Flask(__name__)

RSS_FEED = {'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'Fox News': 'http://feeds.foxnews.com/foxnews/latest',
            'IOL': 'http://rss.iol.io/iol/news'}


@app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc"):
    feed = feedparser.parse(RSS_FEED[publication])

    html = ''
    for article in feed['entries']:
        html += """
        <b>{0}</b> <br/>
        <i>{1}</i> <br />
        <p>{2}</p> <br/>""".format(article.get("title"), article.get("published"), article.get("summary"))
    shell = """<html>
    <body>
        <h1> {0} Headlines </h1>
    {1}
    </body>
    </html>""".format(publication.upper(), html)
    return shell


if __name__ == '__main__':
    app.run(port=5000, debug=True)
