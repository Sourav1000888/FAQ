from fastapi import FastAPI, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import text
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, re
from sentence_transformers import SentenceTransformer
import joblib

load_dotenv()

@asynccontextmanager
async def life_spanning(app : FastAPI):
    global model, finance_df, finance_database, insurance_database, insurance_df, conn1, conn2
    model = SentenceTransformer('all-MiniLM-L6-v2')
    #load fiass database
    finance_database = joblib.load('data_and_file/finance_database.pkl')
    insurance_database = joblib.load('data_and_file/insurance_database.pkl')

    # load dataframe
    finance_df = joblib.load('data_and_file/finance_df.pkl')
    insurance_df = joblib.load('data_and_file/insurance_df.pkl')

    backend_url_1 = os.environ.get('database_url_1')
    backend_url_2 = os.environ.get('database_url_2')

    conn1 = sqlalchemy.create_engine(url=f'{backend_url_1}')
    conn2 = sqlalchemy.create_engine(url=f'{backend_url_2}')
    try:
        with conn1.begin() as connection:
            connection.execute(
                text("CREATE TABLE IF NOT EXISTS finance (id SERIAL PRIMARY KEY, domain TEXT, un_answered_query TEXT)"))

            connection.commit()
    except Exception as e:
        print(f'{e}')
    
    try:
        with conn2.begin() as connection:
            connection.execute(
                text("CREATE TABLE IF NOT EXISTS insurance (id SERIAL PRIMARY KEY, domain TEXT, un_answered_query TEXT)"))

            connection.commit()
    except Exception as e:
        print(f'{e}')

    yield

app = FastAPI(title='faq backend', lifespan=life_spanning)



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

origins = os.environ.get('origins')

app.add_middleware(
    CORSMiddleware, allow_origins=f'{origins}', allow_methods=['GET', 'POST'], 
    allow_headers=['*'], allow_credentials=True
)


class validation(BaseModel):
    domain : str
    question : str

@app.post('/v1/faq/database/finance/query')
def starting_database_finance(data : validation, back : BackgroundTasks):
    back.add_task(insert_into_finance_database, data)
    return JSONResponse(status_code=200, content='Saved')

