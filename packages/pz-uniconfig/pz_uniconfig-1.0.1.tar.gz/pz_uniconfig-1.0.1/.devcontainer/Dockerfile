# .devcontainer/Dockerfile
FROM python:3.13-slim

# ensure that apt-get is non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# install any OS packages you need here
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy only requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project
COPY . .

# Use a non-root user for VS Code
ARG USERNAME=vscode
RUN useradd -m ${USERNAME} \
 && chown -R ${USERNAME}:${USERNAME} /workspace

USER ${USERNAME}

CMD ["bash"]