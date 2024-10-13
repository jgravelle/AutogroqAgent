import streamlit as st
import os
from dotenv import load_dotenv
from pocketgroq import GroqProvider
from pocketgroq.autonomous_agent import AutonomousAgent

# Load environment variables
load_dotenv()

# List of available Groq models
GROQ_MODELS = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
    "llama3-8b-4096",
    "llama3-70b-4096",
    "llava-v1.5-7b-4096-preview",
    "llama3-8b-16384",
    "llama3-70b-16384",
    "llama3-2.7b-8192",
    "mixtral-8x7b-32768"
]

def get_groq_api_key():
    if 'groq_api_key' not in st.session_state:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            api_key = st.text_input("Enter your Groq API Key:", type="password")
            if api_key:
                st.session_state['groq_api_key'] = api_key
        else:
            st.session_state['groq_api_key'] = api_key
    return st.session_state.get('groq_api_key')

def initialize_agent(api_key, model, temperature):
    if api_key:
        groq_provider = GroqProvider(api_key=api_key)
        return AutonomousAgent(groq_provider, model=model, temperature=temperature)
    return None

def main():
    st.title("AutogroqAgent Chat")

    api_key = get_groq_api_key()

    if not api_key:
        st.warning("Please enter a valid Groq API Key to continue.")
        return

    # Model selection dropdown
    default_model = "llama3-8b-8192"
    selected_model = st.selectbox("Select Model:", GROQ_MODELS, index=GROQ_MODELS.index(default_model))

    # Temperature slider
    temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

    agent = initialize_agent(api_key, selected_model, temperature)

    if not agent:
        st.warning("Failed to initialize the agent. Please check your API key.")
        return

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is your question?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            research_steps = []
            
            for step in agent.process_request(prompt):
                if isinstance(step, dict) and 'type' in step:
                    if step['type'] == 'research':
                        research_steps.append(step['content'])
                    elif step['type'] == 'response':
                        full_response += step['content']
                        message_placeholder.markdown(full_response)
                else:
                    full_response += step
                    message_placeholder.markdown(full_response)
            
            if research_steps:
                with st.expander("View research process"):
                    for i, step in enumerate(research_steps, 1):
                        st.markdown(f"**Step {i}:** {step}")

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()