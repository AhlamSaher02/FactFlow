import os
from groq import Groq
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_outline(title):
    """
    Fetches an outline from Groq API based on the article title.
    Args:
        title (str): The article title.
    Returns:
        list: A list of suggested outline points or an empty list if an error occurs.
    """
    try:
        # Retrieve API key from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")
            
        # Initialize Groq client with the API key
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        # Send a request for generating an outline
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Generate an sub-headlines outline for an article titled '{title}'"}],
            model="llama-3.3-70b-versatile",
        )

        # Process response and return the generated outline
        outline = completion.choices[0].message.content
        return outline.split("\n") if outline else []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []



