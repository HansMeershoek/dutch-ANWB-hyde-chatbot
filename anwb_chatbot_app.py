import streamlit as st
import os
import base64
from typing import List, Any, Optional
from langchain_core.documents import Document
from langchain_core.callbacks.manager import Callbacks, CallbackManagerForRetrieverRun
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models.llms import LLM
from langchain_core.embeddings import Embeddings
import traceback
from pydantic import PrivateAttr

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Load and encode image as base64 (not used)
def get_image_as_base64(path):
    if not os.path.exists(path):
        print(f"Warning: Logo image not found at {path}")
        return None
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Custom retriever using HyDE (hypothetical document embeddings)
class HydeRetriever(BaseRetriever):
    vectorstore: FAISS
    embeddings_for_hyde: Embeddings
    k_docs: int = 4
    _llm_for_hyde: LLM = PrivateAttr()

    def __init__(self, llm_for_hyde: LLM, **kwargs: Any):
        super().__init__(**kwargs)
        self._llm_for_hyde = llm_for_hyde

    class Config:
        arbitrary_types_allowed = True

    def _generate_hypothetical_answer(self, query: str, run_manager: CallbackManagerForRetrieverRun) -> str:
        hyde_prompt_text = (
            "You are an AI assistant. Based on the ANWB Wegenwacht Service terms and conditions, "
            "generate a hypothetical but plausible answer to the following user question. "
            "This answer will be used to find relevant documents.\n"
            f"User Question: {query}\nHypothetical Answer:"
        )
        try:
            if not self._llm_for_hyde:
                 raise ValueError("LLM for HyDE not initialized properly in HydeRetriever.")
            ai_message = self._llm_for_hyde.invoke(
                hyde_prompt_text,
                callbacks=run_manager.get_child()
            )
            return ai_message.content if hasattr(ai_message, 'content') else str(ai_message)
        except Exception as e:
            print(f"Error generating hypothetical answer: {e}")
            print(traceback.format_exc())
            return query

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun, **kwargs: Any
    ) -> List[Document]:
        # Use HyDE to generate a hypothetical answer, embed it, and retrieve docs
        hypothetical_answer = self._generate_hypothetical_answer(query, run_manager=run_manager)
        hyde_embedding = self.embeddings_for_hyde.embed_query(hypothetical_answer)
        docs = self.vectorstore.similarity_search_by_vector(embedding=hyde_embedding, k=self.k_docs)
        for doc in docs:
            if doc.metadata is None:
                 doc.metadata = {}
            doc.metadata['retrieved_with_hyde_answer'] = hypothetical_answer
        return docs

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun, **kwargs: Any
    ) -> List[Document]:
        # Async version (falls back to sync if needed)
        if not self._llm_for_hyde or not hasattr(self._llm_for_hyde, 'ainvoke'):
            return self._get_relevant_documents(query, run_manager=run_manager, **kwargs)
        hypothetical_answer_message = await self._llm_for_hyde.ainvoke(
            "You are an AI assistant. Based on the ANWB Wegenwacht Service terms and conditions, "
            "generate a hypothetical but plausible answer to the following user question. "
            "This answer will be used to find relevant documents.\n"
            f"User Question: {query}\nHypothetical Answer:",
            callbacks=run_manager.get_child()
        )
        hypothetical_answer = hypothetical_answer_message.content if hasattr(hypothetical_answer_message, 'content') else str(hypothetical_answer_message)
        if not hasattr(self.embeddings_for_hyde, 'aembed_query'):
            hyde_embedding = self.embeddings_for_hyde.embed_query(hypothetical_answer)
        else:
            hyde_embedding = await self.embeddings_for_hyde.aembed_query(hypothetical_answer)
        return self.vectorstore.similarity_search_by_vector(embedding=hyde_embedding, k=self.k_docs)

# Logo and title
logo_path_candidates = [
    os.path.join(os.path.dirname(__file__), "ANWB_logo_wit.jpg") if "__file__" in locals() else "ANWB_logo_wit.jpg",
    os.path.join(os.getcwd(), "ANWB_logo_wit.jpg"),
    os.path.join("/content/", "ANWB_logo_wit.jpg")
]
logo_path = next((p for p in logo_path_candidates if os.path.exists(p)), None)

