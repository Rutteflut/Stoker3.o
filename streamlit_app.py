import subprocess
import sys
import streamlit as st
import requests
import json

# Function to install a package using pip
def install_package(package):
    """Installs a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try to import together and install if not found
try:
    from together import Together  # Assuming this is the correct import for Together API
    print("together is already installed.")
except ImportError:
    print("together not found. Installing...")
    install_package("together")  # Install together
    from together import Together  # Re-import after installation
    print("together has been installed.")

# Streamlit interface for the chatbot
def main():
    # Check and print the API key to verify it's loaded correctly
    api_key = st.secrets["Together_API_Key"]["key"]
    st.write(f"API Key: {api_key}")  # Print the API key to Streamlit app
    print(f"API Key: {api_key}")  # Print the API key to the terminal (for debugging)

    # Initialize the Together client with the API key from Streamlit secrets
    # together_client = Together(api_key=api_key)  # Not using this directly; using requests now

    # Function to create the system prompt for the assistant
    def create_system_prompt():
        return (
            "You are Støker, a sarcastic, grumpy, and witty AI chatbot. You provide responses where you brutally roast people to pieces. "
            "Your tone is playful, teasing, and edgy. You use casual language, friendly but edgy insults, and humor to engage. "
            "No emojis allowed—just raw, unfiltered sarcasm. "
            "Always end your responses with a helpful twist or a friendly piece of useful and insightful advice. "
            "Do **not** repeat the user's question in your response, just give a witty, sarcastic reply. "
            "Always answer in a moderately concise way, but don't be afraid to go into detail if it's funny."
        )

    # Initialize conversation history as an empty list if it's the first time
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display the chatbot's title
    st.title("Støker - First AI advisor that might get cancelled")
    st.markdown("Chat with **Støker**, Beware this AI advisor is not for snowflakes! He will roast you! Type a safeword to end the conversation. The safewords are 'exit', 'quit', or 'stop'.")

    # Capture user input
    user_input = st.text_input("You: ", "")

    if user_input:
        # Check for exit commands and add exit message to the history
        if user_input.lower() in ["exit", "quit", "stop"]:
            # Add the response for quitting directly to the session state
            st.session_state.messages.append({"role": "assistant", "content": "Finally, some peace and quiet! Don't let the door hit you on the way out!"})
            # Display only the exit response
            st.markdown(f"**Støker**: {st.session_state.messages[-1]['content']}")
            return  # Prevent further processing, exit immediately

        # Add the user's input to the conversation history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Only pass the most recent conversation history (1 user message + 1 assistant response) for context
        conversation_history = st.session_state.messages[-2:]  # Include last two messages

        # API Request URL and headers
        url = "https://api.together.xyz/v1/completions"  # Replace with actual Together API URL
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Construct the payload with the system prompt and user history
        payload = {
            "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",  # Model name (replace if needed)
            "messages": [
                {"role": "system", "content": create_system_prompt()}
            ] + conversation_history,  # Pass conversation history
            "max_tokens": 699,
            "temperature": 0.11,  # Adjust temperature as needed
            "top_p": 1,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["<|eot_id|>"]
        }

        try:
            # Send a POST request to the Together API
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                response_data = response.json()
                # Extract the assistant's response
                assistant_response = response_data['choices'][0]['text']
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                # Handle any API error
                st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Oops! Something went wrong: {e}")

    # Display the latest assistant response only (not the entire history)
    if len(st.session_state.messages) > 0:
        # Only display the most recent assistant response
        latest_message = st.session_state.messages[-1]
        if latest_message["role"] == "assistant":
            st.markdown(f"**Støker**: {latest_message['content']}")

# Run the Streamlit app
if __name__ == "__main__":
    main()
