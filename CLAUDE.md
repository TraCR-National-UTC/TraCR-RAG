# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
TraCR-RAG is a Retrieval-Augmented Generation (RAG) powered Large Language Model designed for legislative analysis of connected and automated transportation systems. It uses Django as the web framework and LlamaIndex for RAG functionality to analyze cybersecurity laws from different US states.

## Architecture
- **Django Web Framework**: Standard Django project structure with main config in `config/`
- **RAG Implementation**: Core RAG functionality in `chatbot/tracr_rag.py` using LlamaIndex
- **Vector Storage**: Pre-computed vector indices stored in `Vector_Storage_Context/` organized by US state
- **Static Files**: Legislative PDFs organized by state in `static/legislations/Current Cybersecurity Law/`
- **Database**: SQLite database (`db.sqlite3`) for Django application data

## Key Files
- `chatbot/tracr_rag.py`: Main RAG implementation with OpenAI integration
- `config/settings.py`: Django configuration with environment variable support
- `chatbot/views.py`: Django views handling web requests and chatbot interactions
- `templates/chatbot/`: HTML templates for the web interface

## Development Commands
- **Start development server**: `python manage.py runserver`
- **Database migrations**: `python manage.py makemigrations` then `python manage.py migrate`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic`

## Environment Setup
- Python 3.10+ required
- Virtual environment recommended: `python -m venv .venv`
- Install dependencies: `pip install -r requirements.txt`
- Required environment variables in `.env`:
  - `OPENAI_API_KEY`: OpenAI API key for RAG functionality
  - `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
  - `DEBUG`: Set to "True" for development

## Data Structure
- **Vector Storage**: Each US state has its own directory in `Vector_Storage_Context/` with:
  - `default__vector_store.json`: Main vector store
  - `docstore.json`: Document store
  - `graph_store.json`: Graph relationships
  - `index_store.json`: Index metadata
  - `image__vector_store.json`: Image embeddings

## Legal Document Processing
- PDFs are organized by state and law type in `static/legislations/`
- The system processes documents using PyPDF2 for text extraction
- Vector embeddings are pre-computed and stored for efficient retrieval
- URL generation handles special characters and file paths via `safe_url()` function

## Key Dependencies
- Django 5.2.8: Web framework
- LlamaIndex: RAG implementation
- OpenAI: LLM integration  
- python-dotenv: Environment variable management
- PyPDF2: PDF processing
- whitenoise: Static file serving