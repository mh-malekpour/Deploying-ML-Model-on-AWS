# Deploying ML Model on AWS

### Overview

This guide outlines the steps for setting up and running the AWS ML Serving project. The project is structured into several folders, each with specific roles:

1. **Infrastructure Folder**: Contains scripts for setting up the AWS infrastructure, including worker and orchestrator instances, and deploying applications on them.
2. **Worker Folder**: Includes a Flask app and Dockerfile to set up two containers (serving ML models on ports 5001 and 5002) on the worker instances.
3. **Orchestrator Folder**: Contains a Flask app and Dockerfile to handle client requests and distribute them across worker instances, running on the orchestrator instance.
4. **Client Folder**: Includes a Python module that can be run on a local PC to send requests to the orchestrator.

### Step-by-Step Instructions

### 1. Setting Up AWS Infrastructure

To set up the AWS infrastructure and create 5 EC2 instances (4 workers and 1 orchestrator), follow these steps:

a. Place your AWS credentials into the appropriate file:

```
~/.aws/credentials
```

b. Clone the repository and navigate to the infrastructure directory:

```
git clone git@github.com:mh-malekpour/Deploying-ML-Model-on-AWS.git
cd Deploying-ML-Model-on-AWS/infrastructure
```

c. Set up a virtual environment and activate it:

```
python -m virtualenv venv
source venv/bin/activate
```

d. Install required dependencies:

```
pip install -r requirements.txt
```

e. Execute the main script to set up the infrastructure:

```
python main.py
```

### 2. Setting Up Workers

To pull codes, install required packages on workers, and deploy the Flask app for serving the ML model using Docker Compose:

```
python workers.py
```

### 3. Setting Up the Orchestrator

To set up the orchestrator for deploying the Flask app, which manages and distributes requests among workers:

```
python orchestrator.py
```

### 4. Sending Requests to the Orchestrator

To send requests from your local PC to the orchestrator:

a. Navigate to the client directory:

```
cd Deploying-ML-Model-on-AWS/client
```

b. Execute the client script:

```
python main.py
```

---
**Note**: Ensure you have the necessary permissions and the latest version of Python installed on your system before proceeding with the setup.
