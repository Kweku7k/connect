
import csv
import datetime
from email.message import EmailMessage
import os
import pprint
import smtplib
from flask import Flask, flash, jsonify,redirect,url_for,render_template,request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
from sqlalchemy.dialects.postgresql import JSONB, JSON
from flask_bcrypt import Bcrypt
from variables import *
from bs4 import BeautifulSoup
import json
from functools import wraps
import jwt
from utils import *

from forms import *
# from flask_login import UserMixin, login_user, logout_user, current_user, LoginManager, login_required

app=Flask(__name__)
app.config['SECRET_KEY'] = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'
app.config['JWT_SECRET_KEY'] = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'


# app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:adumatta@localhost:5432/connect'
# app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:adumatta@database-1.crebgu8kjb7o.eu-north-1.rds.amazonaws.com:5432/connect'
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('CONNECT_DB_URL', 'postgresql://postgres:adumatta@localhost:5432/connect' )

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

cors = CORS(app)

algorithms = ["HS256"]


baseUrl = os.environ.get('CONNECT_BASE_URL', 'https://connect.prestoghana.com')
prestoUrl = os.environ.get('PRESTO_PROD_URL', 'https://prestoghana.com')
server = os.environ.get('SERVER', None)
environment = os.environ.get('ENVIRONEMT', 'DEV')

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

chat_id = os.environ.get('CONNECT_TELGRAM')
telegramToken = os.environ['PRESTO_TELEGRAM_BOT_TOKEN']


def get_current_user():
    # TODO: Convert class into dictionary
    user_found = session.get('current_user', None)
    if user_found is not None:
        user = User.query.get_or_404(user_found)
        if user is not None:
            return user
    return None
     

def reportTelegram():
    pass

