# Use Python 3.12 as the base image
FROM python:3.12

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

#Installing dependencies 
RUN pip install -r requirements.txt

EXPOSE 5000

# Running the app.py
CMD ["python3", "Server/app.py"]