import eel
import json
import asyncio
import re
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

executor = ThreadPoolExecutor(max_workers=3)

# Function to query Weaviate for phone recommendations based on criteria
async def query_weaviate_for_phones(keywords):
    response = (
        client.query
        .get("Phone", ["name", "description", "price"])
        .with_near_text({"concepts": keywords})
        .with_limit(2)
        .do()
    )
    return response['data']

# Function to extract keywords using Llama2
async def extract_keywords_with_llm(prompt):
    keyword_extraction_prompt = f"Extract important keywords from the following customer query to search in Weaviate: '{prompt}'"
    response = llm(keyword_extraction_prompt, max_tokens=100)['choices'][0]['text']
    
    # Use regular expressions to extract keywords
    keywords = re.findall(r'\b\w+\b', response)
    
    # If the reply doesn't contain satisfactory keywords, regenerate
    if not keywords or len(keywords) < 2:
        response = llm(keyword_extraction_prompt, max_tokens=100)['choices'][0]['text']
        keywords = re.findall(r'\b\w+\b', response)
    
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
    keywords = await extract_keywords_with_llm(prompt)
    
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

# Initialize the database
async def initialize_db():
    # Load phones from JSON into Weaviate
    with open("phones.json", "r") as f:
        data = json.load(f)
        phones = data['phones']  # Access the 'phones' key to get the list of phones
    for phone in phones:
        if isinstance(phone, dict):
            client.data_object.create({
                "name": phone.get("name", ""),
                "description": phone.get("retailPrice", ""),
                "price": phone.get("monthlyPrice", "")
            }, "Phone")

# Main function
async def main():
    await initialize_db()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
    eel.start('index.html')

