import subprocess
import sys
import streamlit as st

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
    together_client = Together(api_key=api_key)

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

        try:
            # Create a chat completion request, including conversation history as context
            response = together_client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                messages=[
                    {
                        "role": "system",
                        "content": create_system_prompt()
                    }
                ] + conversation_history,  # Only pass the last user + assistant pair for context
                max_tokens=699,
                temperature=0.11,  # Low temperature for less random answers
                top_p=1,  # Nucleus sampling
                top_k=50,  # Top K sampling to limit choices
                repetition_penalty=1,  # Prevent repetition
                stop=["<|eot_id|>"]
            )

            # Get the assistant's response
            assistant_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

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
