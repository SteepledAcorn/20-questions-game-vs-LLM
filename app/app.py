import streamlit as st
import yaml
from client import LLMApiClient

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

api_key = config['API_KEY']
client = LLMApiClient(api_key)

## Begin App ##
st.title("20 Questions vs. AI 🤖")
st.text("""Think of anything and see if AI can guess what you are thinking of! 
To restart the game simply refresh the page.""")

# Hidden context for LLM, not displayed in UI
context_list = config['SYSTEM_CONTEXT']
display_list = config['DISPLAY_QUESTION']

# Game state dictionaries
session_variables = ['hidden_messages', 'messages', 'llm_questions', 'answers', 'bingo']

# Initialise session_state variables
if any(var not in st.session_state for var in session_variables):

    # Hidden context for LLM
    st.session_state.hidden_messages = [{'role': context_list[i]['role'], 'content': context_list[i]['content']} for i in range(len(context_list))]
    # Questions & subsequent messages
    st.session_state.messages = [{'role': display_list[i]['role'], 'content': display_list[i]['content']} for i in range(len(display_list))]
    # List of LLM questions
    st.session_state.llm_questions = [{'role': display_list[i]['role'], 'content': display_list[i]['content']} for i in range(len(display_list))]
    # List of answers
    st.session_state.answers = []
    # Iniatilise bingo boolean (AI wins)
    st.session_state.bingo = False


## Write chat history to UI ##
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# If someone has won, end game. If not, continue
if st.session_state.bingo:
    st.success('AI wins! Refresh the page to play again', icon="✅")
    st.balloons()

elif len(st.session_state.llm_questions) == 20:     
    st.success('Player wins! Question limit reached', icon="✅")
    st.balloons()

else:

    if prompt := st.chat_input("Please answer yes/no or 'bingo' if I have correctly guessed what you were thinking"):
        
        if prompt in ['yes', 'no']:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Combine hidden context and initial message for LLM
                full_message_list = st.session_state.hidden_messages + st.session_state.messages

                # Provide full history to LLM for every response
                response_data = client.chat_completion(
                                model = config['MODEL'], 
                                messages = [
                                    {"role": m["role"], "content": m["content"]}
                                    for m in full_message_list
                                    ],
                                temperature =  config['TEMPERATURE'])

                full_response = response_data['choices'][0]['message']['content']
            
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})
            st.session_state.llm_questions.append({'role': 'assistant', 'content': full_response})

        # Player tells AI it won
        elif prompt == 'bingo':
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            st.success('AI wins! Refresh the page to play again', icon="✅")
            st.balloons()
            st.session_state.bingo = True

        # Ignore invalid input
        else:
            st.error(body = 'Invalid input', icon = '🚨')