#base
FROM python:3.12.7

#workdir
WORKDIR /FAQ

#copy
COPY . .

#run
RUN pip install --no-cache-dir -r requirements.txt

#port
EXPOSE 8501

#command
CMD ["streamlit", "run", "app15.py", "--server.port=8501", "--server.address=0.0.0.0"]