FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
    tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver - Using fixed stable version
RUN CHROMEDRIVER_VERSION=131.0.6778.108 && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    echo "ChromeDriver installed:" && \
    chromedriver --version && \
    echo "Chrome installed:" && \
    google-chrome --version

# Install Python dependencies
COPY req.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy test files
COPY selenium-tests/ ./selenium-tests/

# Run tests
CMD ["pytest", "selenium-tests/test_todo_app.py", "-v", "-s", "--tb=short"]