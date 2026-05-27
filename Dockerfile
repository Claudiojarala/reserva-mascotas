FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

# COMANDO CORREGIDO: Arranca el servidor de Streamlit en el puerto asignado por Railway
CMD ["streamlit", "run", "app.py", "--server.port", "8050", "--server.address", "0.0.0.0"]
