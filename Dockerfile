FROM zauberzeug/nicegui:latest
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt