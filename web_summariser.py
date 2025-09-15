import streamlit as st
from openai import OpenAI
from bs4 import BeautifulSoup
import requests

# Page configuration
st.set_page_config(
    page_title="Website Summarizer",
    page_icon="📄",
    layout="wide"
)

# Headers for web scraping
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No Title found"
        
        # Remove irrelevant elements
        if soup.body:
            for irrelevant in soup.body(['script', 'style', 'img', 'nav', 'header', 'footer']):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = "No content found"

system_prompt = """You are an assistant that analyzes the contents of a website 
and provides a short summary, ignoring text that might be navigation related. Also ignore the ads on the page.
Respond in markdown."""

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled '{website.title}'"
    user_prompt += "\n\nThe contents of this website is as follows; "
    user_prompt += "please provide a short summary of this website in markdown. "
    user_prompt += "If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(url):
    try:
        # Initialize Ollama OpenAI client
        ollama_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
        
        # Create website object
        website = Website(url)
        
        # Get summary from AI
        response = ollama_openai.chat.completions.create(
            model="llama3.2",
            messages=messages_for(website)
        )
        return response.choices[0].message.content, website.title
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching website: {str(e)}", "Error"
    except Exception as e:
        return f"Error processing request: {str(e)}", "Error"

# Streamlit UI
def main():
    st.title("Website Summarizer")
    st.markdown("Enter a website URL to get an AI-powered summary of its contents.")
    
    # URL input
    url = st.text_input(
        "Website URL:",
        placeholder="https://example.com",
        help="Enter the full URL including http:// or https://"
    )
    
    # Summarize button
    if st.button("Summarize Website", type="primary"):
        if url:
            if not url.startswith(('http://', 'https://')):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                with st.spinner("Analyzing website content..."):
                    summary, title = summarize(url)
                
                # Display results
                st.success("Summary generated successfully!")
                
                # Show website title
                if title != "Error":
                    st.subheader(f"📄 {title}")
                
                # Display summary in markdown
                st.markdown("### Summary:")
                st.markdown(summary)
                
                # Show original URL
                st.markdown(f"**Source:** [{url}]({url})")
        else:
            st.warning("Please enter a website URL")
    
    # Instructions
    with st.expander("How to use"):
        st.markdown("""
        1. Enter a website URL in the text box above
        2. Click the "Summarize Website" button
        3. Wait for the AI to analyze and summarize the content
        4. Review the generated summary
        
        **Note:** Make sure Ollama is running locally on port 11434 with the llama3.2 model installed.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by Ollama and Llama 3.2*")

if __name__ == "__main__":
    main()