def login_user(user):
    print("Logging in :")
    print(user)
    token = jwt.encode({'user':user.id, 'exp':datetime.datetime.now()+datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    session['jwt']=token
    session['current_user'] = user.id
    return token

def user_loader(user_id):
    return User.query.get_or_404(user_id)

def logout_user():
    print('Logging out user!')
    session.pop('jwt')
    session.pop('current_user')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = session.get('token') #https://
        token = session.get('jwt') #https://
        print(token)

        if not token:
            return redirect(url_for('login'))

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=algorithms)
            print("-----jwt-----")
            print(data)
            session['current_user'] = data['user']

        except:
            print(f'Token is invalid')
            flash(f'Token is invalid')
            return redirect(url_for('login'))

        
        return f(*args, **kwargs)

    return decorated



# ------ MODELS

class Groups(db.Model):
    tablename = ['Groups']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    appId = db.Column(db.String)
    slug = db.Column(db.String)
    total = db.Column(db.Integer, default=0)
    added = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"Group('id: {self.id}', 'total:{self.total}', 'slug:{self.slug}')"


class SenderId(db.Model):
    tablename = ['Groups']

    id = db.Column(db.Integer, primary_key=True)
    senderId = db.Column(db.String)
    appId = db.Column(db.String)
    slug = db.Column(db.String)
    total = db.Column(db.Integer, default=0)
    approved = db.Column(db.Boolean, default=True)
    added = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    date_approved = db.Column(db.DateTime)


    def __repr__(self):
        return f"Sender('id: {self.senderId}', 'AppId:{self.appId}')"


class User(db.Model):
    tablename = ['User']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    password = db.Column(db.String)
    appId = db.Column(db.String)
    slug = db.Column(db.String)
    total = db.Column(db.Integer, default=0)
    balance = db.Column(db.Float, default=0)
    credits = db.Column(db.Integer, default=0)
    added = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"User('id: {self.id}', 'slug:{self.slug}')"


class Package(db.Model):
    tablename = ['Package']

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    count = db.Column(db.Boolean, default=True)

    added = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
            return f"Package('id: {self.id}', 'price:{self.price}', 'credits:{self.credits}')"


class Report(db.Model):
    tablename = ['Report']

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    appId = db.Column(db.String)
    senderId = db.Column(db.String)
    message = db.Column(db.String)
    groupName = db.Column(db.String)
    sent = db.Column(db.Integer)
    rejected = db.Column(db.Integer)
    credit = db.Column(db.Integer)
    contacts = db.Column(db.Integer)
    groupId = db.Column(db.Integer)
    balanceBefore = db.Column(db.Float)
    balanceAfter = db.Column(db.Float)
    type = db.Column(db.String)
    providerId = db.Column(db.String)
    rawdata = db.Column(JSON, nullable=True)
    responsedata = db.Column(JSON, nullable=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"Report('id: {self.appId}-{self.id}', {self.sent}/{self.contacts}')"
    

class Contacts(db.Model):
    tablename = ['Contacts']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phoneNumber = db.Column(db.String)
    email = db.Column(db.String)
    appId = db.Column(db.String)
    slug = db.Column(db.String)
    groupId = db.Column(db.Integer)

    def __repr__(self):
        return f"Contact('id: {self.appId}-{self.id}', 'name:{self.name}', 'phoneNumber:{self.phoneNumber}')"
  
    # function to get all emails filter by appId and return as an array
    @staticmethod
    def get_all_emails(groupId):
        emails = Contacts.query.filter_by(groupId=groupId).all()
        email_array = []
        for email in emails:
            email_array.append(email.email)
        return email_array

class Message(db.Model):
    tablename = ['Message']
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    appId = db.Column(db.String)
    message = db.Column(db.String)
    groupSlug = db.Column(db.String)
    message_to = db.Column(db.String)
    message_from = db.Column(db.String)
    total = db.Column(db.Integer, default=0)


    def __repr__(self):
        return f"Message('id: {self.appId}-{self.id}', 'to:{self.groupSlug}', 'total:{self.total}')"


class Transactions(db.Model):
    tablename = ['Transactions']

    id = db.Column(db.Integer, primary_key=True)
    appId = db.Column(db.String)
    userId = db.Column(db.String, nullable=False)
    username = db.Column(db.String)
    packageId = db.Column(db.String)
    package = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    amount = db.Column(db.Float)
    total = db.Column(db.Float)
    charges = db.Column(db.Float)
    balanceBefore = db.Column(db.Float)
    balanceAfter = db.Column(db.Float)
    pending = db.Column(db.Boolean, default=True)
    requested = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    account = db.Column(db.String)
    network = db.Column(db.String)    
    transactionType = db.Column(db.String)
    ledgerEntryId = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    ref = db.Column(db.String) #notsupersure?
    prestoTransactionId = db.Column(db.Integer)
    channel = db.Column(db.String)
    telegramChatId = db.Column(db.String)

    def __repr__(self):
        return f"Transaction(': {self.id}', 'Amount:{self.amount}', 'User:{self.username}', 'Paid:{self.paid}')"

class LedgerEntry(db.Model):
    tablename = ['LedgerEntry']

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    amount = db.Column(db.Float)
    listing = db.Column(db.String)
    count = db.Column(db.Integer, default=0)
    balanceBefore = db.Column(db.Float)
    balanceAfter = db.Column(db.Float)
    transactionId = db.Column(db.Integer)
    type = db.Column(db.String)
    package = db.Column(db.String)
    packageId = db.Column(db.String)
    ref = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Payment Ghc('{self.amount}', ' - {self.userId}')"

class EmailTemplateEntry(db.Model):
    tablename = ['EmailTemplateEntry']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    subject = db.Column(db.String)
    message = db.Column(db.String)
    templateId = db.Column(db.String)
    groupId = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_sent = db.Column(db.DateTime)
    templateBody = db.Column(JSONB, nullable=True)
    recievers = db.Column(JSONB, nullable=True)
    bcc = db.Column(JSONB, nullable=True)

    def __repr__(self):
        return f"EmailTemplateEntry('{self.name}', ' - {self.subject}')"




def reportError(e, message = None):
    print(e)


def createTransaction(body):
    newTransaction = Transactions(
        userId=body.get("userId"),
        appId=body.get("appId"),
        username=body.get("username"),
        packageId=body.get("packageId"),
        package=body.get("package"),
        credits=body.get("credits"),
        amount=body.get("amount"),
        balanceBefore=body.get("balanceBefore"),
        account = body.get("account"),
        network = body.get("network"),
        channel = body.get("channel"),
        transactionType = body.get('transactionType'),
        total=body.get('total')
    )

    try:
        db.session.add(newTransaction)
        db.session.commit()
    except Exception as e:
        reportError(e)
        flash('There was an error creating this transaction!')

    return newTransaction


def externalPay(transaction):
    print("Triggering External Pay Transaction!")

    paymentInfo = {
        "name":"connect",
        "transactionId":transaction.id,
        "amount":transaction.amount,
        "currency":"GHS",
        "reference":transaction.username,
        "charges":0.03,
        "callbackUrl":baseUrl+"/confirm/"+str(transaction.id)
    }

    print(paymentInfo)

    try:   
        print("prestoUrl")
        print(prestoUrl)
        # response = requests.post(prestoUrl+"/externalpay/"+transaction.appId, json=paymentInfo)
        response = requests.post("https://prestoghana.com/externalpay/connect", json=paymentInfo)
        transaction.ref = response.json()["transactionId"]
    except Exception as e:
        print(e)
        print("Creating External Transaction failed!")

    print(response)
    print(response.json())
    return response.json()

def confirmPrestoPayment(transaction):

    r = None

    try:
        print("prestoUrl")
        print(prestoUrl)
        r = requests.get(prestoUrl + '/verifykorbapayment/'+str(transaction.ref)).json()
    except Exception as e:
        print(e)
    
    print(r)
    print("--------------status--------------")
    status = r.get("status", "failed")
    print(status)

    print("--------------server--------------")
    print(server)

    print("--------------transaction channel--------------")
    print(transaction.channel)

    if status == 'success' or environment == 'DEV' and server == "LOCAL" or transaction.channel == 'BANK':

        print("Attempting to update transctionId: " +str(transaction.id) + " to paid! in " + environment + "environment || SERVER:" + server)
        
        # findtrasaction, again because of the lag.
        state = Transactions.query.get_or_404(transaction.id)
        if state.paid != True:
            try:
                state.paid = True
                db.session.commit()
                print("Transaction : "+str(transaction.id) + " has been updated to paid!")

            except Exception as e:
                print("Failed to update transctionId: "+str(transaction.id )+ " to paid!")
                app.logger.error(e)
                reportError(e)

            return True
        return False

    else:
        print(str(transaction.id) + " has failed.")
        return False

def updateUserBalance(transaction):
    # find vote with same transaction id.
    alreadyCounted = LedgerEntry.query.filter_by(transactionId = transaction.id).first()
    if alreadyCounted != None: #If found.
        return None

    try: #Create a new vote
        newLedgerEntry = LedgerEntry(userId=transaction.userId, name=transaction.username, package = transaction.packageId, amount=transaction.amount, transactionId=transaction.id)
        db.session.add(newLedgerEntry)
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        reportError(str(e))
        app.logger.error("Couldnt create ledgerEntry for " + transaction.username)

    try: #SET UP DECIMAL POINTS
        user = User.query.get_or_404(int(transaction.userId))
        package = Package.query.get_or_404(transaction.packageId)
        
        transaction.balanceBefore = user.balance
        transaction.balanceAfter = user.balance - newLedgerEntry.amount
        # package.count += newLedgerEntry.amount

        print("----------------------- Updating balance ---------------------------")
        print("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        sendTelegram("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))

        # user.balance += package.credits
        # user.paid += newLedgerEntry.amount

        print("---USER IDENTIFICATION--")
        print(user)
        print(user.credits)
        print(transaction.credits)
        user.credits += transaction.credits
        
        transaction.ledgerEntryId = newLedgerEntry.id

        db.session.commit()

        print("----------------------- Updated Successfully! ---------------------------")

    except Exception as e:
        app.logger.error("Updating user " + user.username + " balance has failed." )
        app.logger.error(e)
        reportError(str(e))

    return newLedgerEntry

def sendTelegram(message_text, chat_id=chat_id):
    params = {
        'chat_id': chat_id,
        'text': message_text
    }
    pprint.pprint(params)

    try:
        response = requests.post(url = f'https://api.telegram.org/bot{telegramToken}/sendMessage', params=params)
        return response
    except Exception as e:
        reportError(e)
        return e
    
@app.errorhandler(500)
def internal_server_error(error):
    sendTelegram(f"500 Error on Dashboard \n {error}")
    return render_template('500.html'), 500



@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()   

    if request.method == 'POST':
        print(form.data)

        user = User.query.filter_by(email = form.email.data).first()
        print("user found :")
        print(user)

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print(user)

            jwt_token = login_user(user)
            print(jwt_token)

            sendTelegram(f"{user.username} has logged in to the dashboard.")
            return redirect(url_for('dashboard'))
        
        else:
            flash(f'These credentials are not valid')

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash(f'Successfully logged you out.')
    return redirect(url_for('home'))


@app.route('/addpackage', methods=['GET','POST'])
def addPackage():
    print("request")
    body = request.json

    package = {
        'price':body.get('price'),
        'credits':body.get('credits'),
        'active':body.get('active'),
    }

    message = f"Package {package.price} already exists"
    if Package.query.filter_by(price=body['price']) is None:
            
        try:
            newPackage = Package(price = body['price'], credits=body['credits'], active=body['active'])
            db.session.add(newPackage)
            db.session.commit()
            message = f'Package GHS{newPackage.price} has been uploaded successfully.'
        except Exception as e:
            reportError(e)
            message = 'Upload of new package has failed.'

    return message


@app.route('/',methods=['GET','POST'])
def home():
    current_user = get_current_user()
    return render_template('index.html', current_user=current_user)

def getgroup(groupId):
    groups = Contacts.query.filter_by(groupId=groupId).all()
    print(groups)
    return groups



@app.route('/broadcast', methods=['GET', 'POST'])
@app.route('/broadcast/<int:groupId>', methods=['GET', 'POST'])
def broadcast(groupId = None):
    current_user = get_current_user()
    form = BroadcastForm()
    form.senderId.choices = [ group.senderId for group in SenderId.query.filter_by(appId=current_user.appId).all()]
    print(groupId)
    if groupId is not None:
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.filter_by(id = groupId).all()]
        grouptotal = Groups.query.get_or_404(groupId).total
    else:
        grouptotal = 0
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.all()]
    if request.method == 'POST':
        if form.validate_on_submit():

            if current_user.credits < 0:
                flash(f'You dont have enough credits, Please purchase a bundle to continue.')
                return redirect(url_for('purchase'))
            
            message = form.message.data + f"\n{datetime.datetime.now().strftime('%c')}"+"\nPowered By PrestoConnect"
            groupId = form.group.data
            senderId = form.senderId.data

            print("senderId")
            print(senderId)

            group = getgroup(groupId)
            groupData = Groups.query.get_or_404(groupId)

            if group is not None:
                contacts = [contacts.phoneNumber for contacts in group]
            else:
                contacts = Contacts.query.all()

            print("Contacts: ",contacts)
            print("Message:",message,"Group",group)

            contacts = list(dict.fromkeys(contacts))
            print(contacts)

            response = sendMnotifySms(senderId, contacts, message)

            print("response!")
            pprint.pprint(response)
            response["presto_summary_data"] = {
                "message":message,
                "groupName":groupData.name,
                "groupId":groupData.id,
                "appId":current_user.appId,
                "balance":current_user.balance,
                "senderId":senderId
            }

            rawdata = {
                "contacts":contacts
            }

            # create report.
            createReport(response,rawdata)

            if response is not None:
                flash(f'{response["summary"]["total_sent"]} Messages were sent succesfully. Please check your reports')
                return redirect(url_for('dashboard'))
    return render_template('broadcast.html', form=form, current_user=current_user, grouptotal=grouptotal)




