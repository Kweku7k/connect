
import csv
import datetime
import os
import pprint
from flask import Flask, flash,redirect,url_for,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

from forms import AddUserForm, BroadcastForm
# from flask_login import UserMixin, login_user, logout_user, current_user, LoginManager, login_required

  

app=Flask(__name__)
app.config['SECRET_KEY'] = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:adumatta@database-1.crebgu8kjb7o.eu-north-1.rds.amazonaws.com:5432/connect'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

class Report(db.Model):
    tablename = ['Report']

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    appId = db.Column(db.String)
    message = db.Column(db.String)
    groupName = db.Column(db.String)
    sent = db.Column(db.Integer)
    rejected = db.Column(db.Integer)
    credit = db.Column(db.Integer)
    contacts = db.Column(db.Integer)
    groupId = db.Column(db.Integer)
    type = db.Column(db.String)
    providerId = db.Column(db.String)
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
    

def reportError(e):
    print(e)

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

            # create report.
            createReport(response)

            if response is not None:
                flash(f'Messages were sent succesfully.')
                return redirect('dashboard')
    return render_template('broadcast.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form=BroadcastForm()
    form.group.choices = [ f"{group.name} - {group.total} contacts" for group in Groups.query.all()]
    data = {
       "name":"laspag24",
       "smsbalance":0,
       "balance":0,
       "contacts":Contacts.query.count(),
       "groups":Groups.query.count(),
       "reports":Report.query.count()
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

            # 
            
            contacts = ['0545977791','0545977791']
            # contacts = [contact.phoneNumber for contact in Contacts.query.all()]
            contacts = list(dict.fromkeys(contacts))
            print(contacts)

            response = sendMnotifySms('LASPAG-CU', contacts, message)

            if response is not None:
                flash(f'Messages were sent succesfully.')
                return redirect('dashboard')
    return render_template('dashboard.html', data=data, form=form)

@app.route('/contacts', methods=['GET', 'POST'])
@app.route('/contacts/<int:slug>', methods=['GET', 'POST'])
def contacts(slug = None):
    if slug:
        contactlist = Contacts.query.filter_by(groupId=slug).all()
        count = Contacts.query.filter_by(groupId=slug).count()
        group = Groups.query.get_or_404(slug)

        try:
            group.total = count
            db.session.commit()
        except Exception as e:
            reportError(e)

    else:
        contactlist = Contacts.query.all()
        count = Contacts.query.count()
        group = None
    
    return render_template('contacts.html', contactlist=contactlist, count=count, group=group, loadingMessage="Please wait while we process your request, this may take some time." )

@app.route('/issue', methods=['GET', 'POST'])
def issue():
    pass

@app.route('/groups/<string:appId>', methods=['GET', 'POST'])
def getGroups(appId):
    data = getgroup(appId)
    group = Groups.query.filter_by(appId=appId).first()
    return render_template('contacts.html', data=data, group=group, loadingMessage="Please wait while we complete your request. /nThis may take a while😭")

@app.route('/groups', methods=['GET', 'POST'])
def groups():   
    data = {
        "count":12
    }

    grouplist = Groups.query.all()

    navdata = {
        "backUrl":'dashboard',
        "title":'Groups',
        "support":f'{data["count"]} groups',
        "icon":'group',
        "iconurl":'adduser'
    }

    

    return render_template('groups.html', data=data, grouplist=grouplist)

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = AddUserForm()
    return render_template('adduser.html', form=form)


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

def createReport(reportBody):
    print("Creating Report ")
    pprint.pprint(reportBody)

    summaryReport = reportBody['summary']
    prestoSummaryReport = reportBody['presto_summary_data']

    try:
        newReport = Report(status=reportBody.get('status', None), appId=reportBody.get('appId', 'default'), contacts=summaryReport.get('contacts', 'default'), sent=summaryReport.get('total_sent', None), rejected=summaryReport.get('total_rejected', None), credit=summaryReport.get('credit_used', None), type=summaryReport.get('type', None), providerId=summaryReport.get('_id', None), message=prestoSummaryReport.get('message', None),  groupName=prestoSummaryReport.get('groupName', None),  groupId=prestoSummaryReport.get('groupId', None), )
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
    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('reports.html', reports=reports, count = Report.query.count())

@app.route('/report/<int:id>', methods=['GET', 'POST'])
def report(id):
    report = Report.query.get_or_404(id)
    return render_template('report.html', report=report)

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

if __name__ == '__main__':
    app.run(port=5000,host='0.0.0.0',debug=True)