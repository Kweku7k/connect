
import csv
import datetime
import os
import pprint
from flask import Flask, flash, jsonify,redirect,url_for,render_template,request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
from sqlalchemy.dialects.postgresql import JSON
from flask_bcrypt import Bcrypt


from functools import wraps
import jwt

from forms import *
# from flask_login import UserMixin, login_user, logout_user, current_user, LoginManager, login_required

app=Flask(__name__)
app.config['SECRET_KEY'] = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'
app.config['JWT_SECRET_KEY'] = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'

# app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:adumatta@database-1.crebgu8kjb7o.eu-north-1.rds.amazonaws.com:5432/connect'
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('CONNECT_DB_URL', 'postgresql://postgres:adumatta@localhost:5432/connect' )

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


algorithms = ["HS256"]



baseUrl = os.environ.get('CONNECT_BASE_URL', 'sandbox.prestoghana.com')
prestoUrl = os.environ.get('PRESTO_URL', 'sandbox.prestoghana.com')
server = os.environ.get('SERVER', None)
environment = os.environ.get('ENVIRONEMT', None)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

chat_id = os.environ.get('presto_telegram_bot')
telegramToken = os.environ.get('telegram_token')


def get_current_user():
    # TODO: Convert class into dictionary
    user_found = session.get('current_user', None)
    if user_found is not None:
        user = User.query.get_or_404(user_found)
        if user is not None:
            return user
    return None
     

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
            flash(f'Token is invalid')
            return redirect(url_for('dashboard'))

        
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
    appId = db.Column(db.String)
    slug = db.Column(db.String)
    groupId = db.Column(db.Integer)

    def __repr__(self):
        return f"Contact('id: {self.appId}-{self.id}', 'name:{self.name}', 'phoneNumber:{self.phoneNumber}')"
  

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
    ref = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Payment Ghc('{self.amount}', ' - {self.userId}')"



def reportError(e):
    print(e)