@app.route('/broadcastemail', methods=['GET', 'POST'])
@app.route('/broadcastemail/<int:groupId>', methods=['GET', 'POST'])
def broadcastemail(groupId = None):
    current_user = get_current_user()
    form = BroadcastEmailForm()

    print(groupId)

    if groupId is not None:
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.filter_by(id = groupId).all()]
        grouptotal = Groups.query.get_or_404(groupId).total
    else:
        grouptotal = 0
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.all()]
    
    if request.method == 'POST':
        
        if form.validate_on_submit():

            if current_user.credits < 0:
                flash(f'You dont have enough credits, Please purchase a bundle to continue.')
                return redirect(url_for('purchase'))
            
            message = form.message.data + f"\n{datetime.datetime.now().strftime('%c')}"+"\nPowered By PrestoConnect"
            groupId = form.group.data
            # senderId = form.senderId.data

            print("senderId")
            # print(senderId)

            group = getgroup(groupId)
            groupData = Groups.query.get_or_404(groupId)

            if group is not None:
                contacts = [contacts.email for contacts in group]
            else:
                contacts = Contacts.query.all()

            print("Contacts: ",contacts)
            print("Message:",message,"Group",group)

            contacts = list(dict.fromkeys(contacts))
            print(contacts)

            response = sendAnEmail(form.title.data, form.subject.data, form.message.data, contacts)

            print("response!")
            pprint.pprint(response)
            response["presto_summary_data"] = {
                "message":message,
                "groupName":groupData.name,
                "groupId":groupData.id,
                "appId":current_user.appId,
                "balance":current_user.balance
                # "senderId":senderId
            }

            rawdata = {
                "contacts":contacts
            }

            # create report.
            createReport(response,rawdata)

            if response is not None:
                flash(f'{response["summary"]["total_sent"]} Messages were sent succesfully. Please check your reports')
                return redirect(url_for('dashboard'))

    else:
        print(form.errors)
    return render_template('broadcastemail.html', form=form, current_user=current_user, grouptotal=grouptotal)


@app.route('/dashboard', methods=['GET', 'POST'])
@token_required
def dashboard():

    # sendTelegram(message_text="Hello")
    current_user = get_current_user()
    form=BroadcastForm()
    # form.group.choices = [ f"{group.name} - {group.total} contacts" for group in Groups.query.filter_by(appId=current_user.appId).all()]+[(None,'--None--')]
    data = {
       "name":current_user.username,
       "smsbalance":0,
       "senderIds":SenderId.query.filter_by(appId=current_user.appId).count(),
       "balance":current_user.credits,
       "contacts":Contacts.query.filter_by(appId=current_user.appId).count(),
       "groups":Groups.query.filter_by(appId=current_user.appId).count(),
       "reports":Report.query.filter_by(appId=current_user.appId).count()
    }

    if request.method == 'POST':
        if form.validate_on_submit():
            message = form.message.data + "\nPowered By PrestoConnect"
            
            # group = form.group.data
            sender_id = form.senderId.data
            recipients = form.recipients.data
            
            # split the recipients by comma into an array
            recipients = recipients.split(',')
            print(recipients)

            print("Contacts: ")
            print("Message:",message)

            response = sendMnotifySms(sender_id, recipients, message)
            print("response")
            print(response)

            if response is not None:
                flash(f'Messages were sent succesfully.')
                sendTelegram(f"{sender_id}:{recipients}\n{message}")
                return redirect('dashboard')
            else:
                flash(f'There seems to have been a problem.')
        else:
            print(form.errors)
    return render_template('dashboard.html', current_user=current_user ,data=data, form=form, user=get_current_user())

