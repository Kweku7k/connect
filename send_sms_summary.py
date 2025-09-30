"""
Function to send SMS summary to Telegram
"""

from telegram_formatter import format_sms_summary_for_telegram
from app import sendTelegram

def send_sms_summary_to_telegram(summary_data):
    """
    Format SMS summary data and send it to Telegram
    
    Args:
        summary_data (dict): The SMS summary data dictionary
        
    Returns:
        Response: The response from the Telegram API
    """
    # Format the message
    formatted_message = format_sms_summary_for_telegram(summary_data)
    
    # Send the message to Telegram
    response = sendTelegram(formatted_message)
    
    return response

# Example usage:
if __name__ == "__main__":
    # Example SMS summary data
    example_data = {
        'summary': {
            '_id': '09B233CF-6F69-4650-A87F-C7471DA90480',
            'contacts': 1,
            'credit_left': 3635,
            'credit_used': 1,
            'message_id': '20250530233545977791V2',
            'numbers_sent': ['0545977791'],
            'total_rejected': 0,
            'total_sent': 1,
            'type': 'API GROUP SMS'
        }
    }
    
    # Send the summary to Telegram
    send_sms_summary_to_telegram(example_data)