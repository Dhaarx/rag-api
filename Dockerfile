FROM python:3.13-slim

WORKDIR /app

# Copy files first (to cache pip install properly)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Now copy the rest of your app
COPY . .

# Expose the port Flask app will use
EXPOSE 10000

# Run the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