@app.route('/contacts', methods=['GET', 'POST'])
@app.route('/contacts/<int:slug>', methods=['GET', 'POST'])
@token_required
def contacts(slug = None):
    # Set the number of items per page
    per_page = 10

    # Get the current page number from the request arguments; default to 1
    page = request.args.get('page', 1, type=int)
    current_user = get_current_user()
    if slug:
        contactlist = Contacts.query.filter_by(groupId=slug, appId=current_user.appId).paginate(page=page, per_page=per_page)
        count = Contacts.query.filter_by(groupId=slug, appId=current_user.appId).count()
        group = Groups.query.get_or_404(slug)

        try:
            group.total = count
            db.session.commit()
        except Exception as e:
            reportError(e)

    else:
        contactlist = Contacts.query.filter_by(appId=current_user.appId).paginate(page=page, per_page=per_page)
        count = Contacts.query.filter_by(appId=current_user.appId).count()
        group = None
    
    return render_template('contacts.html', slug=slug, current_user=current_user, contactlist=contactlist, count=count, group=group, loadingMessage="Please wait while we process your request, this may take some time." )

@app.route('/issue', methods=['GET', 'POST'])
def issue():
    pass

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    current_user = get_current_user()
    form = TakePayment()
    packages = Package.query.order_by(Package.price.asc()).all()

    return render_template('purchase.html', form=form, current_user=current_user, loadingMessage="loadingMessage",charges=0.03, packages=packages)

@app.route('/groups/<string:appId>', methods=['GET', 'POST'])
def getGroups(appId):
    data = getgroup(appId)
    group = Groups.query.filter_by(appId=appId).first()
    return render_template('contacts.html', data=data, group=group, loadingMessage="Please wait while we complete your request. /nThis may take a while😭")

@app.route('/groups', methods=['GET', 'POST'])
def groups():   
    current_user = get_current_user()

    grouplist = Groups.query.filter_by(appId=current_user.appId).all()

    groupCount = len(grouplist)
    return render_template('groups.html', current_user=current_user,groupCount=groupCount ,grouplist=grouplist)

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = AddUserForm()
    return render_template('adduser.html', form=form)


@app.route('/recipt', methods=['GET', 'POST'])
def recipt():
    return render_template('email/receipt.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    return render_template('email/booking.html')

@app.route('/cureset', methods=['GET', 'POST'])
def cureset():
    return render_template('email/cureset.html')

@app.route('/newsletter', methods=['GET', 'POST'])
def newsletter():
    # news_items = [
    #     {
    #         "link": "https://www.central.edu.gh/expand/3117",
    #         "image": "https://webcms.central.edu.gh/wp-content/uploads/2024/07/WhatsApp-Image-2024-07-29-at-15.34.07-2.jpeg",
    #         "category": "Historical news",
    #         "title": "Central University and ICAG Forge Strategic Partnership",
    #         "description": "Central University has signed a Memorandum of Understanding (MoU) with the Institute of Chartered Accountants, Ghana (ICAG). This partnership, established under the Institute of Chartered Accountants, Ghana Act, 2020, Act 1058, is poised to elevate the education and training of accountants in the country."
    #     },
    #     {
    #         "link": "https://www.central.edu.gh/expand/3044",
    #         "image": "https://webcms.central.edu.gh/wp-content/uploads/2024/07/WhatsApp-Image-2024-07-18-at-05.07.00.jpeg",
    #         "category": "Student Activity",
    #         "title": "CU Chaplaincy Impact Prampram SHS",
    #         "description": "To God’s glory 94 dedicated students from Central University’s Campus Ministry under the guidance of the Chaplaincy, embarked on a meaningful outreach to Prampram Senior High School."
    #     },
    #     {
    #         "link": "https://www.central.edu.gh/expand/2777",
    #         "image": "https://webcms.central.edu.gh/wp-content/uploads/2024/05/IMG_6992.jpg",
    #         "category": "Alumni Focus",
    #         "title": "CU Alumni Association New Executives Sworn into Office",
    #         "description": "The new executives of the Central University (CU) Alumni Association were sworn into office on Thursday May 16 2024 at a short ceremony held at the Christ Temple Campus (CTC)."
    #     }
    # ]
    title = "The Reporter 🗞️"

    # Render the HTML content
    html_content = render_template('email/newsletter.html', title=title)

    # Define email details
    subject = "Central University Newsletter - August 2024"
    receivers = ["oadewale@central.edu.gh"]

    # Send the email
    sendAnEmail(title, subject, html_content, receivers)

    return "Newsletter sent successfully!"

@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template('email/success.html')


@app.route('/email_templates', methods=['GET', 'POST'])
def email_templates():
    # ADE: TEMPLATES ARE ARRAYS SO SEND THE ARRAYS TO THE FRONT NOT INDIVIDUAL ITEMS
    templates = [
        {
        "title" : "Newsletter",
        "url":  "newsletter",
        "img" :"https://cdn.dribbble.com/userupload/14695577/file/original-93441cc40aba53310e95e95ecb6424a6.png?resize=1504x1128"
        }
    ]
    return render_template('email/email_templates.html', templates= templates)

# Function to take an array of id and return a group of post
def convetIdToPost(idArray):
    posts = []
    
    for i in idArray:
        wppost = getMetaData(i)
        wpImage = getImageUrl(wppost['rendered_content']['featured_media'])
        post = {
            "title": wppost['rendered_content']['title']['rendered'],
            "link": f"https:central.edu.gh/expand/{i}",
            "category": "cat",
            "image": wpImage,
            "description": wppost['rendered_content']['excerpt']['rendered'],
        }
        pprint.pprint(post)

        posts.append(post)
    return posts
        
    

@app.route('/email_details', methods=['GET', 'POST'])
@app.route('/email_details/<string:templateId>', methods=['GET', 'POST'])
def email_details(templateId=None):

    form = BroadcastEmailForm()
    # templateId = "dynamic"
    templateId = "newsletter" 

    form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.all()]
    form.templateid.choices = [ (template) for template in fetchEmailtemplate()]

    # create a temporary id
    # save to session
    # do a blast and create a report.

    # preview function should return an html render in a new opage
    if request.method == 'POST':
        if form.validate_on_submit(): 
            group = Groups.query.get_or_404(form.group.data)
            # emails = Contacts.get_all_emails(group.id)

            templateId = form.templateid.data


            # PROCESS JSON INTO DICTIONARY
            pretemplateBody = json.loads(form.message.data) #TODO: Convert back to templateBody for consistency
            pprint.pprint(pretemplateBody)

        
            templateBody = {
                "type": "short",
                "groupId":form.group.data,
                "templateId":form.templateid.data,
                "title": form.title.data,
                "subject": form.subject.data,
                "name": "PRESTO CONNECT",
                "receivers":["connect@prestoghana.com"],
                "bcc": [],
                "message": "PRESTO CONNECT",
                "data": pretemplateBody
            }
            
            # CREATE TEMPORARY BODY 

            session['temporaryBody'] = templateBody
            pprint.pprint(templateBody)
            return render_template(f'email/{templateId}.html', body=templateBody, local=False)
        else:
            print(form.errors)

    return render_template('email/email_details.html', groups=groups, form=form, template=templateId, templateId=templateId)


