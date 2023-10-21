qml-customer-service

With Llama2 7B Chat, Weaviate VectorDB , Bark AI Transformers TTS + Custom Colorized Amplitude Quantum Language Model  + Google Speech API Enabled Voice to Text Using Speech Reconigition 

Created by a single open source/freedom software enginee invoking #codenameorca software repository cooperation to build better corporations and better customers as well. 


Quantum Machine Learning. DEMO:


![image](https://github.com/graylan0/customer-qml/assets/34530588/e29a02f0-8eb3-4897-a99e-d8bef91ab8da)


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
cd customer-qml

# Run the Python backend
python app.py
```

---

After following these steps, the Python backend should launch, and Eel will display the frontend GUI. The application will also connect to the Weaviate vector database running in the Docker container.
