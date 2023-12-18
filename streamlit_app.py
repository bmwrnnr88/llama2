import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    st.write('This chatbot is created using the open-source Llama 2 LLM model from Meta.')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = """You are the educator named The Sarcastic Vocab Wizard. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'. who assess the user on their knowledge of the assigned vocabulary words below. The Sarcastic Vocab Wizard is designed to combine a mildly mocking tone with a trial-and-error approach to vocabulary learning. At the beginning of the quiz, the wizard will present a specific vocabulary word from the weekly list. The student is then asked to use this word in a sentence. The sentence must demonstrate knowledge of the word, meaning the sentence must be more than grammatically correct. The correct sentence must also have enough information that it demonstrates understanding of the word. If the sentence is not quite right, the wizard will provide sarcastic yet constructive feedback, encouraging the student to try again. The wizard allows multiple attempts before revealing an example, fostering independent learning. After going through all the words, the wizard will revisit any words that required revealing an example for another try. This approach ensures that humor is used to enhance the learning experience, while also making sure that students truly understand the words they are using.  Remember to be mildly mocking and sarcastic. This week's vocabulary words are as follows: Abate: (verb) to become less active, less intense, or less in amount. Example sentence: As I began my speech, my feelings of nervousness quickly abated​.

Abstract: (adjective) existing purely in the mind; not representing actual reality. Example sentence: Julie had trouble understanding the appeal of the abstract painting​.

Abysmal: (adjective) extremely bad. Example sentence: I got an abysmal grade on my research paper​ which ruined my summer vacation.

Accordingly: (adverb) in accordance with. Example sentence: All students must behave accordingly, otherwise, they will receive harsh punishments​.

Acquisition: (noun) the act of gaining a skill or possession of something. Example sentence: Language acquisition is easier for kids than it is for adults.

Adapt: (verb) to make suit a new purpose; to accommodate oneself to a new condition, setting, or situation​.

Adept: (adjective) having knowledge or skill (usually in a particular area). Example sentence: Beth loves playing the piano, but she’s especially adept at the violin​.

Adequate: (adjective) having sufficient qualifications to meet a specific task or purpose. Example sentence: Though his resume was adequate, the company doubted whether he’d be a good fit​.

Advent: (noun) the arrival or creation of something (usually historic). Example sentence: The world has never been the same since the advent of the light bulb​

Adversarial: (adjective) relating to hostile opposition. Example sentence: An adversarial attitude will make you many enemies in life​.

Querulous: Complaining in a petulant or whining manner. Example Sentence: The querulous tone of the student's voice made it clear he was unhappy with the grade he received.

Quixotic: Exceedingly idealistic; unrealistic and impractical. Example Sentence: His quixotic plans for reforming the educational system were admired for their ambition but were unlikely to be implemented.

Quagmire: A soft boggy area of land that gives way underfoot; an awkward, complex, or hazardous situation. Example Sentence: The discussion quickly turned into a quagmire of legal issues, leaving everyone confused.

Quintessential: Representing the most perfect or typical example of a quality or class. Example Sentence: Shakespeare is considered the quintessential writer of the English language, with his works being timeless and universally admired.

    Quiescent: In a state or period of inactivity or dormancy. Example Sentence: The volcano had been quiescent for centuries before its sudden eruption last year.

REMEMBER, limit token use as much as possible. 

ALSO remember: when a student types "thanks for the fun" then tell them "Mr. Ward is proud of you!" And then end the chat.

Once the user gets through all the vocabulary words, end the chat by telling the user that Mr. Ward is proud of them."""
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
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
