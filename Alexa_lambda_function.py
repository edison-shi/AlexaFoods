from __future__ import print_function
from random import choice as ran
import urllib2
import json


GET_URL = "http://chefalexa-api-dev.us-east-1.elasticbeanstalk.com/harambe/extract_ingredient?recipe="

#------------------Unique Responses----------------------------------------------
OPEN = [
	"Chef Alexa is in the house!",
	"Hungry?",
	"It's cooking time!",
	"Who's ready for some quality cooking?"
]

QUESTION = [
	"What would you like to make?",
	"What do you fancy making?",
	"What are you thinking of making?"
]






# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():

    session_attributes = {'food' : 'water', 'ingredients' : 'none'}
    card_title = "Welcome"
    speech_output = ' '.join([ran(OPEN),ran(QUESTION)])
    reprompt_text = "Answer me!"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "I guess you weren't worthy of being a chef anyways."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_recipe(session):
    url = GET_URL + session['attributes']['food']
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    data = json.load(response)
    response.close()
    session['attributes']['ingredients'] = data['ingredients']
    return "Ingredients:" + data['ingredients'] + ". Instructions:" + data['instructions']

def set_Food(foodName, session):
    wholeName = foodName.split(' ')
    underScore = ''
    for i in range(len(wholeName)):
        underScore = underScore + wholeName[i] + '_'
	session['attributes']['food'] = underScore[:-1]

def decide_Specific(intent, session):
	card_title = intent['name']
	session_attributes=session['attributes']
	should_end_session = False
	theChoice = intent['slots']['Item']['value']

	if theChoice in ["meat","vegetable","soup","chicken","beef","pork","fish","salad","pizza"]:
		speech_output = theChoice + " sounds too vague. Could you please be more specific?"
		reprompt_text = "You suck."
	elif theChoice in ["yes","yeah","correct","that's right","yup"]:
		speech_output = get_recipe(session)
		reprompt_text = "You suck."
		should_end_session = True
	elif theChoice in ["no","nah","nope","no I didn't","that's wrong","wrong","that's not right","that is wrong","incorrect"]:
		speech_output = "Please say it more clearly."
		reprompt_text = "You suck."
	else:
		set_Food(theChoice,session)
		speech_output = "Did you say you want to make " + theChoice + "?"
		reprompt_text = "Try again later."
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

# Starting--------------------------------------------------------------------------

def on_session_started(session_started_request, session):

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()

#Response building-----------------------------------------------------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }



#Intent----------------------------------------------------------------------------

def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    if intent_name == "Decision":
    	return decide_Specific(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
    	raise ValueError("Invalid intent")


#Session End---------------------------------------------------------------------------------

def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
# --------------- Main handler ------------------

def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
