FROM jenkins/jenkins:lts

USER root

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
 && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
 && rm kubectl

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip \
 && unzip awscliv2.zip \
 && ./aws/install \
 && rm -rf aws awscliv2.zip

USER jenkins