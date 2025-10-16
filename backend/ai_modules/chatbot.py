"""
Chatbot Demo Module
Purpose: FAQ or customer support bot (rule-based)
Reference: PROMPT.md → AI Sandbox Modules → chatbot_demo
"""

# Placeholder for future chatbot functionality
def get_bot_response(user_message):
    """
    Generate chatbot response for customer queries
    Args:
        user_message: Customer's message/question
    Returns:
        str: Bot response
    """
    # TODO: Implement rule-based chatbot
    responses = {
        "warranty": "Your warranty period is typically 1-2 years depending on the product.",
        "prescription": "Please consult with our optometrist for prescription updates.",
        "default": "Thank you for contacting OptiCare24. How can I help you today?"
    }
    
    for key in responses:
        if key in user_message.lower():
            return responses[key]
    
    return responses["default"]