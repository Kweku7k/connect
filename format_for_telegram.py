"""
Example usage of the telegram formatter
"""

from telegram_formatter import format_sms_summary_for_telegram

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

# Format the message
formatted_message = format_sms_summary_for_telegram(example_data)
print(formatted_message)

# This formatted message can be sent to Telegram using the sendTelegram function
# Example: sendTelegram(formatted_message)