# Services Dockerfile (Python/FastAPI development)
FROM python:3.11-slim

# set working directory
WORKDIR /code

# copy and install requirements
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# copy application code
COPY . /code

# expose uvicorn port
EXPOSE 8000

# run uvicorn with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
