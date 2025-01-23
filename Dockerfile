###    Docker Config   ###


#   Python
FROM python:3.11-slim

#   Set the working directory
WORKDIR /app

# Atualizar o sistema e instalar dependências para Tkinter
RUN apt-get update && apt-get install -y python3-tk x11-apps \
    build-essential \
    libsqlite3-dev \
    tk-dev \
    && apt-get clean

#   Copy the current directory contents into the container at /app
COPY . /app

#   Atualizar o pip e numpy
RUN apt-get update && apt-get install -y python3-tk
RUN pip install --upgrade pip 
RUN pip install --upgrade setuptools==68.0.0
RUN apt-get update && apt-get install -y build-essential
#RUN pip install numpy==1.24.4 --no-build-isolation

#   Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#   Comando padrão para rodar o container
CMD ["python", "GUI.py"]







