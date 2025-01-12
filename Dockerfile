# Usar imagen base de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . .

# Comando para ejecutar el bot con gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT main:create_app
