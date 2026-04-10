import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
import joblib, re
import os
import pymysql


# Frequency ask questions

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="FAQ Center",
    page_icon="❓",
    layout="wide"
)


# load model and dataframes
@st.cache_resource
def load_pretrained_model():
    if os.path.exists('./faq_model'):
        model = SentenceTransformer('./faq_model')
        print('model load successfully ')
    else:
        print('folder not found')

    #load fiass database
    finance_database = joblib.load('finance_database.pkl')
    program_database = joblib.load('programming_database.pkl')
    insurance_database = joblib.load('insurance_database.pkl')

    # load dataframe
    finance_df = joblib.load('finance_df.pkl')
    program_df = joblib.load('programming_df.pkl')
    insurance_df = joblib.load('insurance_df.pkl')

    return model, finance_database, finance_df, program_database, program_df, insurance_database, insurance_df


model, finance_database, finance_df, program_database, program_df, insurance_database, insurance_df  = load_pretrained_model()


# database
def save_to_db(domain, query):
    try:
        con = pymysql.Connect(host='localhost', user='root', password='admin', database='faq')
        cur = con.cursor()
        cur.execute(f"insert into un_answered_query (domain, query) values ('{domain}', '{query}')")
        con.commit()
        # con.close()
        return 'success'
    except:
        return 'fail to save'
    

# text cleaning
def text_preprocessing_query(text):
    if text is None:
        return ''
    # convert in lower case
    text = text.lower()
    # remove html tags
    text = re.sub(r'<.*?>', '', text)
    # remove punctuations
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


#css
st.markdown("""
        <style>
         .gray{
            font-size:18px;
            height: 20px;
            color: green;
            }
       
        .error{
            color:red;
            text-size:18px;
            }
        </style>
            """, unsafe_allow_html=True)


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
    st.rerun()


domain_filter = st.sidebar.selectbox(
    "Select Domain",
    options=['Financial', 'Programming', 'Insaurance']
)



if 'answer' not in st.session_state:
    st.session_state['answer'] = None

if 'option' not in st.session_state:
    st.session_state['option'] = []