# class WordpressPost:
#     def __init__(self, id, title, content, date, author, image):
#         self.id = id
#         self.title = title
#         self.content = content
#         self.date = date
#         self.author = author
#         self.image = image
        
def getMetaData(id):
    # Get URL
    url = cuwebBaseUrl + "/?rest_route=/wp/v2/posts/" + str(id)
    print(url)
    r = requests.get(url)
    content = r.json()
    # print(content)
    # print(content[0])
    return ({"rendered_content":content})

def getImageUrl(id):
    print(id)
    try:
        url = cuwebBaseUrl + "/?rest_route=/wp/v2/media/" + str(id)
        r = requests.get(url)
        print(r)
        image = r.json()["guid"]["rendered"]
    except Exception as e:
        print(e)
        image = "https://banner2.cleanpng.com/20190216/fox/kisspng-central-university-ghana-technology-university-col-school-of-theology-amp-missions-central-univer-5c67c799ec2858.1783459915503051779673.jpg"
    return image

def news():
    page = request.args.get("page", "1")
    print("page")
    print(page)
    # Get URL
    id = 24
    per_page = 30
    url = (
        baseWpUrl
        + "/wp-json/wp/v2/posts?page="
        + str(page)
        + "&categories="
        + str(id)
        + "&per_page="
        + str(per_page)
    )
    # url = "http://45.222.128.105/wp-json/wp/v2/posts?categories="+str(id)
    r = requests.get(url)
    response = r.json()
    print("response.headers")
    print(r.headers)
    totalPages = r.headers["x-wp-totalpages"]
    news = []
    for i in response:
        article = {}
        article["id"] = i["id"]
        article["image"] = getImageUrl(i["featured_media"])
        article["title"] = i["title"]["rendered"]
        article["date"] = i["date"]
        article["author"] = getAuthorName(i["author"])
        news.append(article)
    print(news)
    return render_template(
        "news.html",
        news=news,
        totalPages=totalPages,
        page=page,
        per_page=per_page,
        title="News & Blog",
    )

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    return render_template('email/reset.html')

@app.route('/thankyou', methods=['GET', 'POST'])
def thankyou():
    return render_template('email/thankyou.html')

@app.route('/election')
def election():
    return render_template('email/election.html')


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    return render_template('email/survey.html')


@app.route('/purchase/<int:id>', methods=['GET','POST'])
def pay(id):
    print("purchasing package id.")
    package = Package.query.get_or_404(id)
    user = get_current_user()
    print("---------")
    print(user)
    body={
        "userId":user.id,
        "appId":user.appId,
        "username":user.username,
        "amount":package.price,
        "package":package.price,
        "packageId":package.id,
        "credits":package.credits,
        "balanceBefore":user.balance,
        "transactionType":'Default',
        "channel":"WEB"
    }

    # include date bought
    # credits before purchase
    transaction = createTransaction(body)

    response = externalPay(transaction)

    return redirect(response["url"])

def sendMnotifySms(sender_id, recipients, message):
    endPoint = 'https://api.mnotify.com/api/sms/quick'
    api_key = "whmBov51IDjkTtj6AAWmakuid9NljoRPFdr4Jx6rbqM4T" #Remember to put your own API Key here
    data = {
    'recipient[]': recipients,
    'sender': sender_id,
    'message': message,
    'is_schedule': False,
    'schedule_date': ''
    }
    url = endPoint + '?key=' + api_key
    response = requests.post(url, data)
    data = response.json()
    pprint.pprint(data)
    return data

def createMnotifyGroup(group_name):
    endPoint = 'https://api.mnotify.com/api/sms/quick'
    api_key = "whmBov51IDjkTtj6AAWmakuid9NljoRPFdr4Jx6rbqM4T" #Remember to put your own API Key here
    data = {
    'group_name': group_name,
    }
    url = endPoint + '?key=' + api_key
    response = requests.post(url, data)
    data = response.json()
    pprint.pprint(data)
    return data
  

def save_uploaded_file(file):
    print(file)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    # Create contacts
    # Append them to group
    return filename

def findExistingPhoneNumber(phone):
    print(phone)
    return True

def updateGroup(id):
    group = Groups.query.get_or_404(id)
    total = Contacts.query.filter_by(groupId = id).count()
    try:
        group.total = total
        db.session.commit()
    except Exception as e:
        reportError(e)

def convertToPhoneNumber(phone):
    phone = phone.replace(' ','')
    phone = "0"+phone[-9:]
    return phone


