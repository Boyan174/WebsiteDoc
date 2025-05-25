# Accessibility Analyzer

A full-stack web application that analyzes websites for accessibility issues using AI-powered insights.

## Project Structure

This repository contains both the frontend and backend components of the Accessibility Analyzer application:

```
accessibility-analyzer/
├── accessibility-analyzer-frontend/    # React TypeScript frontend
└── accessibility-analyzer-backend/     # Python FastAPI backend
```

## Features

- URL input for website analysis
- Web scraping using Firecrawl
- AI-powered accessibility analysis using LangChain
- Detailed accessibility reports with recommendations
- Modern, responsive UI

## Tech Stack

### Frontend
- React with TypeScript
- CSS for styling
- Axios for API communication

### Backend
- Python FastAPI
- Firecrawl for web scraping
- LangChain with OpenAI for AI analysis
- Pydantic for data validation

## Getting Started

### Prerequisites
- Node.js and npm (for frontend)
- Python 3.8+ (for backend)
- API keys for Firecrawl and OpenAI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Boyan174/accessibility-analyzer.git
cd accessibility-analyzer
```

2. Set up the backend:
```bash
cd accessibility-analyzer-backend
pip install -r requirements.txt
# Create .env file with your API keys
```

3. Set up the frontend:
```bash
cd accessibility-analyzer-frontend
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd accessibility-analyzer-backend
python main.py
```

2. Start the frontend development server:
```bash
cd accessibility-analyzer-frontend
npm start
```

3. Open http://localhost:3000 in your browser

## Environment Variables

### Backend (.env)
```
FIRECRAWL_API_KEY=your_firecrawl_api_key
OPENAI_API_KEY=your_openai_api_key
```

## License

This project is licensed under the MIT License.
