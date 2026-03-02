import streamlit as st

from retrieval.store import VectorStore
from retrieval.retriever import retrieve_context
from chat.qa_chain import answer_with_citations


def render_chat(store: VectorStore) -> None:
    """Render chat messages and input; on submit, retrieve, generate answer, show with sources."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.caption(msg["sources"])

    if prompt := st.chat_input("Ask a question about the lease..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "sources": None})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching and answering..."):
                chunks = retrieve_context(store, prompt)
                if not chunks:
                    response = "No relevant sections were found in the document for this question."
                    sources_line = "None"
                else:
                    response, sources_line = answer_with_citations(chunks, prompt)
                st.markdown(response)
                st.caption(sources_line)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": sources_line,
        })
