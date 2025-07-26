# Use Python 3.12 as the base image
FROM python:3.12.11-bullseye

# Run in container
RUN mkdir -p /home/app

# Run in Host pc
COPY . /home/app

# Set the working directory in the container to /app
WORKDIR /home/app

#Installing dependencies 
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Running the app.py
CMD ["python3", "app.py"]
