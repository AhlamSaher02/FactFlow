import streamlit as st
import google.generativeai as genai
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import spacy
import pandas as pd
import re
from transformers import pipeline
import json
from datetime import datetime
import time
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini API
#   # Store API key in Streamlit secrets
# Load Spacy NLP Model
nlp = spacy.load("en_core_web_trf")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")



def extract_claims(text):
    """Extract claims with improved filtering and deduplication"""
    doc = nlp(text)
    claims = []
    
    for sent in doc.sents:
                  
        # Enhanced claim detection
        has_entity = any(token.ent_type_ for token in sent)
        has_verb = any(token.pos_ == "VERB" for token in sent)
        has_subject = any(token.dep_ in ["nsubj", "nsubjpass"] for token in sent)
        
        # Additional filters for claim quality
        is_question = sent.text.strip().endswith("?")
        has_quote = '"' in sent.text or '"' in sent.text
        
        if has_entity and has_verb and has_subject and not is_question:
            claims.append(sent.text)
            
    
    # Deduplicate and summarize
    claims = list(set(claims))
    
    # Batch process claims for efficiency
    summarized_claims = [summarizer(claim, max_length=50, min_length=20, do_sample=False)[0]['summary_text'] for claim in claims]
    
    
    
    return summarized_claims
# Extract Claims





def analyze_claim_with_gemini(claim):
    """Unified function to handle both evidence search and fact-checking"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        unified_prompt = f"""
        1. Fact check this claim: "{claim}".
        2. Search for specific evidence from reliable sources (include dates, stats, expert opinions).
        3. Analyze the claim based on the evidence.
        4. Provide a JSON response with:
           - verdict (TRUE/FALSE/UNCERTAIN)
           - confidence_score (0-100)
           - explanation (detailed analysis)
           - sources (list of sources with links)
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=unified_prompt,
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
                response_modalities=["TEXT"],
                temperature=0.2
            )
        )

        # Parse response into structured format
        try:
            result = json.loads(response.text)
        except:
            result = {
                "verdict": "UNCERTAIN",
                "confidence_score": 0,
                "explanation": response.text,
                "sources": []
            }

        return result

    except Exception as e:
        st.error(f"Error analyzing claim: {str(e)}")
        return None