def insert_into_finance_database(data : validation):
    try:
        with conn1.begin() as connection:
            connection.execute(
                text("""INSERT INTO finance (domain, un_answered_query) VALUES 
                     (:domain, :un_answered_query);"""), 
                     {"domain" : data.domain, "un_answered_query" : data.question}
            )
            connection.commit()
        return JSONResponse(status_code=200, content='saved in database')
    except Exception as e:
        return JSONResponse(content=f'{e}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE)



@app.post('/v1/faq/database/insurace/query')
def starting_database_insurance(data : validation, back : BackgroundTasks):
    back.add_task(insert_into_insurace_database, data)
    return JSONResponse(status_code=200, content='Saved')

def insert_into_insurace_database(data : validation):
    try:
        with conn2.begin() as connection:
            connection.execute(
                text("""INSERT INTO insurance (domain, un_answered_query) VALUES 
                     (:domain, :un_answered_query);"""), 
                     {"domain" : data.domain, "un_answered_query" : data.question}
            )

            connection.commit()
        return JSONResponse(status_code=200, content='saved in database')
    except Exception as e:
        return JSONResponse(content=f'{e}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


            
@app.get('/v1/faq/insurace/query')
def respond_insurance_query(domain:str, Query:str):

    if domain == 'Insaurance':
        # preprocessing input query
        question = text_preprocessing_query(Query)
        #generate embeddings
        query_embedding = model.encode([question])
        
        similarity, index = insurance_database.search(query_embedding, k=1)
        if similarity[0][0] >= 0.90:
            result = insurance_df['ground_truth'].iloc[index[0][0]]
            return {
                'type' : 'exact_match',
                'status_code' : 200,
                'data' : result,
                'Score' : round(float(similarity[0][0]), 2)
            }
        
        elif similarity[0][0] >= 0.70:
            dis, idx = insurance_database.search(query_embedding, k=3)

            ques1 = insurance_df['input'].loc[idx[0][0]]
            ques1_embedding = model.encode([ques1])
            d1, i = insurance_database.search(ques1_embedding, k=1)
            ans1 = insurance_df['ground_truth'].iloc[i[0][0]]
            
            ques2 = insurance_df['input'].loc[idx[0][1]]
            ques2_embedding = model.encode([ques2])
            d2, i = insurance_database.search(ques2_embedding, k=1)
            ans2 = insurance_df['ground_truth'].iloc[i[0][0]]
            
            ques3 = insurance_df['input'].loc[idx[0][2]]
            ques3_embedding = model.encode([ques3])
            d3, i = insurance_database.search(ques3_embedding, k=1)
            ans3 = insurance_df['ground_truth'].iloc[i[0][0]]
            
            suggestion_list = [
                {'question' : f'{ques1}', 
                    'Answer' : f'{ans1}',
                    'Score' : round(float(d1[0][0]), 2)
                },
                {'question' : f'{ques2}', 
                    'Answer' : f'{ans2}',
                    'Score' : round(float(d2[0][0]), 2)
                },
                {'question' : f'{ques3}', 
                    'Answer' : f'{ans3}',
                    'Score' : round(float(d3[0][0]), 2)
                },
                {'question' : 'None of these',
                    'Answer' : 'No Information about this Query Your query is added in databased We will reply in 2 hours Thank you..'
                }
            ]

            return {
                'type' : 'suggestions',
                'status_code' : 200,
                'data' : suggestion_list,
                'message' : 'I am not sure about it, Did you mena this..'
            }

        
        else:
            payload = validation(domain=domain, question=question)
            insert_into_insurace_database(payload)
            return {
                'type' : 'no_match',
                'status_code' : 200,
                'message' : 'No Information about this Query Your query is added in databased We will reply in 2 hours Thank you..'
            }
    else:
        pass



@app.get('/v1/faq/finance/query')
def responsed_finance_query(domain:str, Query:str):
    # domain conditions
    if domain == 'Financial':  
        # preprocessing input query
        question = text_preprocessing_query(Query)
        #generate embeddings
        query_embedding = model.encode([question])

        similarity, index = finance_database.search(query_embedding, k=1)
        if similarity[0][0] >= 0.90:
            result = f"{finance_df['context'].loc[index[0][0]]}"
            return {
                'type' : 'exact_match',
                'status_code' : 200,
                'data' : result,
                'Score' : round(float(similarity[0][0]), 2)
            }
        
        elif similarity[0][0] >= 0.70:
            distance, idx = finance_database.search(query_embedding, k=3)
           
            ques1 = finance_df['question'].loc[idx[0][0]]
            ques1_embedding = model.encode([ques1])
            d1, i = finance_database.search(ques1_embedding, k=1)
            ans1 = finance_df['context'].iloc[i[0][0]]

            ques2 = finance_df['question'].loc[idx[0][1]]
            ques2_embedding = model.encode([ques2])
            d2, i = finance_database.search(ques2_embedding, k=1)
            ans2 = finance_df['context'].iloc[i[0][0]]

            ques3 = finance_df['question'].loc[idx[0][2]]
            ques3_embedding = model.encode([ques3])
            d3, i = finance_database.search(ques3_embedding, k=1)
            ans3 = finance_df['context'].iloc[i[0][0]]

            suggestion_list = [
                {'question' : f'{ques1}', 
                    'Answer' : f'{ans1}',
                    'Score' : round(float(d1[0][0]), 2)
                },
                {'question' : f'{ques2}', 
                    'Answer' : f'{ans2}',
                    'Score' : round(float(d2[0][0]), 2)
                },
                {'question' : f'{ques3}', 
                    'Answer' : f'{ans3}',
                    'Score' : round(float(d3[0][0]), 2)
                },
                {'question' : 'None of these',
                    'Answer' : 'No Information about this Query Your query is added in databased We will reply in 2 hours Thank you..'
                }
            ]

            return {
                'type' : 'suggestions',
                'status_code' : 200,
                'data' : suggestion_list,
                'message' : 'I am not sure about it, Did you mena this..'
            }
            
               
        else:
            payload = validation(domain=domain, question=question)
            insert_into_finance_database(payload)
            return {
                'type' : 'no_match',
                'status_code' : 200,
                'message' : 'No Information about this Query Your query is added in databased We will reply in 2 hours Thank you..'
            }
