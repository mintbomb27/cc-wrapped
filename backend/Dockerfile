# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
# This assumes the Dockerfile is in the 'backend' directory and
# the application code is also within 'backend'.
COPY . /app

# Install any needed packages specified in requirements.txt
# If your project doesn't use requirements.txt, you can remove or modify this line.
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
# Change this to the port your backend application listens on.
EXPOSE 8000

# Define environment variable for production
ENV PYTHONUNBUFFERED 1

# Run the application
# Replace 'app.py' with your main backend application file and
# adjust the command if you use a different server (e.g., gunicorn, uvicorn).
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "2", "--threads", "2", "--timeout", "120"]