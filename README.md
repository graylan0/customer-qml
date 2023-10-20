# verizon-qml-customer-service Non Official Customer Developer

With Llama2 7B Chat, Weaviate VectorDB , Bark AI Transformers TTS + Custom Colorized Amplitude Quantum Language Model  + Google Speech API Enabled Voice to Text Using Speech Reconigition 

Created by a single open source/freedom software enginee invoking #codenameorca software repoistory cooperation to build better corporations and better customers as well. 


QUANTUM DEMO:

![image](https://github.com/graylan0/verizon-qml-customer-service/assets/34530588/5b16000e-9a4c-4d6b-9123-ec6b50ed34c1)

![image](https://github.com/graylan0/verizon-qml-customer-service/assets/34530588/d95d4383-1444-4446-aeea-f6407b143d9f)

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

# Install SpeechRecognition Library
pip install SpeechRecognition

# Install Pennylane Library
pip install pennylane

# Install Textblob
pip install textblob

# Install SciPy
pip install SciPy


```

#### Set Up Weaviate Vector Database

```bash
# Pull and run Weaviate Docker image
use the docker-compose.yml located in the repo. (better docs coming) 
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

After following these steps, the Python backend should launch, and Eel will display the frontend GUI. The application will also connect to the Weaviate vector database running in the Docker container.