col1, col2 = st.columns([1, 5])
with col1:
    if logo_path:
        st.image(logo_path, width=80)
with col2:
    st.title("Voorwaarden VHV-BU 2025")

# Sidebar: package and supplement selection
default_package = "Niet gespecificeerd"
default_supplement = "Geen supplement"
package_options = [
    default_package,
    "Wegenwacht Europa Instap", "Wegenwacht Europa Standaard", "Wegenwacht Europa Compleet",
    "Wegenwacht Europa Plus Instap", "Wegenwacht Europa Plus Standaard", "Wegenwacht Europa Plus Compleet"
]
supplement_options = [
    default_supplement,
    "Aanhangwagen Service Buitenland", "Kampeerauto Service Buitenland"
]

with st.sidebar:
    st.header("Context Selection (Optional)")
    if 'selected_package' not in st.session_state:
        st.session_state.selected_package = default_package
    if 'selected_supplement' not in st.session_state:
        st.session_state.selected_supplement = default_supplement
    st.session_state.selected_package = st.selectbox(
        "Select Package:",
        package_options,
        index=package_options.index(st.session_state.selected_package)
    )
    st.session_state.selected_supplement = st.selectbox(
        "Select Supplement:",
        supplement_options,
        index=supplement_options.index(st.session_state.selected_supplement)
    )
    st.caption("Leave on 'Niet gespecificeerd' and 'Geen supplement' for general questions.")

# LLM (Groq) setup
groq_api_key_from_env = os.environ.get('GROQ_API_FOR_STREAMLIT')
if not groq_api_key_from_env:
    st.error("Groq API Key (GROQ_API_FOR_STREAMLIT) is not set as an environment variable.")
    st.stop()
try:
    llm_instance = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=groq_api_key_from_env,
        temperature=0.2,
        top_p=0.9,
    )
    st.sidebar.success("Groq LLM initialized.")
except Exception as e:
    st.error(f"Error initializing ChatGroq: {e}")
    st.text(traceback.format_exc())
    st.stop()

# Embedding model setup
embedding_model_naam = "intfloat/multilingual-e5-large"
embeddings_instance = HuggingFaceEmbeddings(model_name=embedding_model_naam)
st.sidebar.success("Embedding model initialized.")

# Load FAISS vector DB
current_script_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
faiss_index_path = os.path.join(current_script_dir, "faiss_index")
if not os.path.exists(faiss_index_path) or not os.path.isdir(faiss_index_path):
    if os.path.exists("/content/faiss_index") and os.path.isdir("/content/faiss_index"):
        faiss_index_path = "/content/faiss_index"
        st.sidebar.info(f"FAISS index loaded from Colab path: {faiss_index_path}")
    else:
        st.error(f"FAISS index directory not found. Expected at: '{faiss_index_path}' or '/content/faiss_index'.")
        st.stop()
try:
    vector_db_instance = FAISS.load_local(
        faiss_index_path,
        embeddings_instance,
        allow_dangerous_deserialization=True
    )
    st.sidebar.success("FAISS Vector DB loaded.")
except Exception as e:
    st.error(f"Error loading FAISS index from '{faiss_index_path}': {e}")
    st.text(traceback.format_exc())
    st.stop()

# HyDE retriever
try:
    hyde_retriever = HydeRetriever(
        llm_for_hyde=llm_instance,
        vectorstore=vector_db_instance,
        embeddings_for_hyde=embeddings_instance,
        k_docs=4
    )
    st.sidebar.success("HyDE Retriever initialized.")
except Exception as e:
    st.error(f"Error initializing HydeRetriever: {e}")
    st.text(traceback.format_exc())
    st.stop()

# Conversation memory
@st.cache_resource
def init_memory():
    return ConversationBufferMemory(
        output_key='answer',
        memory_key='chat_history',
        return_messages=True
    )
memory = init_memory()
st.sidebar.success("Memory initialized.")

