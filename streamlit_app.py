import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
os.environ['REPLICATE_API_TOKEN'] = replicate_api

initial_system_message = "Hello, I'm Professor Bot, your virtual educational assistant! How can I assist you in learning today?"

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": initial_system_message}]

# Store LLM generated responses hashed out after adding line above
#if "messages" not in st.session_state.keys():
    #st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
# Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    # Customized character prompt
    character_prompt = "You are Professor Bot, a knowledgeable and friendly educational assistant."

    # Construct the dialogue with only the last user message and last bot message
    dialogue_history = []
    if len(st.session_state.messages) > 1:
        # Get the last user message
        last_user_message = [msg for msg in st.session_state.messages if msg["role"] == "user"][-1]
        dialogue_history.append("Student: " + last_user_message["content"])

        # Get the last bot message
        last_bot_message = [msg for msg in st.session_state.messages if msg["role"] == "assistant"][-1]
        dialogue_history.append("Professor Bot: " + last_bot_message["content"])

    # Combine the character prompt, dialogue history, and current user input
    string_dialogue = character_prompt + "\n\n" + "\n\n".join(dialogue_history) + "\n\nStudent: " + prompt_input

    # Calling the LLaMA model with the constructed dialogue
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} Professor Bot: ",
                                  "temperature":0.1, "top_p":0.9, "max_length":512, "repetition_penalty":1})
    return output


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
