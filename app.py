import eel
import json
import asyncio
import re
import collections
import logging
from concurrent.futures import ThreadPoolExecutor
import numpy as np
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

# Initialize ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=3)

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
        
# Function to run Llama model and query Weaviate for phone recommendations
async def run_llm(prompt):
    agi_prompt = ("You are a Verizon Service Sales Representative AI Ambassador. "
                  "Your job is critical. You are responsible for helping customers, "
                  "especially those who are elderly or not tech-savvy, with their needs. "
                  "Your duties include: \n"
                  "1. Providing accurate and helpful information.\n"
                  "2. Making personalized recommendations.\n"
                  "3. Ensuring customer satisfaction.\n"
                  "4. Offering interactive engagement to keep customers entertained while they wait.\n")
    
    # Extract keywords dynamically from the user's prompt using Llama2
    keywords = await extract_keywords_with_summarization(prompt)
    
    # Query Weaviate for phone recommendations based on the extracted keywords
    recommended_phones = await query_weaviate_for_phones(keywords)
    
    # Prepare the phone recommendations for inclusion in the Llama model prompt
    phone_recommendations = ""
    if recommended_phones:
        for phone in recommended_phones:
            phone_recommendations += f"\n- {phone['name']}: {phone['description']} (Price: {phone['price']})"
    
    query_prompt = f"A customer is looking for a phone and said: '{prompt}'. What are the best 2 phones you recommend and why? Here are some options based on your criteria:{phone_recommendations}"
    
    full_prompt = agi_prompt + query_prompt
    
    # Generate the response using the Llama model
    response = llm(full_prompt, max_tokens=900)['choices'][0]['text']
    
    # Print the Llama model's reply to the console
    print("Llama model's reply:", response)

    return response

# BarkTTS function
def generate_audio_for_sentence(sentence):
    audio = generate_audio(sentence, history_prompt="v2/en_speaker_6")
    file_name = str(uuid.uuid4()) + ".wav"
    write_wav(file_name, SAMPLE_RATE, audio)
    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()

# EEL function to send message to Llama and get a response
@eel.expose
def send_message_to_llama(message):
    response = asyncio.run(run_llm(message))
    generate_audio_for_sentence(response)
    return response


# Entry point of the script
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    eel.start('index.html')
