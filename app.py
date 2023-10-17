import eel
import asyncio
import re
import speech_recognition as sr
import time
import collections
import threading
import logging
from textblob import TextBlob
from pennylane import numpy as np
import pennylane as qml
from concurrent.futures import ThreadPoolExecutor
import sounddevice as sd
import uuid
from scipy.io.wavfile import write as write_wav
from llama_cpp import Llama
from bark import generate_audio, SAMPLE_RATE  # Assuming you have Bark installed
from weaviate import Client
# Initialize EEL with the web folder
eel.init('web')

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Weaviate client
client = Client("http://localhost:8080")

# Initialize Llama model
llm = Llama(
    model_path="llama-2-7b-chat.ggmlv3.q8_0.bin",
    n_gpu_layers=-1,
    n_ctx=3900,
)

# Initialize a quantum device
dev = qml.device("default.qubit", wires=4)

# Initialize ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=3)

# Initialize variables for speech recognition
is_listening = False
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Function to start/stop speech recognition
@eel.expose
def set_speech_recognition_state(state):
    global is_listening
    is_listening = state

# Function to run continuous speech recognition
def continuous_speech_recognition():
    global is_listening
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            if is_listening:
                try:
                    audio_data = recognizer.listen(source, timeout=1)
                    text = audio_to_text(audio_data)  # Convert audio to text
                    if text not in ["Could not understand audio", ""]:
                        asyncio.run(run_llm(text))
                        eel.update_chat_box(f"User: {text}")
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    eel.update_chat_box(f"An error occurred: {e}")
            else:
                time.sleep(1)

# Start the continuous speech recognition in a separate thread
thread = threading.Thread(target=continuous_speech_recognition)
thread.daemon = True  # Set daemon to True
thread.start()

async def query_weaviate_for_phones(keywords):
    try:
        query = {
            "operator": "Or",
            "operands": [
                {
                    "path": ["description"],
                    "operator": "Like",
                    "valueString": keyword
                } for keyword in keywords
            ]
        }
        results = (
            client.query
            .get('Phone', ['name', 'description', 'price'])
            .with_where(query)
            .do()
        )
        
        if 'data' in results and 'Get' in results['data']:
            return results['data']['Get']['Phone']
        else:
            return []
    except Exception as e:
        logging.error(f"An error occurred while querying Weaviate: {e}")
        return []

async def update_weaviate_with_quantum_state(quantum_state):
    try:
        # Assume 'CustomerSupport' is the class name in Weaviate schema
        # Generate a unique ID for each quantum state; you can use any other method to generate a unique ID
        unique_id = str(uuid.uuid4())
        client.data_object.create(
            {
                "class": "CustomerSupport",
                "id": unique_id,
                "properties": {
                    "quantumState": list(quantum_state)  # Convert numpy array to list
                }
            }
        )
    except Exception as e:
        logging.error(f"An error occurred while updating Weaviate: {e}")


def audio_to_text(audio_data):
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results; {e}"
    
# Function to extract keywords using summarization technique
async def extract_keywords_with_summarization(prompt):
    # Tokenize the text into individual words
    words = re.findall(r'\b\w+\b', prompt.lower())
    
    # Define a set of stop words to ignore
    stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"])
    
    # Remove stop words
    filtered_words = [word for word in words if word not in stop_words]
    
    # Always include the keyword "phone" for better context
    filtered_words.append("phone")
    
    # Count the frequency of each word
    word_count = collections.Counter(filtered_words)
    
    # Find the 5 most common words
    common_words = word_count.most_common(5)
    
    # Extract just the words from the list of tuples
    keywords = [word[0] for word in common_words]
    
    # Print the extracted keywords to the console
    print("Extracted keywords:", keywords)
    
    return keywords

async def summarize_to_color_code(prompt):
    # Use TextBlob to analyze the sentiment of the prompt for amplitude
    analysis = TextBlob(prompt)
    sentiment_score = analysis.sentiment.polarity

    # Normalize the sentiment score to an amplitude between 0 and 1
    amplitude = (sentiment_score + 1) / 2

    # Initialize color_code to None
    color_code = None

    # Loop to keep trying until a valid color code is found
    while color_code is None:
        color_prompt = "Generate a single map to emotion html color code based upon the following text;" + prompt
        color_response = llm(color_prompt, max_tokens=350)['choices'][0]['text'].strip()
        # Print the Llama model's reply to the console
        print("Llama model's reply:", color_response)
        # Use advanced regex to find a color code in the Llama2 response
        match = re.search(r'#[0-9a-fA-F]{6}', color_response)
        if match:
            color_code = match.group(0)
        else:
            print("Retrying to get a valid color code...")

    return color_code, amplitude        

