import streamlit as st
from generate_outline import generate_outline
from improve_writing import improve_writing
from analyze_writing import AcademicWritingStyleAnalyzer  # Import the analyzer class
# from fact_check3 import extract_claims,search_evidence_with_gemini,fact_check_claim
from fact_check3 import analyze_claim_with_gemini,extract_claims
from similar_publications import search_serpapi

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
import language_tool_python
import textstat
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
import re
import logging

# Initialize the analyzer
analyzer = AcademicWritingStyleAnalyzer()

# Set up the page layout
st.set_page_config(page_title="FactFlow", layout="wide")

# CSS for dark theme and styling
st.markdown(
    """
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #121212;
        }
        .stApp {
            background-color: #121212;
        }
        .title-box {
            margin-top: 20px;
            padding: 20px;
            background-color: #1f2937;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        }
        .title-box label {
            color: #e2e8f0;
            font-size: 16px;
        }
        input, textarea {
            background-color: #1e293b !important;
            color: #e2e8f0 !important;
            border: 2px solid #374151 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 16px !important;
        }
        textarea {
            height: 400px !important;
            resize: both !important;
        }
        /* Sidebar */
        .css-1d391kg .css-1lcbmhc {
            background-color: #1f2937;
            color: white;
        }
        .css-1d391kg .css-1lcbmhc button {
            font-size: 16px;
            margin: 10px 0;
            color: white !important;
            background: #4a5568 !important;
            border: none !important;
            border-radius: 6px;
            transition: background 0.3s ease;
        }
        .css-1d391kg .css-1lcbmhc button:hover {
            background: #2d3748 !important;
        }
        /* Output box */
        .output-box {
            margin-top: 20px;
            padding: 20px;
            background-color: #2d3748;
            border-radius: 12px;
            color: #e2e8f0;
            font-size: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Home"
# Sidebar
# with st.sidebar:
#     st.markdown("### FactFlow")
#     st.markdown("#### WRITING TOOLS")
#     generate_outline_button = st.button("📖 Generate Outline")
#     improve_writing_button = st.button("🖋️ Improve Writing", key="improve_writing_button")
#     analyze_writing_button = st.button("📊 Analyze Writing")
#     verify_claims_button =st.button("✔️ Verify Facts")
#     search_publication=st.button("🔍 Find Similar")
with st.sidebar:
    st.markdown("### FactFlow")
    if st.button("📖 Generate Outline"):
        st.session_state.active_page = "Generate Outline"
    if st.button("🖋️ Improve Writing"):
        st.session_state.active_page = "Improve Writing"
    if st.button("📊 Analyze Writing"):
        st.session_state.active_page = "Analyze Writing"
    if st.button("✔️ Verify Facts"):
        st.session_state.active_page = "Verify Claims"
    if st.button("🔍 Find Similar"):
        st.session_state.active_page = "Search Publications"


# Main Content in Vertical Layout
st.markdown("<div class='title-box'>", unsafe_allow_html=True)

# Title input box
article_title = st.text_input("Article Title", placeholder="Enter your article title here...")

# Content text area
article_content = st.text_area("Article Content", placeholder="Start writing your article here...")

st.markdown("</div>", unsafe_allow_html=True)

# Display Generate Outline results in a separate box
def render_generate_outline_button():

    st.markdown("<div class='output-box'>", unsafe_allow_html=True)
    st.markdown("### Suggested Outline")
    outline = generate_outline(article_title)
    if outline:
        for idx, item in enumerate(outline, 1):
            st.markdown(f"**{idx}. {item}**")
    else:
        st.write("No outline could be generated. Please try again.")
    st.markdown("</div>", unsafe_allow_html=True)

# When the "Improve Writing" button is clicked, improve the writing
def render_improve_writing_button():
    st.title(" Results")
    st.markdown("<div class='output-box'>", unsafe_allow_html=True)
    st.markdown("### Improved Writing")
    improved_text = improve_writing(article_content)
    st.write(improved_text)
    st.markdown("</div>", unsafe_allow_html=True)


def render_analyze_writing_page():
    # Initialize the analyzer
    analyzer = AcademicWritingStyleAnalyzer()

    # Streamlit UI
    st.title("📘 Academic Writing Analyzer")
    if article_content.strip():
        st.subheader("📊 Analysis Results")

        # Run analysis
        results = analyzer.analyze_text(article_content)

        ## ---- Display Readability Scores ---- ##
        st.markdown("### 🧑‍🏫 Readability Scores")
        readability_df = pd.DataFrame(results["readability"].items(), columns=["Metric", "Score"])
        st.table(readability_df)

        # Readability Score Visualization
        st.markdown("#### 📊 Readability Score Distribution")
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.barplot(data=readability_df, x="Score", y="Metric", palette="coolwarm", ax=ax)
        ax.set_xlabel("Score")
        ax.set_title("Readability Scores")
        st.pyplot(fig)

        ## ---- Grammar Issues ---- ##
        grammar_issues = results["grammar_issues"]
        st.markdown("### ✍️ Grammar & Style Issues")
        if grammar_issues:
            for issue in grammar_issues[:5]:  # Show first 5 issues
                st.write(f"🔹 **Incorrect:** {issue['incorrect']}")
                st.write(f"💡 **Suggestion:** {', '.join(issue['suggestions']) if issue['suggestions'] else 'No suggestions available.'}")
                st.markdown("---")
        else:
            st.success("✅ No major grammar issues detected.")

        ## ---- Passive Voice Detection ---- ##
        passive_sentences = results["passive_voice"]
        st.markdown("### 🏛 Passive Voice Usage")
        if passive_sentences:
            st.warning(f"⚠️ Detected {len(passive_sentences)} passive voice sentences.")
            for sentence in passive_sentences:
                st.write(f"🔹 **Passive Sentence:** {sentence}")
        else:
            st.success("✅ No passive voice detected!")

        ## ---- Conciseness Suggestions ---- ##
        conciseness_suggestions = results["conciseness_suggestions"]
        st.markdown("### ✂️ Conciseness Suggestions")
        if conciseness_suggestions:
            for suggestion in conciseness_suggestions:
                st.write(f"💡 {suggestion}")
        else:
            st.success("✅ No wordiness issues detected.")

        ## ---- Vocabulary Suggestions ---- ##
        vocab_suggestions = results["vocabulary_suggestions"]
        st.markdown("### 📖 Academic Vocabulary Improvements")
        if vocab_suggestions:
            vocab_df = pd.DataFrame(vocab_suggestions)
            st.table(vocab_df)
        else:
            st.success("✅ No vocabulary improvements needed!")

        ## ---- Word Cloud for Academic Vocabulary ---- ##
        st.markdown("#### ☁️ Word Cloud of Vocabulary Suggestions")
        word_list = [word["word"] for word in vocab_suggestions]
        if word_list:
            wordcloud = WordCloud(width=500, height=300, background_color="white").generate(" ".join(word_list))
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No word replacements suggested for vocabulary improvement.")

        ## ---- Sentence Complexity Visualization ---- ##
        st.markdown("### 🔢 Sentence Complexity Analysis")
        complexity = results["complexity"]
        complexity_df = pd.DataFrame(complexity.items(), columns=["Metric", "Value"])

        fig, ax = plt.subplots(figsize=(2, 3))
        sns.barplot(data=complexity_df, x="Value", y="Metric", palette="viridis", ax=ax)
        ax.set_xlabel("Score")
        ax.set_title("Sentence Complexity Analysis")
        st.pyplot(fig)

        ## ---- Summary of Results ---- ##
        st.markdown("### 📌 Summary of Findings")
        summary = f"""
        - **Grammar Issues:** {len(grammar_issues)}
        - **Passive Voice Sentences:** {len(passive_sentences)}
        - **Conciseness Suggestions:** {len(conciseness_suggestions)}
        - **Complexity Score:** {complexity["complexity_score"]}
        - **Average Sentence Length:** {complexity["average_length"]}
        - **Readability Score (Flesch-Kincaid Grade Level):** {results["readability"]["flesch_kincaid_grade"]}
        """
        st.markdown(summary)

    else:
        st.error("❌ Please enter some text for analysis.")
    
# def render_verify_claims_button():
#     if article_content:
#         with st.spinner("Analyzing article..."):
#             # Extract and display claims
#             claims = extract_claims(article_content)
        
#             if not claims:
#                 st.warning("No clear claims found in the text. Try a longer article or adjust the settings.")
#             else:
#                 # Create tabs for different views
#                 tab1, tab2 = st.tabs(["Claims Analysis", "Detailed Report"])
            
#                 with tab1:
#                     for i, claim in enumerate(claims, 1):
#                         with st.expander(f"Claim {i}: {claim[:100]}..."):
#                             evidence = search_evidence_with_gemini(claim)
#                             if evidence:
#                                 result = fact_check_claim(claim, evidence)
                            
#                                 if result:
                                    
                                
#                                     st.markdown("### Analysis")
#                                     st.write(result["explanation"])
                                
#                                     if result["sources"]:
#                                         st.markdown("### Sources")
#                                         for source in result["sources"]:
#                                             st.markdown(f"- {source}")
            
#                 with tab2:
#                     # Generate comprehensive report
#                     report_data = []
#                     for claim in claims:
#                         evidence = search_evidence_with_gemini(claim)
#                         result = fact_check_claim(claim, evidence)
#                         if result:
#                             report_data.append({
#                                 "Claim": claim,
#                                 "Verdict": result["verdict"],
#                                 "Confidence": result["confidence_score"],
#                                 "Explanation": result["explanation"]
#                             })
                
#                     if report_data:
#                         df = pd.DataFrame(report_data)
#                         st.dataframe(df)
                    
#                         # Export options
#                         csv = df.to_csv(index=False).encode('utf-8')
#                         st.download_button(
#                             "Download Report",
#                             csv,
#                             "fact_check_report.csv",
#                             "text/csv",
#                             key='download-csv'
#                         )


def render_verify_claims_button():
    if article_content:
        with st.spinner("Analyzing article..."):
            claims = extract_claims(article_content)

            if not claims:
                st.warning("No clear claims found in the text. Try a longer article or adjust the settings.")
            else:
                tab1, tab2 = st.tabs(["Claims Analysis", "Detailed Report"])

                with tab1:
                    for i, claim in enumerate(claims, 1):
                        with st.expander(f"Claim {i}: {claim[:100]}..."):
                            result = analyze_claim_with_gemini(claim)
                            if result:
                                st.markdown("### Analysis")
                                st.write(result["explanation"])

                                if result["sources"]:
                                    st.markdown("### Sources")
                                    for source in result["sources"]:
                                        st.markdown(f"- {source}")

                with tab2:
                    report_data = [
                        {
                            "Claim": claim,
                            "Verdict": (result := analyze_claim_with_gemini(claim))["verdict"],
                            "Confidence": result["confidence_score"],
                            "Explanation": result["explanation"]
                        }
                        for claim in claims if (result := analyze_claim_with_gemini(claim))
                    ]

                    if report_data:
                        df = pd.DataFrame(report_data)
                        st.dataframe(df)

                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Report",
                            csv,
                            "fact_check_report.csv",
                            "text/csv",
                            key='download-csv'
                        )



def render_search_publication():
    st.title("Article Search 🔍")

# Input query
    query = st.text_input("Enter a topic or title to search:")
    max_results = st.slider("Number of results to display:", 1, 10, 5)

# Search button
    if st.button("Search"):
        if query:
            st.subheader(f"Results for '{query}':")
            articles = search_serpapi(query, max_results=max_results)
        
            if articles:
                for idx, article in enumerate(articles, 1):
                    st.markdown(f"### {idx}. {article['title']}")
                    st.write(article['snippet'])
                    st.markdown(f"[Read more]({article['url']})")
                    st.write("---")
            else:
                st.warning("No articles found.")
        else:
            st.warning("Please enter a search query.")



    
# The render function will be called when the appropriate page or tab is selected.
def main(): 
    if st.session_state.active_page == "Generate Outline":
        render_generate_outline_button()
    elif st.session_state.active_page == "Improve Writing":
        render_improve_writing_button()
    elif st.session_state.active_page == "Analyze Writing":
        render_analyze_writing_page()
    elif st.session_state.active_page == "Verify Claims":
        render_verify_claims_button()
    elif st.session_state.active_page == "Search Publications":
        render_search_publication()
    else:
        st.info("Welcome to FactFlow! Use the sidebar to navigate.")  
    
if __name__ == "__main__":
    main()
