# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for the database
RUN mkdir -p /app/data

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production


# Expose port 5000
EXPOSE 5000

# Give write permissions to the app directory
RUN chmod -R 777 /app/data

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]
