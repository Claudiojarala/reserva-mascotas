FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Eliminamos el EXPOSE fijo porque Railway asigna el puerto dinámicamente

# COMANDO CORREGIDO: Usamos el puerto que Railway nos impone en producción
CMD ["streamlit", "run", "app.py", "--server.port", "8050", "--server.address", "0.0.0.0"]
