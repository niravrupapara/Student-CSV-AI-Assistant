import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from src.data_loader import load_csv_data
from src.graph import build_student_agent_graph, run_agent_query

# Load environment variables (.env file containing MISTRAL_API_KEY)
load_dotenv()

st.title("Student CSV Agent")

# Sidebar - CSV File Uploader
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

# Initialize Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "dataframe" not in st.session_state: st.session_state.dataframe = None
if "agent_graph" not in st.session_state: st.session_state.agent_graph = None

# Handle CSV Upload
if uploaded_file is not None:
    df = load_csv_data(uploaded_file)
    st.session_state.dataframe = df
    st.session_state.agent_graph = build_student_agent_graph()
    st.success(f"CSV uploaded successfully! Rows: {len(df)}, Columns: {len(df.columns)}")

# Render Chat History
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.write(msg.content)

# Chat Input
user_question = st.chat_input("Ask a question about the schedule...")

if user_question:
    if st.session_state.dataframe is None or st.session_state.agent_graph is None:
        st.error("Please upload a CSV file first.")
    else:
        # Save user question to chat history
        st.session_state.messages.append(HumanMessage(content=user_question))
        with st.chat_message("user"):
            st.write(user_question)

        # Run agent workflow
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = run_agent_query(
                    graph=st.session_state.agent_graph,
                    user_question=user_question,
                    message_history=st.session_state.messages[:-1]
                )
                st.write(answer)
                st.session_state.messages.append(AIMessage(content=answer))