# Prompt template (Dutch, for LLM)
template = """Je bent een gespecialiseerde vriendelijke AI-assistent voor medewerkers van de ANWB Alarmcentrale. Je hoofdtaak is het accuraat beantwoorden van vragen over de voorwaarden van ANWB Wegenwacht Service, met een focus op hulpverlening in het buitenland.

Richtlijnen voor je antwoorden:
1.  **Basis:** Baseer antwoorden *altijd en uitsluitend* op de aangeleverde context (opgehaald via HyDE). Interpreteer deze context zorgvuldig.
2.  **Terminologie:** De brontekst gebruikt 'het lid' en 'de klant' afwisselend. Gebruik alleen de exacte namen van diensten zoals gespecificeerd. Spreek in de derde persoon (bijv. "Het lid heeft recht op...").
3.  **Nauwkeurigheid & Stijl:** Formuleer heldere, feitelijke, beknopte, professionele en helpende antwoorden. Vermijd speculatie.
4.  **Volledigheid:** Geef relevante details weer zoals wachttijden, maximale vergoedingen, dekkingsgebieden, en uitsluitingen.
5.  **Informatie Ontbreekt:** Als de benodigde informatie niet in de verstrekte context staat, geef dit dan duidelijk aan. Speculeer niet over niet-benoemde diensten.
6.  **Focus:** Help de medewerker snel de juiste informatie te vinden.
7.  **Directheid:** Begin je antwoord direct met de relevante informatie. Vermijd inleidende zinnen over je eigen proces (bijvoorbeeld, zeg niet "Ik kan je helpen met...", "Volgens de informatie die ik heb opgehaald via HyDE,...", of "Op basis van de context..."). Ga direct naar de kern van het antwoord op de vraag.

Context (opgehaald met HyDE) to answer question: {context}

Question to be answered (mogelijk hergeformuleerd met chatgeschiedenis): {question}
Response:"""
prompt_template_obj = PromptTemplate(template=template, input_variables=["context", "question"])

# Build the conversational retrieval chain
try:
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm_instance,
        retriever=hyde_retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt_template_obj}
    )
    st.sidebar.success("Conversational Chain initialized.")
except Exception as e:
    st.error(f"Error initializing ConversationalRetrievalChain: {e}")
    st.text(traceback.format_exc())
    st.stop()

# Streamlit chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Hallo collega! Stel je vraag over de ANWB Wegenwacht Service voorwaarden."})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query_prompt := st.chat_input("Hi collega, stel je vraag over de voorwaarden..."):
    st.chat_message("user").markdown(user_query_prompt)
    st.session_state.messages.append({"role": "user", "content": user_query_prompt})
    final_question_for_chain = user_query_prompt
    selected_pkg = st.session_state.get('selected_package', default_package)
    selected_supp = st.session_state.get('selected_supplement', default_supplement)
    if selected_pkg != default_package:
        package_context_info = f"Pakket: {selected_pkg}"
        if selected_supp != default_supplement:
            package_context_info += f", Supplement: {selected_supp}"
        final_question_for_chain = f"Voor de context: {package_context_info}. De vraag van de medewerker is: {user_query_prompt}"
    with st.spinner("Ik zoek het voor je op...🔍 (met HyDE)"):
        try:
            result = chain.invoke({"question": final_question_for_chain})
            response = result["answer"]
            with st.chat_message("assistant"):
                st.markdown(response)
                if result.get("source_documents"):
                    with st.expander("Bekijk bronnen (opgehaald met HyDE)"):
                        for i, doc in enumerate(result["source_documents"]):
                            hyde_ans_for_debug = doc.metadata.get('retrieved_with_hyde_answer', '')
                            if hyde_ans_for_debug:
                                 st.markdown(f"<small><i>HyDE Antwoord voor retrieval: {hyde_ans_for_debug[:150]}...</i></small>", unsafe_allow_html=True)
                            st.markdown(f"**Bron {i+1}**")
                            st.markdown(f"H2: {doc.metadata.get('H2_Titel', 'N/A')}, H3: {doc.metadata.get('H3_Titel', 'N/A')}")
                            st.caption(doc.page_content[:300] + "...")
                            st.markdown("---")
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Fout tijdens het verwerken van de vraag: {e}")
            st.text(traceback.format_exc())
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, er ging iets mis bij het verwerken van je vraag. Details: {str(e)[:100]}..."})

            
