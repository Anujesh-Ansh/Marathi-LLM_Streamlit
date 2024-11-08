import streamlit as st
import time  # For adding simulated delay
import requests
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables

from transformers import MBartForConditionalGeneration, MBart50TokenizerFast


load_dotenv()


model_directory = "/Users/anujeshansh/Git/Btech_Project/Model"

tokenizer = MBart50TokenizerFast.from_pretrained(model_directory)
import google.generativeai as gi
from langdetect import detect
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
gi.configure(api_key=MODEL_API_KEY)


generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


chat_model = gi.GenerativeModel(
    model_name="gemini-1.5-flash",  # Simulate using a custom model name
    generation_config=generation_config,
)
model = MBartForConditionalGeneration.from_pretrained(model_directory)


def generate_response(prompt, task_type="summarization"):
    task_instruction = "मला मराठी भाषेत 200 शब्दांपर्यंत " + ("सारांश" if task_type == "summarization" else "प्रश्नाचे उत्तर") + " द्या."
    chat_session = chat_model.start_chat(
        history=[
            {"role": "user", "parts": [task_instruction]},
            {"role": "model", "parts": ["ठीक आहे, मी मराठी भाषेतच 200 शब्दांच्या मर्यादेत उत्तर देईन."]}
        ]
    )
    # Simulate delay
    time.sleep(4)  # Adds a delay to simulate model processing time
    response = chat_session.send_message(prompt)
    return response.text

# User Authentication (Simple Simulation for Demo)
def authenticate(username, password):
    demo_users = {"testuser": "password123", "anujesh": "admin", "aarohi": "admin", "mokshada": "admin", "sakshi": "love"}
    return demo_users.get(username) == password

# Set up login state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Main App Structure
if not st.session_state["logged_in"]:
    st.title("Marathi LLM App 🔒")
    page_selection = st.radio("Choose an option:", ["Login", "Sign Up"])

    if page_selection == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["logged_in"] = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password.")

    elif page_selection == "Sign Up":
        st.subheader("Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if new_username in demo_users:
                st.error("Username already exists. Please choose another.")
            else:
                demo_users[new_username] = new_password
                st.success("Account created successfully! You can now log in.")

else:
    # Main App Code for logged-in users
    st.set_page_config(page_title="Marathi LLM App", page_icon="🤖")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page:", ["ChatBot", "QnA", "Summarization", "User Feedback", "Logout"])

    # Logout Option
    if page == "Logout":
        st.session_state["logged_in"] = False
        st.sidebar.empty()
        st.experimental_rerun()

    # ChatBot Page
    elif page == "ChatBot":
        st.title("💬 Vachanakar - Marathi ChatBot")
        st.caption("🚀 A chatbot for Marathi text generation, question answering, and summarization")
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "Please enter prompt to generate text"}]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            response = generate_response(prompt, "chat")
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)
            else:
                st.error("Error: Unable to generate response")

    # QnA Page
    elif page == "QnA":
        st.title("📖 QnA - Marathi Question Answering")
        st.subheader("Step 1: Enter Content")
        content = st.text_area("Enter the content in Marathi:")

        if "qna_history" not in st.session_state:
            st.session_state.qna_history = []
            st.session_state.current_content = ""

        if content and content != st.session_state.current_content:
            st.session_state.current_content = content
            st.session_state.qna_history.clear()

        if st.session_state.current_content:
            st.success("Content accepted! You can now ask questions based on this content.")

            if st.session_state.qna_history:
                st.write("**Previous Q&A:**")
                for entry in st.session_state.qna_history:
                    st.write(f"**Q:** {entry['question']}")
                    st.write(f"**A:** {entry['answer']}")

            st.subheader("Step 2: Ask a Question")
            question = st.text_input("Enter your question related to the content in Marathi:")

            if question:
                prompt = f"Content: {st.session_state.current_content}\n\nQuestion: {question}"
                response = generate_response(prompt, "qna")
                
                if response:
                    st.write("**Answer:**")
                    st.write(response)
                    st.session_state.qna_history.append({"question": question, "answer": response})
                else:
                    st.error("Error: Unable to generate response")

    elif page == "Summarization":
        st.title("📝 Summarization - Marathi Text Summarization")
        prompt = st.text_area("Enter text to summarize in Marathi:")

        if st.button("Summarize") and prompt:
            response = generate_response(prompt, "summarization")
            if response:
                st.write("**Summary:**")
                st.write(response)
            else:
                st.error("Error: Unable to generate response")

    elif page == "User Feedback":
        st.title("📢 User Feedback")
        st.write("Please provide your feedback below:")

        if "feedback_text" not in st.session_state:
            st.session_state.feedback_text = ""

        feedback = st.text_area("Enter your feedback here:", value=st.session_state.feedback_text, key="feedback")

        if st.button("Submit"):
            if feedback:
                st.success("Thank you for your feedback!")
                st.session_state.feedback_text = ""
            else:
                st.error("Please enter feedback before submitting.")