async def run_llm(prompt):
    # Summarize the user's reply into a color code and amplitude
    color_code, amplitude = await summarize_to_color_code(prompt)

    # Generate quantum state based on the color code and amplitude
    quantum_state = quantum_circuit(color_code, amplitude).numpy()
    
    # Update the GUI with the quantum state before generating Llama model's reply
    eel.update_chat_box(f"Quantum State based on User's Reply: {quantum_state}")

    # Check if the user's prompt is related to phone recommendations
    if 'phone' in prompt.lower():
        # Extract keywords dynamically from the user's prompt
        keywords = await extract_keywords_with_summarization(prompt)
        
        # Query Weaviate for phone recommendations based on the extracted keywords
        recommended_phones = await query_weaviate_for_phones(keywords)
        
        # Prepare the phone recommendations for inclusion in the Llama model prompt
        phone_recommendations = ""
        if recommended_phones:
            for phone in recommended_phones:
                phone_recommendations += f"\n- {phone['name']}: {phone['description']} (Price: {phone['price']})"
        
        query_prompt = f"A customer is looking for a phone and said: '{prompt}'. What are the best 2 phones you recommend and why? Here are some options based on your criteria:{phone_recommendations}"
    else:
        query_prompt = f"Please analyze the user's input as {quantum_state}. This is the amplitude: {amplitude}. Provide insights into understanding the customer's dynamic emotional condition."
    
    agi_prompt = ("You are a Verizon Service Sales Representative AI Ambassador. "
                  "Your job is critical. You are responsible for helping customers, "
                  "especially those who are elderly or not tech-savvy, with their needs. "
                  "Your duties include: \n"
                  "1. Providing accurate and helpful information.\n"
                  "2. Making personalized recommendations.\n"
                  "3. Ensuring customer satisfaction.\n"
                  "4. Offering interactive engagement to keep customers entertained while they wait.\n")
    
    full_prompt = agi_prompt + query_prompt
    
    # Generate the response using the Llama model
    response = llm(full_prompt, max_tokens=900)['choices'][0]['text']
    
    # Update the GUI with the Llama model's reply
    eel.update_chat_box(f"AI: {response}")
    await update_weaviate_with_quantum_state(quantum_state)
    # Convert the Llama model's reply to speech
    generate_and_play_audio(response)

# Function to generate audio for each sentence and add pauses
def generate_audio_for_sentence(sentence):
    audio = generate_audio(sentence, history_prompt="v2/en_speaker_6")
    silence = np.zeros(int(0.75 * SAMPLE_RATE))  # quarter second of silence
    return np.concatenate([audio, silence])

# Function to generate and play audio for a message
def generate_and_play_audio(message):
    sentences = re.split('(?<=[.!?]) +', message)
    audio_arrays = []
    
    for sentence in sentences:
        audio_arrays.append(generate_audio_for_sentence(sentence))
        
    audio = np.concatenate(audio_arrays)
    
    file_name = str(uuid.uuid4()) + ".wav"
    write_wav(file_name, SAMPLE_RATE, audio)
    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()

def sentiment_to_amplitude(text):
    analysis = TextBlob(text)
    return (analysis.sentiment.polarity + 1) / 2

@qml.qnode(dev)
def quantum_circuit(color_code, amplitude):
    r, g, b = [int(color_code[i:i+2], 16) for i in (1, 3, 5)]
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    qml.RY(r * np.pi, wires=0)
    qml.RY(g * np.pi, wires=1)
    qml.RY(b * np.pi, wires=2)
    qml.RY(amplitude * np.pi, wires=3)
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    qml.CNOT(wires=[2, 3])
    return qml.state()

# EEL function to send message to Llama and get a response
@eel.expose
def send_message_to_llama(message):
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(run_llm(message))
    generate_and_play_audio(response)  # Changed this line to use the new function
    return response


# Entry point of the script
if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()
        eel.start('index.html')
    except KeyboardInterrupt:
        print("Exiting program...")
        # Perform any necessary cleanup here
        exit(0)
