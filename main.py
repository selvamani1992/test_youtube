import streamlit as st
from rag_utils import indexing, generate_answer
st.title("YouTube Video Question Answering System")
st.set_page_config(page_title="YouTube Q&A", layout="wide")

#session state 
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    video_url = st.text_input("Enter YouTube Video URL:")
    if video_url and st.button("Process Video"):
        with st.spinner("Processing..."):
            try:
                vector_db = indexing(video_url)
                st.session_state.vector_db = vector_db
                st.success("Video indexed successfully! You can now ask questions about the video.")
            except Exception as e:
                st.error(f"Error processing video: {e}")

if st.session_state.vector_db:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        query = st.chat_input("Ask a question about the video:")
        if query:
            with st.chat_message("user"):
                st.write(query)
                st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("assistant"):
                with st.spinner("Generating answer..."):
                    answer = generate_answer(st.session_state.vector_db, query)
                    st.write(f"Answer: {answer}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()

