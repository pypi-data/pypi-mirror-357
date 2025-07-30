# gemini_processor.py
import google.generativeai as genai
import os

def get_suggested_action(query: str, available_actions: dict) -> str:
    """Asks Gemini to map a natural language query to a predefined action."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return "ERROR_API_KEY"

    genai.configure(api_key=api_key) # Configure the SDK with the API key

    # Prepare the list of actions for the prompt
    action_descriptions = "\n".join([f"- {name}: {desc}" for name, desc in available_actions.items()])

    # **Crucial: Crafting the Prompt**
    # Tell Gemini its role, the available actions, the query, and the desired output format.
    prompt = f"""You are an assistant helping translate natural language security queries into specific commands for a GCP security analysis tool.The available commands/checks are:
    {action_descriptions}
    User query: "{query}"
    Based on the user query, identify the most relevant command NAME from the list above.
    Output only the exact command name (e.g., 'list_open_firewalls').
    If no command seems relevant or the query is ambiguous, output 'UNKNOWN'.
    """
    try:
        # Choose a Gemini model 
        model = genai.GenerativeModel("gemini-1.5-flash-latest") # Updated to use GenerativeModel
        response = model.generate_content(prompt) # Use the combined prompt

        # Basic cleanup of the response
        suggested_action = response.text.strip()

        # Validate if the suggestion is one of the known actions or UNKNOWN
        if suggested_action in available_actions or suggested_action == "UNKNOWN":
            return suggested_action
        else:
            # Gemini might hallucinate or return something unexpected
            print(f"Warning: Gemini returned an unexpected action '{suggested_action}'. Treating as UNKNOWN.")
            return "UNKNOWN"

    except Exception as e:
        print(f"Error interacting with Gemini API: {e}")
        # Handle specific API errors if needed (e.g., quota, auth)
        return "ERROR_GEMINI_API"