@app.route('/upload_file', methods=['GET', 'POST'])
@token_required
def upload_file():
    current_user = get_current_user()
    if request.method == 'POST':
        print('POST REQUEST')
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            print("There was no csvfile found!")
            file = None
        else:
            file = request.files['file']

        name = request.form.get('name','default')

        # appId = request.form.get('appId','default')
        appId = current_user.appId

        slug=appId + name.replace(" ","")+datetime.datetime.now().strftime('%c')
        print("name:",name, "slug:",slug)

        if Groups.query.filter_by(slug=slug).first() is None:
            # calculate contacts with the same slug
            total = Contacts.query.filter_by(slug=slug).count()
            newgroup = Groups(name = name, appId=appId, slug=slug, total=total )
            db.session.add(newgroup)
            db.session.commit()
        else:
            flash(f'Oops, seems there is a group with this slug. Please provide a different identifier.')
            return redirect(url_for('groups'))

        # If the user does not select a file, browser submits an empty file without a filename
        # if file.filename == '':
        #     return redirect(request.url)

        if file:
            # Save the uploaded file
            filename = save_uploaded_file(file)
            print("filename:")
            print(filename)

            # filename =  request.form.get('name',filename)

            # Process the CSV file (for demonstration purposes)
            with open(filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    print(row)
                    # check if phone number already exists
                    # findExistingPhoneNumber()
                    
                    newcontact = Contacts(name=row[0], phoneNumber=convertToPhoneNumber(row[1]), appId=appId, slug=slug, groupId=newgroup.id, email=row[2])
                    try:
                        db.session.add(newcontact)
                    except Exception as e:
                        reportError(e)
                db.session.commit()

        updateGroup(newgroup.id)
        

        flash(f'Your data has been recieved!')
        return redirect('dashboard')

    return "    "


@app.route('/group/<int:groupId>', methods=['GET','POST'])
def group(groupId):
    if request.method == 'POST':

        print(request)
        
        if 'csv_file' not in request.files:
            print("No CSV File!")
            return "No CSV file provided"
        
        if request.form.get('message',None) is None:
            print("No Message Found!")
            return "No Message Found!"
        else:
            message = request.form.get('message',None)
            senderId = request.form.get('senderId',None)

        csv_file = request.files['csv_file']

        if csv_file.filename == '':
            return "No selected file"

        # Process the uploaded CSV file
        csv_content = csv_file.read().decode('utf-8')

        # Generate a unique file name with date-time stamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # filename = f"uploaded_csv_{timestamp}.csv"
        filename = f"{timestamp}-rawdata.csv"

        # Save the processed CSV with the generated filename
        save_path = os.path.join(app.root_path,"Uploads", filename)  # Replace "path_to_save" with your desired path
        
        
        with open(save_path, "w") as f:
            f.write(csv_content)

        flash(f"CSV file uploaded and saved as {filename}")

        with open(save_path, 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            nanakweku = ['0545977791','0245595389']
            contacts = []

            for row in csv_reader:
                contacts.append(row['PhoneNumber'])
            
            # remove duplicates in contacts
            filteredcontacts = list(dict.fromkeys(contacts))
            print(filteredcontacts)

            message = message + "\n\nPowered By PrestoConnect"

            return sendMnotifySms(senderId, filteredcontacts, message)

    else:
        # return group members
        # fetch from csv
        # remove duplicates
        # Return analytics
        
        return render_template('group.html', contacts=contacts)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    return redirect('contacts', )

@app.route('/deleteGroup/<int:id>', methods=['GET', 'POST'])
def deleteGroup(id):
    print("Attempting to delete group and subsequest contacts")

    group = Groups.query.get_or_404(id)
    contacts = Contacts.query.filter_by(groupId=id).all()
    contactCount = Contacts.query.filter_by(groupId=id).count()

    try:
        for index, i in enumerate(contacts):
            print(index, "/", contactCount)
            print(i)
            db.session.delete(i)
            print("---------")
        db.session.commit()
        flash(f'{contactCount} contacts have been deleted')
    except Exception as e:
        reportError(e)

    try:
        db.session.delete(group)
        db.session.commit()
        flash(f'{group.name} has been deleted')
    except Exception as e:
        reportError(e)

    return redirect(url_for('groups'))

def createReport(reportBody, rawdata):
    print("Creating Report ")
    pprint.pprint(reportBody)

    summaryReport = reportBody['summary']
    prestoSummaryReport = reportBody['presto_summary_data']

    print("PRSREPORT!")
    pprint.pprint(prestoSummaryReport)


    try:

        balanceAfter = prestoSummaryReport.get('balance') - summaryReport.get('credit_used', None)

        newReport = Report(rawdata=rawdata, responsedata=reportBody,status=reportBody.get('status', None), appId=prestoSummaryReport.get('appId', 'default'), contacts=summaryReport.get('contacts', 'default'), sent=summaryReport.get('total_sent', None), rejected=summaryReport.get('total_rejected', None), credit=summaryReport.get('credit_used', None), type=summaryReport.get('type', None), providerId=summaryReport.get('_id', None), message=prestoSummaryReport.get('message', None),  groupName=prestoSummaryReport.get('groupName', None),  groupId=prestoSummaryReport.get('groupId', None), balanceBefore = prestoSummaryReport.get('balance', None), senderId=prestoSummaryReport.get('senderId', None), balanceAfter=balanceAfter )
        db.session.add(newReport)
        db.session.commit()

        # newReport.balanceAfter = newReport.balanceBefore - newReport.credit
        # db.session.commit()
    except Exception as e:
        reportError(e)


    try:
        user = User.query.get_or_404(get_current_user().id)

        if user is not None:
            user.credits -= newReport.credit
            user.total += newReport.credit
            db.session.commit() 

    except Exception as e:
        reportError(e, 'Couldnt update user balance')

    # print(newReport)

    # newReport = Report(/)
    # take the json
    # create a db entry
    # send an email
    # done.
    return "Done"


@app.route('/sender_id', methods=['GET', 'POST'])
def sender_id():
    form = RequestSenderIdForm()
    current_user = get_current_user()
    all_sender_id = SenderId.query.filter_by(appId=current_user.appId).all(),

    if request.method == 'POST':
        if form.validate_on_submit():
            requestedSenderId = SenderId(
                senderId=form.senderId.data,
                slug=form.description.data,
                appId=current_user.appId
            )
            print(requestedSenderId)
            # sendTelegram(requestedSenderId)
            sendTelegram(message_text=requestedSenderId)
            flash(f'{form.senderId.data} has been requested!')
            return redirect(url_for('sender_id'))

    return render_template('senderId.html', current_user=current_user, form=form, all_sender_id=all_sender_id)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    current_user = get_current_user()

    reports = Report.query.filter_by(appId=current_user.appId).order_by(Report.id.desc()).all()
    reportCount = len(reports)
    return render_template('reports.html', current_user=current_user,reports=reports, count = reportCount)

@app.route('/report/<int:id>', methods=['GET', 'POST'])
def report(id):
    current_user = get_current_user()

    report = Report.query.get_or_404(id)

    print("RAW DATA")
    pprint.pprint(report.rawdata)
    print("RESPONSE DATA")
    pprint.pprint(report.responsedata)

    allcontacts = report.rawdata['contacts']
    successfulcontacts = report.responsedata['summary']['numbers_sent']
    
    print("Intersecting")
    print(allcontacts)
    print(successfulcontacts)
    
    contacts = []
    for c in allcontacts:
        if c in successfulcontacts:
            contacts.append({c:1})
        else:
            contacts.append({c:0})

    print(contacts)
    return render_template('report.html', report=report, contacts=contacts, current_user=current_user)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def updateContact(id):
    current_user = get_current_user()
    form = AddUserForm()
    user = Contacts.query.get_or_404(id)
    print(user)
    print(user.groupId)
    group = Groups.query.get_or_404(user.groupId)
    print(group)
    if request.method == 'GET':
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.filter_by(id = group.id).all()]
        form.name.data = user.name
        form.phone.data = user.phoneNumber
        form.group.data = group.name
        form.email.data = user.email

    elif request.method == 'POST':
        user.name = form.name.data
        user.phoneNumber = form.phone.data
        user.email = form.email.data

        try:
            db.session.commit()
            flash(f'{user.name} has been updated!')
            return redirect(url_for('contacts', slug=group.id))
        except Exception as e:
            reportError(e, "Couldnt update contact")

    return render_template('addcontact.html', form=form, current_user=current_user)


@app.route('/new', methods=['GET', 'POST'])
@app.route('/new/<int:groupId>', methods=['GET', 'POST'])
@token_required
def new(groupId=None):
    current_user = get_current_user()
    print(f"user: {current_user.username}")

    # if group.appId != current_user.appId:
    #     flash(f'You are not authorized to perform that action')
    #     return redirect('logout')

    form = AddUserForm()

    if groupId is not None:
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.filter_by(id = groupId).all()]
    else:
        form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.filter_by(appId=current_user.appId)]
    
    if request.method == 'POST':
        print(form.data)
        if form.validate_on_submit():
            try:
                newContact = Contacts(name=form.name.data, phoneNumber=form.phone.data, email=form.email.data, appId=current_user.appId, slug="slug", groupId = form.group.data )
                db.session.add(newContact)
                db.session.commit()
                flash(f'New Contact: {newContact.name} has been added to this group!')
                return redirect(url_for('contacts', slug=form.group.data))
            
            except Exception as e:
                reportError(e)
        else:
            print(form.errors)

    return render_template('addcontact.html', form=form, current_user=current_user)


