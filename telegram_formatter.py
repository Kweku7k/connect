"""
Telegram message formatter for PrestoConnect
"""

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
        # Extract the summary from the data
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