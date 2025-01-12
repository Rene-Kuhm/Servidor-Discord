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

# Usar puerto dinámico o por defecto
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} main:create_app