@app.route('/confirm/<string:transactionId>', methods=['GET', 'POST'])
def confirm(transactionId):
    if request.is_json:
        print("-------------- CALLBACK RECIEVED --------------- ")
        print(request.url)
        print("-------------- CALLBACK DATA --------------- ")
        print(request.json)

        message = "In Progress"
        transaction = Transactions.query.get_or_404(transactionId)
        user = User.query.get_or_404(transaction.userId)
        print(transaction)
        # SECURE THIS ROUTE

        if transaction.paid == False:
            body = request.json
            try:
                print("Attempting to update transaction id: " + str(transaction.id) + " with prestoRef ")
                transactionRef = body["transactionId"]
                print(transactionRef)

                transaction.ref = transactionRef
                transaction.account = body.get("account")
                transaction.channel = body.get("channel")

                db.session.commit()
            except Exception as e:
                print(e)

            message = "Failed Transaction"

            if confirmPrestoPayment(transaction) == True:

                message = "Duplicate"
                entry = updateUserBalance(transaction)
                if entry != None: #If a vote was created

                    responseMessage = transaction.packageId + "\nSuccessfully bought " +str(transaction.amount) + " for " + str(transaction.username) + "." + "\nBefore: " + str(transaction.balanceBefore) + "\nAfter: "+ str(transaction.balanceAfter) + "\nTransactionId:" + str(transaction.id) + str(transaction.account) + "\nLedgerId: " + str(entry.id)
                    message = f"Hello {user.username} you have successfully bought {transaction.credits} credits. Your new account balance is {user.credits}."

                    # TODO: SEND A MESSAGE WHEN PURCHASE IS SUCCESSFUL?

                    print("send_sms || PrestoStay)")
                    sendMnotifySms("PRSConnect",transaction.account, message)

                    print(responseMessage)
                    sendTelegram(responseMessage)

                    # sendTelegram(responseMessage, user.chatId)
                    
                    # emails = [ admin.email for admin in User.query.filter_by(role = 'admin').all()]
                    # print(emails)

                    # sendAnEmail(transaction.username, f'GHC {transaction.amount} SUCCESSFULLY RECIEVED', responseMessage, emails)

                    flash(f'This transaction was successful! You should recieve and sms.')
                else:
                    app.logger.error("Transaction: " + str(transaction.id) + " was attempting to be recreated.")
                
            else:
                message = "This transaction has either failed or is being processed. Please check or try again."

        responseBody = {
            "message":message,
            "transactionId":transaction.id,
            "prestoTransactionId":transaction.ref,
            "paid":transaction.paid
        }
        print(responseBody)
        return responseBody
    else:
        transaction = Transactions.query.get_or_404(transactionId)
        user = User.query.get_or_404(transaction.userId)
        return render_template('transaction.html', transaction=transaction, user=user)


@app.route('/api/broadcast', methods=['GET', 'POST'])
def broadcast_api():
    # get message
    print("request")
    print(request.json)
    body = request.json
    pprint.pprint(body)

    message = body.get('message') + f"\n{datetime.datetime.now().strftime('%c')}"+"\nPowered By PrestoConnect"
    senderId = body.get('senderId', 'PRSConnect')
    contacts = body.get('contacts', None)
    # array of contacts

    print("senderId")
    print(senderId)

    print("Contacts: ",contacts)

    # remove duplicates
    contacts = list(dict.fromkeys(contacts))
    # Remove spaces and get last 9 characters
    contacts = ["0"+item.replace(" ", "")[-9:] for item in contacts]
    print(contacts)

    response = sendMnotifySms(senderId, contacts, message)

    response["presto_summary_data"] = {
        "message":message,
        "groupName":"API_SMS",
        "groupId":0
    }

    # create report.
    createReport(response, body)

    return response

