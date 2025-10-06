FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ta-lib and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libpq-dev \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library with ARM64 support
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' -O config.guess && \
    wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' -O config.sub && \
    ./configure --prefix=/usr --build=aarch64-unknown-linux-gnu && \
    make && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set library path for TA-Lib
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel numpy

# Try to install TA-Lib Python wrapper, continue if it fails
RUN pip install --no-cache-dir TA-Lib || \
    echo "⚠️  TA-Lib installation failed - continuing without it. Technical indicators will be limited."

# Install all other Python dependencies (excluding ta-lib)
RUN grep -v "^ta-lib" requirements.txt | grep -v "^#" | grep -v "^$" > /tmp/requirements-no-talib.txt && \
    pip install --no-cache-dir -r /tmp/requirements-no-talib.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["python", "main.py"]
