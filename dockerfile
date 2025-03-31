# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files, excluding the virtual environment
COPY . .

# Remove the virtual environment directory
RUN rm -rf gemini-backend-env

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application
CMD ["python", "run.py"]