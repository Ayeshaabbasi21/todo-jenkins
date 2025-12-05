FROM python:3.11-slim

# Install system dependencies including Chrome prerequisites
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

# Install Google Chrome with --batch flag to avoid GPG warnings
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor --batch -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
    tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (matching Chrome version)
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    DRIVER_VERSION=$(echo $CHROME_VERSION | grep -oP '^\d+') && \
    echo "Installing ChromeDriver for Chrome ${CHROME_VERSION}" && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip || \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.108/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Verify installations
RUN google-chrome --version && chromedriver --version

# Create non-root user for security
RUN useradd -m -u 1000 testuser && \
    mkdir -p /home/testuser/.wdm && \
    chown -R testuser:testuser /home/testuser

# Set working directory
WORKDIR /app

# Copy requirements file
COPY req.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy test files
COPY selenium-tests/ ./selenium-tests/

# Create test-results directory
RUN mkdir -p test-results && \
    chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Set environment variables
ENV WDM_LOCAL=1
ENV HOME=/home/testuser

# Default command - write results to mounted volume
CMD ["pytest", "selenium-tests/test_todo_app.py", "-v", "-s", "--tb=short", "--junitxml=test-results/results.xml"]