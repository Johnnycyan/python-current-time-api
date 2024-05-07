from flask import Flask
from flask import request
from markupsafe import escape
from getTime import main as getTime
import html

app = Flask(__name__)

@app.route('/time')
def application():
    try:
        debug = request.args.get('debug')
        debug = debug.strip()
        debug = html.unescape(debug)
        if debug.lower() == "true":
            debug = True
        else:
            debug = False
    except:
        debug = False
    try:
        fallback = request.args.get('fallback')
        fallback = fallback.strip()
        fallback = html.unescape(fallback)
    except:
        return "Error: No fallback specified."
    try:
        location = request.args.get('location')
        location = location.strip()
        location = html.unescape(location)
    except:
        return "Error: No location specified."
    if location == None:
        location = fallback
    elif location == "":
        location = fallback
    elif "!" in location:
        location = fallback
    elif "@" in location:
        location = fallback
    try:
        result = getTime(location, debug)
        return result
    except:
            return "Error: Invalid location."

if __name__ == "__main__":
    app.run()