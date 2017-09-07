from flask import Flask, render_template, request, make_response
import feedparser
import json
import urllib
import datetime
# import urllib2

app = Flask(__name__)

RSS_FEED = {'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://rss.iol.io/iol/news'}

DEFAULTS = {'publication': 'bbc', 'city': 'London,UK','currency_from':'GBP','currency_to':'USD'}

CURRENCY_URL = 'https://openexchangerates.org/api/latest.json?app_id=df17be3edc88429cab9c9d648b7ee3d3'

def get_weather(query):
    api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=7922aee86e43451effb6e0e1faab5015'
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read().decode('utf8')
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"], "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],'country':parsed['sys']['country']}
    return weather

def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read().decode('utf8')
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate/frm_rate

def get_currency_list():
    all_currency = urllib.request.urlopen(CURRENCY_URL).read().decode('utf8')
    parsed = json.loads(all_currency).get('rates')
    return parsed

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)

    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


def get_news(publication):
    return feedparser.parse(RSS_FEED[publication.lower()])

@app.route("/")
def home():
    #get headlines, based on user input of default
    publication = get_value_with_fallback("publication")
    feed = get_news(publication)

    #get custom weather based on user input or defaults
    city = get_value_with_fallback("city")
    weather = get_weather(city)

    # get custom currency based on user input or defaults
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate = get_rate(currency_from,currency_to)
    currency_list = sorted(list(get_currency_list()))


    response =  make_response(render_template("home.html", articles=feed['entries'],
                                              publication=publication, weather=weather,
                                              currency_from = currency_from,currency_to = currency_to,
                                              rate=rate,currency_list=sorted(currency_list)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication",publication,expires=expires)
    response.set_cookie("city",city,expires=expires)
    response.set_cookie("currency_from",currency_from,expires=expires)
    response.set_cookie("currency_to",currency_to,expires=expires)
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
