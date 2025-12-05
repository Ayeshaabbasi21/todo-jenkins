FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Use Python slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
ARG CHROMEDRIVER_VERSION=131.0.6778.108
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Add a non-root user
RUN useradd -m -u 1000 testuser && mkdir -p /home/testuser/.wdm && chown -R testuser:testuser /home/testuser

# Copy requirements
COPY req.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy tests
COPY selenium-tests/ ./selenium-tests/
RUN chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Default command (can be overridden by Jenkins)
CMD ["pytest", "selenium-tests/test_todo_app.py", "-v", "-s", "--tb=short", "--junitxml=test-results.xml"]

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
    tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver - Using fixed stable version matching Chrome
RUN CHROMEDRIVER_VERSION=131.0.6778.108 && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    echo "ChromeDriver installed:" && \
    chromedriver --version && \
    echo "Chrome installed:" && \
    google-chrome --version

# Create a non-root user for running tests
RUN useradd -m -u 1000 testuser && \
    mkdir -p /home/testuser/.wdm && \
    chown -R testuser:testuser /home/testuser

# Install Python dependencies
COPY req.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy test files
COPY selenium-tests/ ./selenium-tests/

# Change ownership to testuser
RUN chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Set environment variables
ENV WDM_LOCAL=1
ENV HOME=/home/testuser

# Run tests
CMD ["pytest", "selenium-tests/test_todo_app.py", "-v", "-s", "--tb=short", "--junitxml=test-results.xml"]