def createTransaction(body):
    newTransaction = Transactions(
        userId=body.get("userId"),
        appId=body.get("appId"),
        username=body.get("username"),
        packageId=body.get("packageId"),
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
        "name":transaction.username,
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
        response = requests.post("https://sandbox.prestoghana.com/externalpay/"+transaction.appId, json=paymentInfo)
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
        newLedgerEntry = LedgerEntry(userId=transaction.userId, name=transaction.username, package = transaction.package, amount=transaction.amount, transactionId=transaction.id)
        db.session.add(newLedgerEntry)
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        reportError(str(e))
        app.logger.error("Couldnt create ledgerEntry for " + transaction.username)

    try: #SET UP DECIMAL POINTS
        user = User.query.get_or_404(int(transaction.userId))
        package = Package.query.filter_by(slug = user.listingSlug).first()
        
        transaction.balanceBefore = user.balance
        transaction.balanceAfter = user.balance - newLedgerEntry.amount

        package.amountRecieved += newLedgerEntry.amount

        print("----------------------- Updating balance ---------------------------")
        print("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        sendTelegram("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        
        user.balance -= newLedgerEntry.amount
        user.paid += newLedgerEntry.amount
        
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

    try:
        response = requests.post(url = f'https://api.telegram.org/bot{telegramToken}/sendMessage', params=params)
        return response
    except Exception as e:
        reportError(e)
        return e


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
    if request.method=='POST':
        return render_template('index.html')
    return render_template('index.html')

def getgroup(groupId):
    groups = Contacts.query.filter_by(groupId=groupId).all()
    print(groups)
    return groups

@app.route('/broadcast', methods=['GET', 'POST'])
def broadcast():
    form = BroadcastForm()
    form.senderId.choices = ['PrestoHelp']
    form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            message = form.message.data + f"\n{datetime.datetime.now().strftime('%c')}"+"\nPowered By PrestoConnect"
            groupId = form.group.data
            senderId = form.senderId.data

            print("senderId")
            print(senderId)

            group = getgroup(groupId)

            groupData = Groups.query.get_or_404(groupId)

            # check for either groupId or contact array


            if group is not None:
                contacts = [contacts.phoneNumber for contacts in group]
            else:
                contacts = Contacts.query.all()

            print("Contacts: ",contacts)
            print("Message:",message,"Group",group)

            contacts = list(dict.fromkeys(contacts))
            print(contacts)

            response = sendMnotifySms(senderId, contacts, message)

            response["presto_summary_data"] = {
                "message":message,
                "groupName":groupData.name,
                "groupId":groupData.id
            }

            rawdata = {
                "contacts":contacts
            }

            # create report.
            createReport(response,rawdata)

            if response is not None:
                flash(f'Messages were sent succesfully.')
                return redirect('dashboard')
    return render_template('broadcast.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@token_required
def dashboard():
    form=BroadcastForm()
    form.group.choices = [ f"{group.name} - {group.total} contacts" for group in Groups.query.all()]
    current_user = get_current_user()
    data = {
       "name":current_user.username,
       "smsbalance":0,
       "balance":current_user.total,
       "contacts":Contacts.query.filter_by(appId=current_user.appId).count(),
       "groups":Groups.query.filter_by(appId=current_user.appId).count(),
       "reports":Report.query.filter_by(appId=current_user.appId).count()
    }

    if request.method == 'POST':
        if form.validate_on_submit():
            message = form.message.data + "\nPowered By PrestoConnect"
            group = form.group.data

            group = getgroup(group)

            if group is not None:
                contacts = [contacts.phoneNumber for contacts in group]
            else:
                contacts = Contacts.query.all()

            print("Contacts: ",contacts)
            print("Message:",message,"Group",group)

            contacts = ['0545977791','0545977791']
            # contacts = [contact.phoneNumber for contact in Contacts.query.all()]
            contacts = list(dict.fromkeys(contacts))
            print(contacts)

            response = sendMnotifySms('LASPAG-CU', contacts, message)

            if response is not None:
                flash(f'Messages were sent succesfully.')
                return redirect('dashboard')
    return render_template('dashboard.html', current_user=current_user ,data=data, form=form, user=get_current_user())

@app.route('/contacts', methods=['GET', 'POST'])
@app.route('/contacts/<int:slug>', methods=['GET', 'POST'])
def contacts(slug = None):
    current_user = get_current_user()
    if slug:
        contactlist = Contacts.query.filter_by(groupId=slug, appId=current_user.appId).all()
        count = Contacts.query.filter_by(groupId=slug,  appId=current_user.appId).count()
        group = Groups.query.get_or_404(slug)

        try:
            group.total = count
            db.session.commit()
        except Exception as e:
            reportError(e)

    else:
        contactlist = Contacts.query.filter_by(appId=current_user.appId).all()
        count = Contacts.query.filter_by(appId=current_user.appId).count()
        group = None
    
    return render_template('contacts.html', current_user=current_user, contactlist=contactlist, count=count, group=group, loadingMessage="Please wait while we process your request, this may take some time." )

@app.route('/issue', methods=['GET', 'POST'])
def issue():
    pass

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    form = TakePayment()
    packages = Package.query.all()
    return render_template('purchase.html', form=form, user=None, loadingMessage="loadingMessage",charges=0.03, packages=packages)

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


@app.route('/purchase/<int:id>', methods=['GET','POST'])
def pay(id):
    print("purchasing package id.")
    package = Package.query.get_or_404(id)
    user = get_current_user
    
    body={
        "userId":1,
        "appId":user.get("appId"),
        "username":user.get("username"),
        "amount":package.price,
        "package":package.price,
        "credits":package.credits,
        "balanceBefore":user.get("balance"),
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


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print('POST REQUEST')
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            print("There was no csvfile found!")
            file = None
        else:
            file = request.files['file']

        name = request.form.get('name','default')
        slug = request.form.get('slug','default')
        appId = request.form.get('appId','default')

        print("name:",name, "slug:",slug)

        if Groups.query.filter_by(slug=slug).first() is None:
            # calculate contacts with the same slug
            total = Contacts.query.filter_by(slug=slug).count()
            newgroup = Groups(name = name, appId=appId, slug=slug, total=total )
            db.session.add(newgroup)
            db.session.commit()

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
                    newcontact = Contacts(name=row[1], phoneNumber=row[2], appId=request.form.get('appId', 'default'), slug=slug, groupId=newgroup.id)
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

    try:
        newReport = Report(rawdata=rawdata, responsedata=reportBody,status=reportBody.get('status', None), appId=reportBody.get('appId', 'default'), contacts=summaryReport.get('contacts', 'default'), sent=summaryReport.get('total_sent', None), rejected=summaryReport.get('total_rejected', None), credit=summaryReport.get('credit_used', None), type=summaryReport.get('type', None), providerId=summaryReport.get('_id', None), message=prestoSummaryReport.get('message', None),  groupName=prestoSummaryReport.get('groupName', None),  groupId=prestoSummaryReport.get('groupId', None), )
        db.session.add(newReport)
        db.session.commit()
    except Exception as e:
        reportError(e)

    print(newReport)

    # newReport = Report(/)
    # take the json
    # create a db entry
    # send an email
    # done.
    return "Done"

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    current_user = get_current_user()

    reports = Report.query.filter_by(appId=current_user.appId).order_by(Report.id.desc()).all()
    reportCount = len(reports)
    return render_template('reports.html', current_user=current_user,reports=reports, count = reportCount)

@app.route('/report/<int:id>', methods=['GET', 'POST'])
def report(id):
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
    return render_template('report.html', report=report, contacts=contacts)

@app.route('/new', methods=['GET', 'POST'])
def new():
    form = AddUserForm()
    form.group.choices = [ (group.id, f"{group.name} - {group.total} contacts" )for group in Groups.query.all()]
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                newContact = Contacts(name=form.name.data, phoneNumber=form.phone.data, appId="appId", slug="slug", groupId = form.group.data )
                db.session.add(newContact)
                db.session.commit()
                flash(f'Your data has been uplaoded successfully')
                return redirect(url_for('contacts', slug=form.group.data))
            
            except Exception as e:
                reportError(e)
        else:
            print(form.errors)

    return render_template('addcontact.html', form=form)


@app.route('/confirm/<string:transactionId>', methods=['GET', 'POST'])
def confirm(transactionId):
    if request.is_json:
        print("-------------- CALLBACK RECIEVED --------------- ")
        print(request.url)
        print("-------------- CALLBACK DATA --------------- ")
        print(request.json)

        message = "In Progress"
        transaction = Transactions.query.get_or_404(transactionId)
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

                    responseMessage = transaction.listing + "\nSuccessfully bought " +str(transaction.amount) + " for " + str(transaction.username) + "." + "\nBefore: " + str(transaction.balanceBefore) + "\nAfter: "+ str(transaction.balanceAfter) + "\nTransactionId:" + str(transaction.id) + "\nAccount:" + str(transaction.network) + " : "+ str(transaction.account) + "\nLedgerId: " + str(entry.id)
                    message = "Student Name:"+ str(transaction.username) + "\nHostel Name: "+transaction.listing + "\nAmount:" + str(transaction.amount) + "\nPayment Method:"+transaction.channel + "\nPayment  Date" + transaction.date_created.strftime("%Y-%m-%d %H:%M:%S") + "\nReceipt Number: PRS" + str(transaction.id) + "REF" + str(transaction.ref) +"\nYour payment has been received successfully!."

                    print("send_sms || PrestoStay)")
                    sendMnotifySms("PrestoHelp",transaction.account, message)

                    print(responseMessage)
                    sendTelegram(responseMessage)
                    sendTelegram(responseMessage, listing.chatId)
                    
                    emails = [ admin.email for admin in User.query.filter_by(role = 'admin').all()]
                    print(emails)

                    sendAnEmail(transaction.username, f'GHC {transaction.amount} SUCCESSFULLY RECIEVED', responseMessage, emails)
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
    senderId = body.get('senderId', 'PrestoHelp')
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        newuser = User(username=form.username.data, email=form.email.data, phone=form.phone.data, password=hashed_password, balance=100, total=100)
        print(newuser)
        try:
            db.session.add(newuser)
            db.session.commit()
            message =  "Congratulations on successfully being onboarded to Presto Connect.\nYou have recieved 100 free sms credits.\n\nIf you need any form of support you can call +233545977791 "
            sendMnotifySms('PrestoHelp', newuser.phone, message)
            sendTelegram(newuser.phone, newuser.username +" : " + newuser.phone + " has onboarded to PrestoPay. \nhttps://stay.prestoghana.com/profile/ \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
            token = login_user(newuser) 

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

if __name__ == '__main__':
    app.run(port=5000,host='0.0.0.0',debug=True)