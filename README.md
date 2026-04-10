📌 FAQ Retrieval System (BERT + FAISS + SQL)
🚀 Project Overview

This project is an FAQ Retrieval System that returns the most relevant answer for a user query using NLP + Semantic Search + Database integration.

It uses:
BERT for text embeddings
FAISS for fast similarity search
SQL Database for structured FAQ storage and retrieval
3 different datasets for improved generalization

🧠 Problem Statement
Traditional FAQ systems rely on keyword matching which fails when:
User uses different wording
Synonyms are used
Sentence structure changes

👉 This project solves that using semantic search instead of keyword matching.

📊 Datasets Used 
1️⃣ Finance Dataset form kaggle
2️⃣ Programming Dataset from kaggle
3️⃣ Insurance Dataset from kaggle

🗄️ SQL Database Usage
The project uses SQL database to store and manage FAQ data.

📌 Why SQL is used?
Structured storage of un-answered questions
Easy updates & scaling
Acts as source of truth for FAQs

📂 Database Schema
CREATE TABLE faq_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    embedding_id INT
);
📥 Sample Data
INSERT INTO faq_data (question, answer, category)
VALUES (
'What is machine learning?',
'Machine learning is a subset of AI that allows systems to learn from data.',
'AI'
);


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


🔧 Tech Stack
Python 🐍
NLP (Transformers)
BERT embeddings
FAISS vector search
SQL (MySQL)
Pandas, NumPy
Streamlit

🧪 How It Works
All FAQs are converted into embeddings using BERT
Embeddings are stored in FAISS index
User query is converted into embedding
FAISS finds most similar question
SQL database stores only un-answered questions

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
│   ├── 📁faq_model
│
├── app15.py
├── README.md


🚀 Installation & Setup
git clone https://github.com/FAQ
cd FAQ

🏃 Run Project
python app15.py
