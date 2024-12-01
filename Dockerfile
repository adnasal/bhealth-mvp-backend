# Use the official Python 3.10 image as a base
FROM python:3.10

# Set working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"

# Install necessary system dependencies, including Netcat, Postgres client, and utilities
RUN set -x && \
    apt-get update && \
    apt-get install -y \
    wget \
    curl \
    netcat-openbsd \
    postgresql-client \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pyenv to manage Python versions
RUN curl https://pyenv.run | bash

# Add pyenv to the PATH
ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:$PATH"

# Install Python 3.9 using pyenv
RUN pyenv install 3.9.6 && pyenv global 3.9.6

# Install Poetry globally via the official install script
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy application dependencies and configuration files
COPY pyproject.toml poetry.lock /app/

# Set Poetry to use Python 3.9 for the project
RUN poetry env use python3.9

# Install dependencies using Poetry
RUN poetry install --no-interaction

# Add the Python path to include the app directory (if required)
ENV PYTHONPATH="${PYTHONPATH}:/app/bhealthapp"

# Copy the rest of the application code
COPY . /app/

# Expose the application port (e.g., for a Django app)
EXPOSE 8000

# Command to run your application (adjust to your needs, for Django example)
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
