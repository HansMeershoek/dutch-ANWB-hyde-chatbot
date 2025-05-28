# Dutch ANWB HyDE Chatbot

A sophisticated RAG (Retrieval-Augmented Generation) chatbot system with Memory and HyDE (Hypothetical Document Embeddings) capabilities, specifically designed for ANWB T&C International roadside assistance information.

## Features

- **HyDE (Hypothetical Document Embeddings)**: Advanced retrieval technique that generates hypothetical answers to improve document retrieval accuracy
- **RAG with Memory**: Retrieval-Augmented Generation with conversational memory for context-aware responses
- **ANWB T&C Specialized**: Focused on ANWB Terms & Conditions for International roadside assistance
- **Interactive Streamlit Interface**: User-friendly web interface for easy interaction
- **Context-aware Responses**: Package and supplement selection for targeted assistance
- **Multilingual Support**: Optimized for Dutch language queries

## Architecture

The system combines several advanced NLP techniques:

1. **HyDE Retriever**: Generates hypothetical answers to improve semantic search
2. **FAISS Vector Database**: Efficient similarity search and clustering
3. **Groq LLM Integration**: Fast inference with Llama 3.1 8B model
4. **Multilingual Embeddings**: Using `intfloat/multilingual-e5-large` for Dutch language support
5. **Conversational Memory**: Maintains context across chat sessions

## Installation

### Prerequisites

- Python 3.8 or higher
- GROQ API key (set as environment variable `GROQ_API_FOR_STREAMLIT`)

### Install from GitHub

```bash
pip install git+https://github.com/HansMeershoek/dutch-ANWB-hyde-chatbot.git
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/HansMeershoek/dutch-ANWB-hyde-chatbot.git
cd dutch-ANWB-hyde-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GROQ_API_FOR_STREAMLIT="your_groq_api_key_here"
```

## Usage

### Running the Streamlit App

```bash
streamlit run anwb_chatbot_app.py
```

The application will start on `http://localhost:8501`

### Features in the Interface

1. **Package Selection**: Choose from various ANWB Wegenwacht Europa packages
2. **Supplement Options**: Select additional services like trailer or motorhome assistance
3. **Chat Interface**: Ask questions about ANWB services, terms, and conditions
4. **Context Awareness**: Responses tailored to selected package and supplements

### Example Queries

- "Wat zijn de voorwaarden voor pechverhelping in het buitenland?"
- "Welke kosten zijn gedekt bij een autopech in Duitsland?"
- "Hoe werkt de aanhangwagen service?"
- "Wat is het verschil tussen Standaard en Compleet pakket?"

## Project Structure

```
dutch-ANWB-hyde-chatbot/
├── anwb_chatbot_app.py      # Main Streamlit application
├── faiss_index/             # FAISS vector database
├── ANWB.md                  # Source documentation
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore              # Git ignore rules
```

## Technical Details

### HyDE Implementation

The HyDE (Hypothetical Document Embeddings) retriever works by:

1. Taking a user query
2. Generating a hypothetical answer using the LLM
3. Embedding the hypothetical answer
4. Using this embedding to retrieve relevant documents
5. This often yields better results than embedding the query directly

### Model Configuration

- **LLM**: Groq Llama 3.1 8B Instant
- **Embeddings**: `intfloat/multilingual-e5-large`
- **Vector Store**: FAISS with cosine similarity
- **Retrieval**: Top-4 documents with HyDE enhancement

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_FOR_STREAMLIT` | Groq API key for LLM access | Yes |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ANWB for the comprehensive service documentation
- Groq for fast LLM inference
- Hugging Face for multilingual embeddings
- LangChain for the RAG framework
- FAISS for efficient vector search

## Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Note**: This chatbot is designed for informational purposes. For official ANWB services and binding agreements, please consult the official ANWB website and documentation. 