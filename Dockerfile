# Imagem base com Python
FROM python:3.11

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos
COPY . .

# Expõe a porta padrão do Cloud Run
EXPOSE 8080

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8080"]
