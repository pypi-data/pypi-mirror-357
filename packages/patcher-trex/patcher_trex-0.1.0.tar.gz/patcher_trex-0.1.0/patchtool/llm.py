import google.generativeai as genai

# Set your Gemini API key here
GOOGLE_API_KEY = "AIzaSyBEhfxX99Pzx9QBL_VvDxrIFt7roJp8qhQ"

genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def autoCorrect_query(query):
    # Updated query to ensure that the order of the code remains the same as the original
    query_manual = """Please correct the code by removing all errors and ensuring that it functions as intended.
Do not add any comments to the reply at all from your side. Do not include the phrase "Here is the corrected code:" at the beginning.
Do not wrap the code in triple single quotes (''' ''') or any other quote marks.
Do not remove any necessary parts of the code. Ensure that the code performs its intended functionality.
Provide the **full corrected code** as output **without** adding any comments, explanations, or extraneous text.
Ensure that all functions, variables, function calls, and any other necessary functionality are included and intact.
Make sure the output is in pure code format, with no comment lines or unnecessary modifications to the structure of the code.
Ensure the order and structure of the code in the corrected version is **exactly the same** as the original code, keeping 
the code in the same sequence, without altering the sequence of function definitions, variables, or function calls.
Ensure that the **number of lines of code in the corrected version** remain **exactly the same** as in the original code, 
**with no lines added or removed**. The number of lines in the corrected code must be identical to the original code.
Preserve all **internal comments** **(comments that already existed in the original code)**.
**Do not add any new comments**. Ensure that **spaces** are preserved, and no unnecessary formatting changes are made.
If any comments are added by the LLM, **they must be removed**, but **existing comments** in the code should remain intact.
"""
    
    chat_completion = model.generate_content(
        query + query_manual
    )

    # Safeguard: Strip extra whitespace and ensure the content is returned as expected
    response = chat_completion.text.strip()
    
    # Ensure the full code is returned, checking if there is any sign of truncation
    if response.endswith('...'):
        print("Warning: The response may be incomplete. Please verify the full code.")
        print(response)
    return response

def make_query(query):
    # Updated query to ensure that the order of the code remains the same as the original

    chat_completion = model.generate_content(
        query
    )

    # Safeguard: Strip extra whitespace and ensure the content is returned as expected
    response = chat_completion.text.strip()
    
    # Ensure the full code is returned, checking if there is any sign of truncation
    if response.endswith('...'):
        print("Warning: The response may be incomplete. Please verify the full code.")
    return response
