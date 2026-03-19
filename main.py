import streamlit as st

from db.conversations import get_all_conversations, get_conversation, create_new_conversation, add_message
from services.get_models_list import get_ollama_models_list
from services.get_title import get_chat_title
from services.chat_utilities import get_answer

st.set_page_config(page_title="ChatGPT Clone",page_icon="🤖",layout="centered")
st.title("🤖 ChatGPT Clone")

#-----Models List--------
if "OLLAMA_MODELS" not in st.session_state:
    st.session_state.OLLAMA_MODELS = get_ollama_models_list()
selected_model = st.selectbox("Select Model", st.session_state.OLLAMA_MODELS)


#----------Session State---------
st.session_state.setdefault("conversation_id",None)
st.session_state.setdefault("conversation_title", None)
st.session_state.setdefault("chat_history",[])

#-----------Side bar conversations-----------
with st.sidebar:
    st.header("Chat History")
    conversations = get_all_conversations()

    if st.button("+ New Chat"):
        st.session_state.conversation_id = None
        st.session_state.conversation_title = None
        st.session_state.chat_history = []
    for cid,title in conversations.items():
        is_current = cid == st.session_state.conversation_id
        label = f"**{title}**" if is_current else title
        if st.button(label, key=f"conv_{cid}"):
            doc = get_conversation(cid)
            st.session_state.conversation_id = cid
            st.session_state.conversation_title = doc.get("title","Untitled")
            st.session_state.chat_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in doc.get("messages", [])
            ]


#------------Show Chat so far ----------------
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#--------Chat input -----------
user_query = st.chat_input("Ask AI....")
if user_query:
    # 1. show + store user message in UI state
    st.chat_message("user").markdown(user_query)
    st.session_state.chat_history.append({"role":"user","content":user_query})

    # 2. Persist to DB (create convo on first message else append)
    if st.session_state.conversation_id is None:
        try:
            title = get_chat_title(selected_model,user_query) or "New Chat"
        except Exception:
            title = "New Chat"
        convo_id = create_new_conversation(title=title, role="user", content=user_query)
        st.session_state.conversation_id = convo_id
        st.session_state.conversation_title = title
    else:
        add_message(st.session_state.conversation_id, role="user", content=user_query)

    # 3. Get Assistant Response
    try:
        assistant_text = get_answer(selected_model, st.session_state.chat_history)
    except Exception as e:
        assistant_text = f"Error generating response: {str(e)}"


    # 4. Show + store assistant response
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
    st.session_state.chat_history.append({"role":"assistant", "content":assistant_text})

    # 5. Persist assistant response to DB
    if st.session_state.conversation_id :
        add_message(st.session_state.conversation_id, role="assistant", content=assistant_text)









