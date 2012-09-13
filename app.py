from flask import Flask, render_template, request, make_response, url_for, send_from_directory
import json
import dateutil.parser
import hashlib
import os

app = Flask(__name__)

# Define some greetings for different times of the day in different languages
greetings = {"english" : ["Good morning", "Hello", "Good evening"], 
    "french" : ["Bonjour", "Bonjour", "Bonsoir"], 
    "german" : ["Guten morgen", "Hallo" "Guten abend"], 
    "spanish" : ["Buenos d&#237;as", "Hola", "Buenas noches"], 
    "portuguese" : ["Bom dia", "Ol&#225;", "Boa noite"], 
    "italian" : ["Buongiorno", "ciao", "Buonasera"], 
    "swedish": ["God morgon", "Hall&#229;", "God kv&#228;ll"]}

# Edition                        
@app.route("/edition/")
def edition():

    # Check for required vars
    if not request.args.get('local_delivery_time', False):
        return ("Error: No local_delivery_time was provided", 400)
        
    if not request.args.get('lang', False):
        return ("Error: No lang was provided", 400)
        
    if not request.args.get('name', False):
        return ("No name was provided", 400)

    # Our publication is only delivered on Mondays, so we need to work out if it is a Monday in the subscriber's timezone. 
    date = dateutil.parser.parse(request.args['local_delivery_time'])
    if not date.weekday() == 0:
        return ("It is not a Monday", 406)

    # Extract configuration provided by user through BERG Cloud. These options are defined by the JSON in meta.json.
    language = request.args['lang']
    name = request.args['name']

    # Pick a time of day appropriate greeting
    greeting = greetings[language][0]
    if date.hour >= 12 and date.hour <=17:
        greeting = greetings[language][1]
    if (date.hour > 17 and date.hour <=24) or (date.hour >= 0 and date.hour <= 3):
        greeting = greetings[language][2]

    # Set the etag to be this content. This means the user will not get the same content twice, 
    # but if they reset their subscription (with, say, a different language they will get new content 
    # if they also set their subscription to be in the future)
    response = make_response(render_template('hello_world.html', greeting=greeting))
    response.headers['ETag'] = hashlib.sha224(language+name+date.strftime('%d%m%Y')).hexdigest()
    return response

# Sample publication
@app.route("/sample/")
def sample():

    # Example data 
    language = 'english';
    name = 'Little Printer';
    greeting = "%s, %s" % (greetings[language][0], name)

    # Build response
    response = make_response(render_template('hello_world.html', greeting=greeting))
    response.headers['ETag'] = hashlib.sha224(language+name+date.strftime('%d%m%Y')).hexdigest()
    return response

#Validate config e.g. /validate_config/?config={"lang":"english","name":"Pablo"}
@app.route("/validate_config/")
def validate_config():
    json_response = {'errors': [], 'valid': True}

    # Extract config from POST
    user_settings = json.loads(request.args['config'])
    
    # If the user did choose a language:
    if not user_settings.get('lang', None):
        json_response['valid'] = False
        json_response['errors'].append('Please select a language from the select box.')

    # If the user did not fill in the name option:
    if not user_settings.get('name', None):
        json_response['valid'] = False
        json_response['errors'].append('Please enter your name into the name box.')

    # Is a valid language set?
    if user_settings.get('language', None) in greetings:
        json_response['valid'] = False
        json_response['errors'].append("We couldn't find the language you selected (%s) Please select another" % user_settings['language'])
    
    response = make_response(json.dumps(json_response))
    response.mimetype = 'application/json'
    return response

# Add the routes for the static files so they are at root
@app.route('/meta.json')
def meta_json():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'meta.json', mimetype='application/json')

@app.route('/icon.png')
def icon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'icon.png', mimetype='image/png')
                                       
if __name__ == "__main__":
    app.debug = True    
    app.run()