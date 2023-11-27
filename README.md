# Serving ML-Based Web Application on AWS

## 1. Introduction

In the dynamic realm of cloud technologies, orchestrating web applications within containerized environments is a common practice for software systems, including ML-based deployments. This project offers hands-on exploration of deploying ML-based web applications using an orchestrator/worker architecture on the AWS cloud platform.

## 2. Background

### Containerization
Containerization, facilitated by technologies such as Docker, allows developers to encapsulate their applications with all necessary dependencies into portable containers. This ensures consistent application performance across different computing environments.

### Containers Orchestration
As applications scale, orchestration becomes essential. It involves managing multiple containers, ensuring scalability, and automating deployment. Tools like Docker-compose and Kubernetes are commonly used for orchestration.

### Main/Worker Architectural Style
In this style, a central entity (main) manages multiple independent virtual computing instances (workers). This design efficiently parallelizes computing scenarios. The main entity distributes tasks, coordinates, and controls, while workers execute tasks independently.

## 3. Methodology
![Architecture Diagram](https://i.ibb.co/9pTqRZr/Screenshot-2023-11-20-at-5-54-52-PM.png)
The goal of this project is to automate the deployment of an ML model using a containerized approach, following the main/worker architectural style. The deployment architecture is shown below. Steps include:

### 1. Develop Docker Files
Create Docker files for both worker and orchestrator. For workers, include a `docker-compose.yaml` file to handle multiple containers on the same instance. These files are available on our GitHub repository.

### 2. Setup Workers
Launch four EC2 instances with m4.large specifications and 32 GB storage. Install Docker and Docker Compose, clone the worker source code, build Docker images, and execute containers. Test the setup at "worker_IP:port1/run_model" and "worker_IP:port2/run_model".

### 3. Setup Orchestrator
Complete the orchestrator code to forward requests to workers. Deploy a single EC2 instance (m4.large, 16GB storage), install Docker, clone source code, build the Docker image, and run it.

## 4. Reproduction Steps

### Setting Up AWS Infrastructure
1. Add AWS credentials to `~/.aws/credentials`.
2. Clone the repository and navigate to the infrastructure directory:
   ```
   git clone git@github.com:mh-malekpour/Deploying-ML-Model-on-AWS.git
   cd Deploying-ML-Model-on-AWS/infrastructure
   ```
3. Set up and activate a virtual environment:
   ```
   python -m virtualenv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Execute the main script to set up the infrastructure:
   ```
   python main.py
   ```

### Setting Up Workers
Execute `python workers.py` to set up workers.

### Setting Up the Orchestrator
Execute `python orchestrator.py` to set up the orchestrator.

### Sending Requests
To send requests to the orchestrator:
1. Navigate to the client directory:
   ```
   cd Deploying-ML-Model-on-AWS/client
   ```
2. Execute the client script:
   ```
   python main.py
   ```

## Conclusion

This project demonstrates the automated deployment of ML-based web Flask applications in a containerized manner, following the main/worker architectural style.