@app.route('/onboard', methods=['GET', 'POST'])
def onboard():
    form = RegisterForm()
    if form.validate_on_submit():

        # if User.query.filter_by(email=form.email.data) is not None:
        #     flash(f'Sorry this email is taken')
        # elif User.query.filter_by(name=form.name.data) is None:
        #     flash(f'Sorry this senderId is taken.') 


        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        newuser = User(username=form.username.data, email=form.email.data, phone=form.phone.data, password=hashed_password, balance=100, total=100, credits=100, appId=form.appId.data)
        print(newuser)
        try:
            db.session.add(newuser)
            db.session.commit()
            message =  "Congratulations on successfully being onboarded to Presto Connect.\nYou have recieved 100 free sms credits.\n\nIf you need any form of support you can call +233545977791 "
            sendMnotifySms('PRSConnect', newuser.phone, message)
            sendTelegram(newuser.username +" : " + newuser.phone + " has onboarded to PrestoConnect. \nhttps://stay.prestoghana.com/profile/ \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
            token = login_user(newuser)

            try:
                newSenderId = SenderId(senderId='PRSConnect', appId=newuser.appId, approved=True)
                db.session.add(newSenderId)
                db.session.commit()
            except Exception as e:
                reportError(e,'Sender ID assigning to {newuser.username} failed.')
                 

            if token is not None:
                return redirect(url_for('dashboard'))
            else:
                flash(f'Logging in to your account has failed. Please try logging in again.')
                return redirect(url_for('login'))

        except Exception as e:
            print(e)
            print("User was not able to be created")
        print("Registered new user: " + newuser.username + " " + newuser.email)
                

    else:
        print(form.errors)

    return render_template('onboard.html', form=form)


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(error)
    print("error")
    print(error)

    error_message = str(error)

      # Check if the error_message contains "500 Internal Server Error" (default Flask message)
    # if error_message == "500 Internal Server Error":
        # If it's the default message, try to extract the original exception message
    original_exception = getattr(error, "original_exception", None)
    if original_exception:
        error_message = str(original_exception)
        print("====================")
        print(error_message)

        reportTelegram(error_message)
    
    return render_template('500.html'), 500


# @app.route('/foomail', methods=['GET', 'POST'])
# def foomail():
#     if request.method == 'POST':
#         body = request.json

#         templateId = body.get("templateId", "dynamic")
#         # For other templates, render with the provided body data
#         html_content = render_template(f'email/{templateId}.html', body=body.get("templateBody"))

#         # Send the email
#         title = body.get("title", "No Title")
#         subject = body.get("subject", "No Subject")
#         receivers = body.get("receivers", [])
#         bcc_receivers = body.get("bcc", [])

#         sendAnEmail(title, subject, html_content, receivers, bcc_receivers)



#         return "Email sent successfully!"
#     else:
#         return "This endpoint only supports POST requests."
    

@app.route('/email_preview', methods=['GET', 'POST'])
def email_preview():
    body = session['temporaryBody']
    print("===email===body====")
    pprint.pprint(body)
    body['bcc'] = Contacts.get_all_emails(int(body['groupId']))
    pprint.pprint(body)
    # response = body
    response = sendTemplateEmail(body)
    return jsonify(response)



@app.route('/foomail', methods=['GET', 'POST'])
def foomail():
    if request.method == 'POST':
        body = request.json
        print(body)
        pprint.pprint(body)

        # takes in body
        response = sendTemplateEmail(body)
        return jsonify(response)
# function 

def sendTemplateEmail(body):
    templateId = body.get("templateId", "dynamic")

    # For other templates, render with the provided body data
    html_content = render_template(f'email/{templateId}.html', body=body)

    # Send the email
    title = body.get("title", "No Title")
    subject = body.get("subject", "No Subject")
    
    # receivers = body.get("receivers", [])
    receivers = body.get("receivers", [])
    bcc_receivers = body.get("bcc", [])

    emailResponse = sendAnEmail(title, subject, html_content, receivers, bcc_receivers)
    print(emailResponse)

    return emailResponse

# route to take a csv loop throught each line
@app.route('/dynamic_csv', methods=['GET', 'POST'])
def dynamic_csv():
    # accept csv file
    if request.method == 'POST':
        csv_file = request.files['file']
        print(csv_file.filename)
        # check if file is csv

        if csv_file.filename.endswith('.csv'):
            filename = save_uploaded_file(csv_file)
            print("filename", filename)
            # read csv file

            with open(filename, mode='r', newline='') as file:
                print("file: ",file)

                # Create a DictReader object
                csv_reader = csv.DictReader(file)
                print('csv_reader')
                print(csv_reader)

                headers = csv_reader.fieldnames
                print('headers')
                print(headers)

                # Iterate over the rows in the CSV file
                for row in csv_reader:
                    print(row)
                    message = row['Message']
                    # message.format(Name=row['Name'], Category=row['Category'], UssdCode=row['UssdCode'], )
                    formattedMessage = message.format(**row)
                    # Print each row as a dictionary
                    print('row')
                    print(row)
                    print("MESSAGE")
                    print(formattedMessage)
                    sendMnotifySms(row['Number'], row['Number'], formattedMessage)
                
        
            return 'File uploaded successfully'

        else:
            flash('Please upload a csv file')
            return redirect(url_for('dashboard'))
    



def broadcast_mail(body):
    pprint.pprint(body)

    templateId = body.get("templateId")

    html_content =  render_template(f'email/{templateId}.html', body = body.get("templateBody") )
    return sendAnEmail(body.get("title"), body.get("subject"), html_content, body.get("receivers"), bcc_receivers=body.get("bcc"))


def sendAnEmail(title, subject, html_content, email_receiver, bcc_receivers=None,path=None):
    print("Attempting to send an email")
    print(email_receiver)
    print(type(email_receiver))


    email_sender = os.environ["PRESTO_MAIL_USERNAME"]
    email_password = os.environ["PRESTO_MAIL_PASSWORD"]


    em = EmailMessage()
    em["From"] = f"{title} <{email_sender}>"
    em["To"] = email_receiver
    # em["To"] = ", ".j÷oin(email_receiver)
    em["Subject"] = subject
    # em["Bcc"] = 'prestoghana@gmail.com'

    if bcc_receivers:
        if isinstance(bcc_receivers, list):
            em["Bcc"] = ", ".join(bcc_receivers)
            print("bcc_receievers")
            print(bcc_receivers)
        else:
            print("bcc_receivers must be a list of email addresses")
            raise TypeError("bcc_receivers must be a list of email addresses")

    em.set_content("")
    em.add_alternative(html_content, subtype="html")

    print(em)

    if path != None:
        em.add_attachment(
            open(path, "rb").read(),
            maintype="application",
            subtype="pdf",
            filename=title,
        )

    smtp_server = "mail.privateemail.com"
    port = 465

    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(email_sender, email_password)
    # all_recipients = email_receiver
    all_recipients = [email_receiver] + (bcc_receivers if bcc_receivers else [])
    print('all_recipients')
    print(all_recipients)
    server.sendmail(email_sender, all_recipients, em.as_string())
    server.quit()
    return {
        "recipeints":all_recipients, 
        "message":"Email sent successfully"
        }

@app.route('/fetch-metadata', methods=['POST'])
def fetch_metadata(url=None):
    if url is None:
        url = request.json.get('url')
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fetching the title
        title = soup.find('title').string if soup.find('title') else 'No title found'

        # Fetching meta description
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'No description found'
        description = description.replace("<p>","")
        description = description.replace("</p>","")

        # Fetching meta keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords['content'] if keywords else 'No keywords found'

        # Fetch the meta image
        meta_image = soup.find('meta', property='og:image')
        image_url = meta_image['content'] if meta_image else 'No image found'

        return {
            'url': url,
            'image': image_url,
            'title': title,
            'description': description,
            'keywords': keywords,
            'image': image_url
        }
    
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'error': str(e)
        }

def fetch_metadata_from_urls(urls):
    metadata_list = []
    for url in urls:
        metadata = fetch_metadata(url)
        metadata_list.append(metadata)
    return metadata_list

    # metadata = fetch_metadata_from_urls(urls)
    # for data in metadata:
    #     print(f"URL: {data['url']}")
    #     if 'error' in data:
    #         print(f"Error: {data['error']}")
    #     else:
    #         print(f"Title: {data['title']}")
    #         print(f"Description: {data['description']}")
    #         print(f"Keywords: {data['keywords']}")
    #     print('-' * 80)





if __name__ == '__main__':
    app.run(port=4000,host='0.0.0.0',debug=True)