def faq_match(ques, choose):
    # preprocessing input query
    ques = text_preprocessing_query(ques)
    #generate embeddings
    query_embedding = model.encode([ques])

    # domain conditions
    if choose == 'Financial':  
        similarity, index = finance_database.search(query_embedding, k=1)
        if similarity[0][0] >= 0.85:
            result = f"{finance_df['answer'].loc[index[0][0]]} {finance_df['context'].loc[index[0][0]]}"
            st.session_state['answer'] = result
        
        elif similarity[0][0] >= 60 or similarity[0][0] < 85:
            dis, idx = finance_database.search(query_embedding, k=3)

            ques1 = finance_df['question'].loc[idx[0][0]]
            ques1_embedding = model.encode([ques1])
            d, i = finance_database.search(ques1_embedding, k=1)
            ans1 = finance_df['context'].iloc[i[0][0]]

            ques2 = finance_df['question'].loc[idx[0][1]]
            ques2_embedding = model.encode([ques2])
            d, i = finance_database.search(ques2_embedding, k=1)
            ans2 = finance_df['context'].iloc[i[0][0]]

            ques3 = finance_df['question'].loc[idx[0][2]]
            ques3_embedding = model.encode([ques3])
            d, i = finance_database.search(ques3_embedding, k=1)
            ans3 = finance_df['context'].iloc[i[0][0]]

            st.session_state['option'] = [
            {'question' : f'{ques1}', 
                'Answer' : f'{ans1}'},
            {'question' : f'{ques2}', 
                'Answer' : f'{ans2}'},
            {'question' : f'{ques3}', 
                'Answer' : f'{ans3}'},
            {'question' : 'None of these',
                'Answer' : 'No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..'}
        ]
               
        else:
            save_to_db(domain_filter, ques)
            st.success('No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..')

            
    elif choose == 'Programming':
        similarity, index = program_database.search(query_embedding, k=1)
        if similarity[0][0] >= 0.85:
            result = program_df['Body'].iloc[index[0][0]]
            st.session_state['answer'] = result
        
        elif similarity[0][0] >= 60 or similarity[0][0] < 85:
            dis, idx = program_database.search(query_embedding, k=3)

            ques1 = program_df['Title'].loc[idx[0][0]]
            ques1_embedding = model.encode([ques1])
            d, i = program_database.search(ques1_embedding, k=1)
            ans1 = program_df['Body'].iloc[i[0][0]]
            
            ques2 = program_df['Title'].loc[idx[0][1]]
            ques2_embedding = model.encode([ques2])
            d, i = program_database.search(ques2_embedding, k=1)
            ans2 = program_df['Body'].iloc[i[0][0]]
            
            ques3 = program_df['Title'].loc[idx[0][2]]
            ques3_embedding = model.encode([ques3])
            d, i = program_database.search(ques3_embedding, k=1)
            ans3 =  program_df['Body'].iloc[i[0][0]]
            
            st.session_state['option'] = [
            {'question' : f'{ques1}', 
                'Answer' : f'{ans1}'},
            {'question' : f'{ques2}', 
                'Answer' : f'{ans2}'},
            {'question' : f'{ques3}', 
                'Answer' : f'{ans3}'},
            {'question' : 'None of these',
                'Answer' : 'No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..'}
        ]
            
        else:
            save_to_db(domain_filter, ques)
            st.warning('No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..')


    elif choose == 'Insaurance':
        similarity, index = insurance_database.search(query_embedding, k=1)
        if similarity[0][0] >= 0.85:
            result = insurance_df['ground_truth'].iloc[index[0][0]]
            st.session_state['answer'] = result
        
        elif similarity[0][0] >= 60 or similarity[0][0] < 85:
            dis, idx = insurance_database.search(query_embedding, k=3)

            ques1 = insurance_df['input'].loc[idx[0][0]]
            ques1_embedding = model.encode([ques1])
            d, i = insurance_database.search(ques1_embedding, k=1)
            ans1 = insurance_df['ground_truth'].iloc[i[0][0]]
            
            ques2 = insurance_df['input'].loc[idx[0][1]]
            ques2_embedding = model.encode([ques2])
            d, i = insurance_database.search(ques2_embedding, k=1)
            ans2 = insurance_df['ground_truth'].iloc[i[0][0]]
            
            ques3 = insurance_df['input'].loc[idx[0][2]]
            ques3_embedding = model.encode([ques3])
            d, i = insurance_database.search(ques3_embedding, k=1)
            ans3 = insurance_df['ground_truth'].iloc[i[0][0]]
            
            st.session_state['option'] = [
            {'question' : f'{ques1}', 
                'Answer' : f'{ans1}'},
            {'question' : f'{ques2}', 
                'Answer' : f'{ans2}'},
            {'question' : f'{ques3}', 
                'Answer' : f'{ans3}'},
            {'question' : 'None of these',
                'Answer' : 'No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..'}
        ]
        
        else:
            save_to_db(domain_filter, ques)
            st.warning('No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..')

    else:
        pass


# display logic

st.write(f'For {domain_filter}:')
search_query = st.chat_input('Ask Questions')

with st.container(border=True, height=300):
    if search_query:
        st.session_state.search_query = search_query
        st.session_state['answer'] = None
        st.session_state['option'] = []
        st.session_state['suggest_query'] = None
        faq_match(search_query, domain_filter)

    if st.session_state['answer'] and st.session_state.suggest_query:
        if st.session_state['answer'] != 'No Information about this Query \n Your query is added in databased \n We will reply in 2 hours \n Thank you..':
            st.write(f'<p class="gray"> Ques: {st.session_state.suggest_query}? </p>', unsafe_allow_html=True)
            st.write(f'Ans: {st.session_state['answer']}')
        else:
            st.write(f'<p class="gray"> Ques: {st.session_state.search_query}? </p>', unsafe_allow_html=True)
            st.write(f'<p class="error">{st.session_state['answer']} </p>', unsafe_allow_html=True)

    elif st.session_state['answer']:
        st.write(f'<p class="gray"> Ques: {st.session_state.search_query}? </p>', unsafe_allow_html=True)
        st.write(f'Ans: {st.session_state['answer']}')
        
    elif st.session_state['option']:
        st.markdown("<p class='gray'> Not sure, are you asking about </p>", unsafe_allow_html=True)

        for i, item in enumerate(st.session_state['option']):
            if st.button(item['question'], key=f'btn_{i}'):
                st.session_state.suggest_query = item['question']

                if item['question'] == 'None of these':
                   save_to_db(domain_filter, st.session_state.search_query)
                st.session_state['answer'] = item['Answer']        
                st.rerun()    
    
    else:
        pass


    





