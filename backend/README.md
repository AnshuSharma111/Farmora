# Farmora Backend

This is the backend for the Farmora application, consisting of two server components:

1. **AI Server** (Python FastAPI): Handles ML processing, intent classification, data retrieval, and AI response generation
2. **Client Server** (Node.js Express): Handles authentication, database operations, and client requests

## Directory Structure

```
backend/
├── ai_server/           # Python FastAPI server for AI processing
│   ├── main.py          # Main FastAPI application
│   ├── local_model.py   # Local model for intent classification
│   └── requirements.txt # Python dependencies
│
└── client_server/       # Node.js Express server for client logic
    ├── package.json     # Node.js dependencies
    └── src/             # Source code
        ├── index.js     # Express application entry point
        ├── middlewares/ # Middleware functions
        ├── models/      # Mongoose models
        └── routes/      # API routes
```

## AI Server (Python FastAPI)

The AI server is responsible for:

- Classifying the intent of farmer questions (weather, crops, soil, etc.)
- Retrieving relevant data from various sources
- Processing and summarizing data for token efficiency
- Generating farmer-friendly responses using LLMs

### Setup

```bash
cd backend/ai_server
pip install -r requirements.txt
cp .env.example .env  # Edit with your actual API keys
python main.py
```

Server will run on http://localhost:8000 by default.

## Client Server (Node.js Express)

The client server handles:

- User authentication and management
- Storing and retrieving query history
- Forwarding queries to the AI server
- Saving responses and feedback

### Setup

```bash
cd backend/client_server
npm install
cp .env.example .env  # Edit with your configuration
npm run dev
```

Server will run on http://localhost:5000 by default.

## Authentication with Appwrite

Farmora uses [Appwrite](https://appwrite.io/) for authentication. The authentication flow is as follows:

1. Frontend authenticates users directly with Appwrite
2. Frontend receives JWT token from Appwrite
3. Frontend includes token in API requests to both backend servers
4. Backend servers verify token with Appwrite and process requests

For detailed information, see [Appwrite Authentication Documentation](./client_server/docs/appwrite-auth.md).

## API Communication Flow

1. Client authenticates with Appwrite and gets a JWT token
2. Client makes a request to the Client Server API with the token
3. Client Server verifies the token with Appwrite
4. If needed, Client Server forwards the query to AI Server with the token
5. AI Server verifies the token and processes the query
6. AI Server returns results to Client Server
7. Client Server stores results and sends response to the client

## Environment Variables

### AI Server (.env)
- `PORT`: Server port (default: 8000)
- `ENVIRONMENT`: Application environment (development, production)
- `APPWRITE_ENDPOINT`: Appwrite API endpoint
- `APPWRITE_PROJECT_ID`: Appwrite project ID
- `APPWRITE_API_KEY`: Appwrite API key
- `OPENAI_API_KEY`: OpenAI API key for LLM responses
- `WEATHER_API_KEY`: API key for weather data

### Client Server (.env)
- `PORT`: Server port (default: 5001)
- `NODE_ENV`: Application environment (development, production)
- `MONGODB_URI`: MongoDB connection string
- `APPWRITE_ENDPOINT`: Appwrite API endpoint
- `APPWRITE_PROJECT_ID`: Appwrite project ID
- `APPWRITE_API_KEY`: Appwrite API key
- `AI_SERVER_URL`: URL of the AI server
