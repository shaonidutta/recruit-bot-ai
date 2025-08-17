# Use the official Playwright image with the CORRECT, updated version tag
FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

# Set the working directory inside the container
WORKDIR /code

# Copy and install Python dependencies from requirements.txt
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Download the spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code into the container
COPY . /code

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
