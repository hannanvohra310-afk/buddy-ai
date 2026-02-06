# Buddy AI - Career Counselling Chatbot

A conversational AI career counselling chatbot for students in grades 8-10, built with Streamlit and powered by RAG (Retrieval Augmented Generation).

## Features

- **Conversational Career Exploration**: Natural language chat about careers, education paths, and skills
- **7 Conversation States**: Intelligent state detection for contextual responses
- **Memory System**: Remembers student preferences and past conversations
- **Authentication**: School email-based login with session management
- **Admin Dashboard**: Anonymized analytics for administrators

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4o-mini
- **Vector Store**: Pinecone
- **Embeddings**: OpenAI text-embedding-3-small
- **Database**: SQLite (via SQLAlchemy)
- **Authentication**: JWT + bcrypt

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/buddy-ai.git
cd buddy-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
JWT_SECRET_KEY=your_jwt_secret
```

### 5. Run the application
```bash
streamlit run app.py
```

## Project Structure

```
buddy-ai/
├── app.py                 # Main application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── auth/                  # Authentication module
├── chat/                  # Chat management
├── conversation/          # State detection & response generation
├── memory/                # Student profiling & memory
├── prompts/               # System prompts & guardrails
├── ui/                    # Styles & components
├── admin/                 # Admin analytics
├── pages/                 # Streamlit pages (login, etc.)
├── tests/                 # Test suite
└── data/                  # PDF knowledge base
```

## Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in Streamlit Cloud settings

### Environment Variables for Deployment
Set these in your deployment platform:
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `JWT_SECRET_KEY`

## License

Private - All rights reserved.
