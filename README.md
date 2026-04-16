📌 FAQ Retrieval System (BERT + FAISS + SQL) <br>

🚀 Project Overview

This project is an FAQ Retrieval System that returns the most relevant answer for a user query using NLP + Semantic Search + Database integration.

It uses: <br>
BERT for text embeddings <br>
FAISS for fast similarity search <br>
SQL Database for structured FAQ storage and retrieval <br>
3 different datasets for improved generalization <br>

🧠 Problem Statement
Traditional FAQ systems rely on keyword matching which fails when: <br>
User uses different wording <br>
Synonyms are used <br>
Sentence structure changes <br>

👉 This project solves that using semantic search instead of keyword matching.

📊 Datasets Used  <br>
1️⃣ Finance Dataset form kaggle <br>
2️⃣ Programming Dataset from kaggle <br>
3️⃣ Insurance Dataset from kaggle <br>

🗄️ SQL Database Usage
The project uses SQL database to store and manage FAQ data.

📌 Why SQL is used?
Structured storage of un-answered questions
Easy updates & scaling
Acts as source of truth for FAQs

```
📂 Database Schema
CREATE TABLE faq_data (
    domain varchar(255),
    ques varchar(255),
);

📥 Sample Data
INSERT INTO faq_data (domain, ques)
VALUES (
f'{domain}', f'{query}'
);
```
<br>

```
⚙️ System Architecture
User Query
     ↓
Text Preprocessing
     ↓
BERT Embedding Generation
     ↓
FAISS Similarity Search
     ↓
SQL Database Lookup
     ↓
Final Answer Returned
```

🔧 Tech Stack <br>
Python 🐍 <br>
NLP (Transformers) <br>
BERT embeddings <br>
FAISS vector search <br>
SQL (MySQL) <br>
Pandas, NumPy <br>
Streamlit

<br>

🧪 How It Works <br>
All FAQs are converted into embeddings using BERT <br>
Embeddings are stored in FAISS index <br>
User query is converted into embedding <br>
FAISS finds most similar question <br>
SQL database stores only un-answered questions <br>

```
📁 Project Structure
project/
│
├── data/
│   ├── Financial-QA-10k.csv'
│   ├── Programming.csv
│   ├── Insurance_data.csv
│
├── database/
   ├── schema.sql
│
├── embeddings/
│   ├── finance_database.pkl
│   ├── programming_database.pkl
│   ├── insurance_database.pkl
│
├── models/
│   ├── sentence_transformers(all-MiniLM-L6-v2)
│
├── app15.py
├── README.md
```

🚀 Installation & Setup
git clone https://github.com/Sourav1000888/FAQ
cd FAQ

🏃 Run Project
python app15.py
