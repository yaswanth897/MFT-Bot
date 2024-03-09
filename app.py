from flask import Flask, request, jsonify, session, json
import random
from flask_session import Session  # Import the Session extension
from flask_cors import CORS  # Import the CORS extension

app = Flask(__name__, static_folder='static')

# Enable CORS for all domains on all routes
CORS(app, resources={r"/*": {"origins": "https://sites.google.com/ironmountain.com/mftchatbot/home"}})

app.secret_key = 'your_secret_key'

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
prev_category, check, current_key, prev_message = '','','',''
count = ['','']
max=0
sftp_dictionary = {'server':'','client':'','lob':'','BS_Justify':'','owner':'','volume':'','data-arrive':'','accounts':'','username':'','path':'','permissions':'','email':''}
servers = ['frankfurt','uk','europe','south africa','uae','dubai','brazil','sftp.ironmoutnain.de','sftp.ironmoutnain.eu','france','USA','NON-DMS']



def get_category(user_input):
    greetings_keyworks = ['hello','hi','morning','afternoon','evening','night','good']
    praising_keyworks = ['thank you','amazing','fantastic','incredible','wonderful','brilliant','phenomenal','outstanding','excellent','marvelous','exceptional','superb','magnificent','stellar','extraordinary','impressive','remarkable','exquisite','splendid','admirable','fabulous','divine','unbelievable','peerless','unparalleled','supreme','matchless','transcendent','preeminent','incomparable','unequaled']
    questioning_keyworks = ['really','is it','how']
    SFTP_creation_keyworks =['create','new','need','add', 'creating', 'want', 'require', 'request']
    account_type = ['sftp','ftp','globalscape']
    sftp_enable = ['enable','activte']
    confused_keyworks=['sorry','do not know','not']
    
    if ((any(keyword in user_input for keyword in SFTP_creation_keyworks)) and (any(keyword in user_input for keyword in account_type))):
        return 'sftpcreation'
    if ((any(keyword in user_input for keyword in sftp_enable)) and (any(keyword in user_input for keyword in account_type))):
        return 'sftpenable'
    elif any(keyword in user_input for keyword in praising_keyworks):
        return 'compliment'
    elif any(keyword in user_input for keyword in questioning_keyworks):
        return 'question'
    elif any(keyword in user_input for keyword in greetings_keyworks):
        return 'greeting'
    else:
        return 'unknown'

def chatbot_response(message):
    global count, current_key, sftp_dictionary, servers, check, prev_message
    response = ''
    prev_category = session.get('prev_category', '')
    confirm = ['yes','correct','true','please','confirm']
    compliment_responses = ["Thank you, I really appreciate your kind words!", "That's very kind of you to say. Thank you!", "I'm glad you think so, thank you!", "That means a lot to me. Thank you!", "I'm really flattered. Thank you!", "Wow, thank you so much!", "You just made my day! Thank you!", "It's nice to hear that, thank you!", "Thank you, you're too kind!", "I appreciate the compliment, thank you!"]
    
    if count[0] == "sftp":
        if check == 'yes':
            if message.lower() in confirm:
                sftp_dictionary[current_key] = prev_message
            else:
                pass
            check = "no"
        else:
            if current_key == 'server':
                if message.lower() in servers:
                    sftp_dictionary[current_key] = message
                else:
                    response = "Please provide correct server name"
            elif current_key == 'path':
                if message.lower() == "default":
                    sftp_dictionary[current_key] = message
                else:
                    prev_message = message
                    response = "Do you want to the account to be mapped to <b>"+message+"<b>?"
                    check = "yes"
                    return response
            else:
                sftp_dictionary[current_key] = message
    else:
        current_key = ""


    category = get_category(message.lower())
    
    if prev_category == 'compliment' and category == "question":
        response = "Yes! It mean a lot to me. How can I assist you further?"
    elif prev_category =='question' and category == '':
        response = ""
    elif (prev_category == 'request' or prev_category =='question') and category == 'compliment':
        response = random.choice(compliment_responses)
    elif category == 'compliment':
        response = random.choice(compliment_responses)
    elif category == 'question':
        response = "Yes, i can help you with ticket creatin process"
    elif category == 'sftpcreation':
        count = ['sftp','create']
        response = 'Ok. You need a SFTP account.<br>'
    elif category == 'sftpenable':
        count = ['sftp','enable']
        response = 'Ok. You need to activate SFTP account.'
    elif category == 'greeting':
        response = "Hello. How can i assist you today?"
        return response

    if count[0] == 'sftp':
        sftp_expected = ['client','lob','BS_Justify','owner','volume','data-arrive','server','accounts','username','path','permissions','email']
        for key in sftp_expected:
            if key not in sftp_dictionary or sftp_dictionary[key] == '':
                current_key = key
                if key =='client':
                    response = response+"<br>For which client or customer the account need to be created"
                    return response
                elif key =='lob':
                    response = response+"<br>For which Line of Business this request would belong to?"
                    return response
                elif key =='BS_Justify':
                    response = response+"<br>What would be the Business justification?"
                    return response
                elif key =='owner':
                    response = response+"<br>Who would be the owner of the FTP account?"
                    return response
                elif key =='volume':
                    response = response+"<br>What would be the per day volume?"
                    return response
                elif key =='data-arrive':
                    response = response+"<br>How the data will be uploaded to the SFTP?"
                    return response
                elif key == 'server':
                    response = response+"<br>Please provide the country name or the hostname or weburl where the account need to be created"
                    return response
                elif key == 'accounts':
                    response = response+"<br>How many accounts need to be created"
                    return response
                elif key == 'username':
                    response = response+"<br>Please provide the username of the account need to be created"
                    return response
                elif key == 'path':
                    response = response+"<br>If the account need to be mapped to any specific path/folder provide the path/folder name or type <b>default<b>"
                    return response
                elif key == 'permissions':
                    response = response+"<br>Please provide the permissions needed for the account."
                    return response
                elif key == 'email':
                    response = response+"<br>Please provide the email id to which the credentials need to be sent"
                    return response
                break
        response = json.dumps(sftp_dictionary) + "Thanks for the info. I will create a ticket and MFT Team will get back to you."
        count = ['','']
    elif count[0] == "iod":
        response = "we will look into it"
    else:
        response = "Sorry. I cannot assist you with this.<br><br>Currently i am in development phase."


    session['prev_category'] = category
    return response


@app.route('/validate', methods=['POST'])
def validate():
    user_input = request.json['message']
    # Perform validation on user_input
    isValid = True  # This should be the result of your validation logic
    response = "Your input was valid!"  # Customize based on validation
    return jsonify({'isValid': isValid, 'response': response})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    response = chatbot_response(user_input)
    return jsonify({'message': response})

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/initial-message', methods=['GET'])
def get_initial_message():
    message = "Hi, I am a virtual assistant created to help you with the ticket creation process."
    return jsonify(message=message)

if __name__ == "__main__":
    # Adjust the host and debug mode according to your deployment and testing needs
    app.run(host='0.0.0.0', debug=True)