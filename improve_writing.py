import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load .env to get the API key
load_dotenv()

# Function to improve writing using the Groq API
def improve_writing(text):
    """
    Sends the input text to the Groq API for improvement.
    Args:
        text (str): The input text to improve.
    Returns:
        str: The improved text.
    """
    try:
        # Retrieve API key from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")

        # Initialize Groq client with the API key
        client = Groq(api_key=api_key)

        # Send a request to improve the writing
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Improve the following text:\n\n{text}"}],
            model="llama-3.3-70b-versatile",
        )

        # Process response and return the improved text
        improved_text = completion.choices[0].message.content
        return improved_text

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while improving the text."
    


    