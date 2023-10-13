# verizon-qml-customer-service

# Non offical repo by a single open source/freedom software engineer looking to make a change. Build better corporations and better customers as well. 
=
![image](https://github.com/graylan0/verizon-qml-customer-service/assets/34530588/29b4f487-d0b5-4ba5-a7b0-728485465f62)


![image](https://github.com/graylan0/verizon-qml-customer-service/assets/34530588/ec335796-24fd-4ac2-9799-b4443d0d37c8)

## Installation Guide

### Prerequisites

1. **Python**: Make sure Python 3.9 + is installed on your system. [official website](https://www.python.org/downloads/release/python-31013/)
2. **Docker Desktop**: Download and install from the [official website](https://www.docker.com/products/docker-desktop).

### Step-by-Step Instructions

#### Install Required Python Packages

```bash
# Install Eel for GUI
pip install eel

# Install Weaviate Client
pip install weaviate-client

# Install Bark for additional functionalities
pip install git+https://github.com/suno-ai/bark

# Install Llama2 Library
pip install llama-cpp-python==0.1.78
```

#### Set Up Weaviate Vector Database

```bash
# Pull and run Weaviate Docker image
docker run -d --name weaviate -p 8080:8080 weaviate/weaviate
```

#### Clone Project Repository

```bash
# Clone the repository containing index.html and app.py
git clone https://github.com/graylan0/verizon-qml-customer-service
```

#### Run the Application

```bash
# Navigate to the project directory
cd verizon-qml-customer-service

# Run the Python backend
python app.py
```

---

this is how it should look when vectordb load ![image](https://github.com/graylan0/verizon-qml-customer-service/assets/34530588/cb14e3a5-870d-4d59-8071-973ac98d0af9)

After following these steps, the Python backend should launch, and Eel will display the frontend GUI. The application will also connect to the Weaviate vector database running in the Docker container.
