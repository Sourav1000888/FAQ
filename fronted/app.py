import streamlit as st
import time
import requests, os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from streamlit_extras.stylable_container import stylable_container

# Frequency ask questions

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="FAQ",
    page_icon="❓",
    layout="wide"
)


#css
st.markdown("""
        <style>
         .gray{
            font-size:18px;
            height: 20px;
            color: green;
            margin-bottom:10px;
            }
       
        .error{
            color:red;
            text-size:18px;
            }
        </style>
            """, unsafe_allow_html=True)



# Step 1: Custom CSS for Streamlit Button
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #130a33; 
        color: white;              /* Text Color */
        font-size: 18px;
        font-weight: bold;
        padding: 6px 15px;
        border-radius: 8px;        /* Round Corners */
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    /* Hover effect (Jab mouse button par jaye) */
    div.stButton > button:first-child:hover {
        background-color: #141b59; 
        transform: scale(1.02);    /* thoda bada hoga click karne par */
    }
    </style>
""", unsafe_allow_html=True)



# 1. Inject custom CSS to style the chat input
st.html(
    """
    <style>
    /* Target the overall chat input container */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;       /* Rounded corners */
        background-color: #f0f2f6 !important;  /* Light grey background */
        # padding: 2px !important;
    }

    /* Target the inner textarea / text wrapper */
    div[data-testid="stChatInput"] textarea {
        color: white !important;             /* Text color */
        font-size: 16px !important;            /* Font size */
    }

    /* Target the placeholder text color */
    div[data-testid="stChatInput"] textarea::placeholder {
        color: gray !important;
    }

    /* Target the send button icon */
    div[data-testid="stChatInput"] button {
        background-color: blue !important;  /* Button background color */
        border-radius: 50% !important;         /* Circular button */
    }
    </style>
    """
)


#################### starting ##########################3

st.title("❓ Frequently Asked Questions")
st.markdown("Find answers quickly using the **chat** or **domain filter**.")

# # -------------------------------
# # Sidebar Filters
# # -------------------------------
st.sidebar.header("🔎 Filter FAQs")

refresh = st.sidebar.button(
    'Refresh', use_container_width=True
)


if refresh:
    sessions = ['exact_match', 'suggestions', 'no_match']
    for i in sessions:
        if i in st.session_state:
            del st.session_state[i]
    st.rerun()


domain_filter = st.sidebar.selectbox(
    "Select Domain",
    options=['Financial', 'Insaurance']
)


# if 'exact match' not in st.session_state:
#     st.session_state.exact_match = None

# if 'suggestions' not in st.session_state:
#     st.session_state.suggestions = None

# if 'no match' not in st.session_state:
#     st.session_state.no_match = None

# bakend api logic

st.write(f'For {domain_filter}:')


search_query = st.chat_input('Ask Questions')

load_dotenv()
backend_url = os.environ.get('server_url')

if search_query and domain_filter == "Financial":

    sessions = ['exact_match', 'suggestions', 'no_match']
    for i in sessions:
        if i in st.session_state:
            del st.session_state[i]

    response = requests.get(f'{backend_url}/v1/faq/finance/query', params={'domain' : domain_filter, 'Query' : search_query})

    if response.status_code == 200:
        backend_result = response.json()

        if backend_result['type'] == 'exact_match':
            st.session_state['exact_match'] = backend_result['data']
        
        if backend_result['type'] == 'suggestions':
            st.session_state['suggestions'] = backend_result['data']
        
        if backend_result['type'] == 'no_match':
            st.session_state['no_match'] = backend_result['message']

            

if search_query and domain_filter == 'Insaurance':

    sessions = ['exact_match', 'suggestions', 'no_match']
    for i in sessions:
        if i in st.session_state:
            del st.session_state[i]

    response = requests.get(f'{backend_url}/v1/faq/insurace/query',  params={'domain' : domain_filter, 'Query' : search_query})
    
    if response.status_code == 200:
        backend_result = response.json()
    
        if backend_result['type'] == 'exact_match':
            st.session_state['exact_match'] = backend_result['data']
        
        if backend_result['type'] == 'suggestions':
            st.session_state['suggestions'] = backend_result['data']
         
        if backend_result['type'] == 'no_match':
            st.session_state['no_match'] = backend_result['message']
    else:
        st.warning('problem in response')
          


# ui

def streaming_output(text):
    if text is None:
        text = ''
    else:
        text = str(text)

    for word in text.split(" "):
        yield word + ' '
        time.sleep(0.07)


class validation(BaseModel):
    domain : Optional[str] = None
    question : Optional[str] = None

payload = validation(domain=domain_filter, question=search_query)

if 'exact_match' in st.session_state:
    st.write('### Answer:')
    st.write_stream(stream=streaming_output(st.session_state['exact_match']))

if 'suggestions' in st.session_state and st.session_state['suggestions'] is not None:
    st.write('I am not sure about it, Did you mean this...')

    for index, item in enumerate(st.session_state['suggestions']):
        if st.button(item['question'], key=f'btn_{index}'):
            st.session_state['selected_answer'] = item['Answer']
            st.session_state['none_of_these'] = item['question']
            st.session_state['trigger_stream'] = True  # start streaming
            st.rerun()
        
#data storing -- financial
if st.session_state['none_of_these'] == 'None of these' and domain_filter == 'Financial':
    finance_request = requests.post(url=f'{backend_url}/v1/faq/database/finance/query', json=payload.model_dump())


# data storing -- insurance
elif st.session_state['none_of_these'] == 'None of these' and domain_filter == 'Insaurance':
    insurance_request = requests.post(url=f'{backend_url}/v1/faq/database/insurace/query', json=payload.model_dump())
    

if st.session_state.get('trigger_stream', False):
    st.write('### Answer:')
    st.write_stream(stream=streaming_output(st.session_state['selected_answer']))

    # reverse false trigger
    st.session_state['trigger_stream'] = False
    st.session_state['streamed_already'] = True

# elif st.session_state.get('streamed_already', False):
#     st.write('### Answer:')
#     st.success(st.session_state['selected_answer'])


if 'no_match' in st.session_state:
    st.write('### Answer:')
    st.write_stream(stream=streaming_output(st.session_state['no_match']))











    





