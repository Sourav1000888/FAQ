# --- STAGE 1: Main Base Setup ---
FROM python:3.12.7

# Hugging Face permissions ke liye user setting
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# --- STAGE 2: Backend Dependencies ---
# Backend folder se requirements copy karein aur install karein
COPY --chown=user backend/requirements.txt ./requirements_backend.txt
RUN pip install --no-cache-dir -r requirements_backend.txt

# --- STAGE 3: Frontend Dependencies ---
# Frontend folder se requirements copy karein aur install karein
COPY --chown=user fronted/requirements.txt ./requirements_fronted.txt
RUN pip install --no-cache-dir -r requirements_fronted.txt

# --- STAGE 4: Copy All Code ---
# Pura frontend aur backend ka code container mein copy karein
COPY --chown=user . .

# start.sh script ko permission dein
RUN chmod +x start.sh

# Hugging Face default port expose karein
EXPOSE 7860

# Dono apps ko chalane ke liye script run karein
CMD ["./start.sh"]