import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSONB, JSON
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

class Groups(db.Model):
    tablename = ['Groups']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    appId = db.Column(db.String)
    groupId = db.Column(db.String)
    slug = db.Column(db.String)
    total = db.Column(db.Integer, default=0)
    added = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return f"Group('id: {self.id}', 'total:{self.total}', 'slug:{self.slug}')"


class SenderId(db.Model):
    tablename = ['Groups']

    id = db.Column(db.Integer, primary_key=True)
    senderId = db.Column(db.String)
    appId = db.Column(db.String)
    description= db.Column(db.String)
    slug = db.Column(db.String)
    total = db.Column(db.Integer, default=0)
    approved = db.Column(db.Boolean, default=True)
    added = db.Column(db.DateTime, default=datetime.datetime.now())
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
    added = db.Column(db.DateTime, default=datetime.datetime.now())
    api_token = db.Column(db.String, nullable=True)
    def __repr__(self):
        return f"User('id: {self.id}', 'slug:{self.slug}')"


class Package(db.Model):
    tablename = ['Package']

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    count = db.Column(db.Boolean, default=True)

    added = db.Column(db.DateTime, default=datetime.datetime.now())

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
    date = db.Column(db.DateTime, default=datetime.datetime.now())

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

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    
    project_name = db.Column(db.String, nullable=False)
    api_key = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = db.Column(db.Boolean, default=False)
    
    
