
from functools import wraps
import pprint
from flask import flash, jsonify, redirect, request, session, url_for
import requests
from models import *
from config import Config

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
        "callbackUrl":Config.baseUrl+"/confirm/"+str(transaction.id)
    }

    print(paymentInfo)

    try:   
        print("prestoUrl")
        print(Config.prestoUrl)
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
        print(Config.prestoUrl)
        r = requests.get(Config.prestoUrl + '/verifykorbapayment/'+str(transaction.ref)).json()
    except Exception as e:
        print(e)
    
    print(r)
    print("--------------status--------------")
    status = r.get("status", "failed")
    print(status)

    print("--------------server--------------")
    print(Config.server)

    print("--------------transaction channel--------------")
    print(transaction.channel)

    if status == 'success' or Config.environment == 'DEV' and Config.server == "LOCAL" or transaction.channel == 'BANK':

        print("Attempting to update transctionId: " +str(transaction.id) + " to paid! in " + Config.environment + "environment || SERVER:" + Config.server)
        
        # findtrasaction, again because of the lag.
        state = Transactions.query.get_or_404(transaction.id)
        if state.paid != True:
            try:
                state.paid = True
                db.session.commit()
                print("Transaction : "+str(transaction.id) + " has been updated to paid!")

            except Exception as e:
                print("Failed to update transctionId: "+str(transaction.id )+ " to paid!")
                # app.logger.error(e)
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
        # app.logger.error(e)
        reportError(str(e))
        # app.logger.error("Couldnt create ledgerEntry for " + transaction.username)

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
        # app.logger.error("Updating user " + user.username + " balance has failed." )
        # app.logger.error(e)
        reportError(str(e))

    return newLedgerEntry

def format_sms_summary_for_telegram(summary_data):
    """
    Format SMS summary data into a readable Telegram message
    
    Args:
        summary_data (dict): The SMS summary data dictionary
        
    Returns:
        str: Formatted message for Telegram
    """
    if not summary_data or not isinstance(summary_data, dict):
        return "Error: Invalid SMS summary data"
    
    try:
        summary = summary_data.get('summary', {})
        
        # Format the message
        message_lines = [
            "📱 *SMS DELIVERY REPORT* 📱",
            "",
            f"🆔 Message ID: `{summary.get('message_id', 'N/A')}`",
            f"📊 Type: {summary.get('type', 'N/A')}",
            f"✅ Sent: {summary.get('total_sent', 0)}",
            f"❌ Rejected: {summary.get('total_rejected', 0)}",
            f"👥 Total Contacts: {summary.get('contacts', 0)}",
            f"💰 Credit Used: {summary.get('credit_used', 0)}",
            f"💳 Credit Left: {summary.get('credit_left', 0)}",
            "",
            "📱 Numbers Sent:"
        ]
        
        # Add the numbers that were sent successfully
        numbers_sent = summary.get('numbers_sent', [])
        if numbers_sent:
            for number in numbers_sent[:5]:  # Limit to first 5 numbers
                message_lines.append(f"  • {number}")
            
            if len(numbers_sent) > 5:
                message_lines.append(f"  • ...and {len(numbers_sent) - 5} more")
        else:
            message_lines.append("  • None")
            
        return "\n".join(message_lines)
    except Exception as e:
        return f"Error formatting SMS summary: {str(e)}"

def sendTelegram(message_text, chat_id=Config.chat_id):
    params = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'Markdown'  # Enable markdown formatting
    }
    pprint.pprint(params)

    try:
        response = requests.post(url = f'https://api.telegram.org/bot{Config.telegramToken}/sendMessage', params=params)
        return response
    except Exception as e:
        reportError(e)
        return e
    
def get_all_sender_ids(current_user):
    all_sender_id = SenderId.query.filter_by(appId=current_user.appId).all()
    print(all_sender_id)
    return all_sender_id
    
  
