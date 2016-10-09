from __future__ import print_function
from random import choice as ran
import urllib2

GET_URL = "http://api-khe-dev.us-east-1.elasticbeanstalk.com/api/edison?hashtag="

#------------------Unique Responses----------------------------------------------
OPEN = [
	"You have activated feels. Feels bad man.",
    "Activating feels sensor. Feels ready to be feeled.",
    "It seems like you are lacking the feels. Time to get on the feels train.",
    "Hop on the feels train. Choo choo!"
]

QUESTION = [
    "What tweet would you like to feel?",
    "What tweet would you like to start a feels train for?",
    "What tweet would you like to hit with the feels?"
]






# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():

    session_attributes = {}
    card_title = "Welcome"
    speech_output = ' '.join([ran(OPEN),ran(QUESTION)])
    reprompt_text = "Answer me!"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "You do not cancel the feels train. The feels train cancelled you."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_Tweet_Results(tagName):
    url = GET_URL + tagName
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()
    return page

def find_Result(intent, session):
    card_title = intent['name']
    session_attributes={}
    theTweet = intent['slots']['Tag']['value']
    speech_output = get_Tweet_Results(theTweet)
    reprompt_text = "Oopsies"
    should_end_session = True
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
    if intent_name == "Twitter":
    	return find_Result(intent, session)
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