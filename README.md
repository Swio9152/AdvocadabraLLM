# AdvocaDabra Legal AI System

A comprehensive legal AI assistant that combines Similar Case Retrieval (SCR) and Precedent Case Retrieval (PCR) with a modern React frontend and real authentication system.

## Features

- **Similar Case Retrieval (SCR)**: Find cases similar to your query using AI-powered semantic search
- **Precedent Case Retrieval (PCR)**: Discover relevant legal precedents with authority scoring
- **File Upload Support**: Upload and analyze PDF, TXT, JSON, CSV, Excel, and Word documents
- **Real Authentication**: JWT-based authentication with SQLite database
- **Modern UI**: Clean, responsive React interface with Tailwind CSS
- **Fast Search**: FAISS-powered vector search through 103,980+ legal cases
- **Analysis Dashboard**: Integrated interface for text and file analysis

## Architecture

### Backend (`/backend`)
- **Flask API Server**: JWT authentication, file handling, AI analysis
- **SCR/PCR Modules**: Similar Case Retrieval and Precedent Case Retrieval
- **Vector Embeddings**: FAISS-indexed legal case embeddings
- **Data Storage**: SQLite database and file upload system

### Frontend (`/frontend/legal-ai-client`) - **Recently Consolidated**
- **React + Vite**: Modern web application with consolidated architecture
- **Streamlined Structure**: Reduced from 9+ files to 5 core files for better maintainability
- **Unified Authentication**: All auth logic consolidated in single `Auth.jsx` file
- **Integrated Dashboard**: SCR/PCR analysis with Legal Judgment Prediction placeholder
- **Modern UI**: Clean Apple-inspired design with consolidated Tailwind CSS styles

### Data & External Dependencies
- **103,980 Legal Cases** from the DI dataset (stored in `~/Documents/data_raw/`)
- **58,200+ Embeddings** generated (ongoing process)
- **FAISS Index** for fast similarity search
- **Node Modules** managed automatically by npm (no duplicate installations)

## Project Structure

```
AdvocadabraLLM/
├── README.md                 # Main project documentation
├── start_system.sh          # One-command system startup
├── test_system.py           # Comprehensive system tests
├── cleanup.py               # Project maintenance script
├── backend/                 # Flask API Server
│   ├── backend_server.py    # Main API server
│   ├── build_scr.py        # Similar Case Retrieval
│   ├── build_pcr.py        # Precedent Case Retrieval
│   ├── Embeddings.py       # Vector embedding generation
│   ├── requirements.txt    # Python dependencies
│   ├── users.db           # SQLite authentication database
│   ├── di_prime_embeddings/   # Vector embeddings storage
│   └── uploads/           # User uploaded files
└── frontend/              # React Web Application  
    └── legal-ai-client/   # Consolidated frontend (9+ files → 5 core files)
        ├── package.json   # Node.js dependencies
        ├── vite.config.js # Build configuration
        ├── src/          # Streamlined React source code
        │   ├── App.jsx   # Main app with embedded Navbar
        │   ├── Auth.jsx  # Consolidated: Login + Signup + useAuth + ProtectedRoute
        │   ├── api.js    # API utilities (moved from lib/)
        │   ├── index.css # All styles merged (Tailwind + custom)
        │   ├── main.jsx  # Entry point
        │   └── routes/   # Page components (Dashboard, Landing)
        └── public/       # Static assets
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- 8GB+ RAM (for embeddings)

### **🚀 One-Command Setup:**
```bash
# Set up development environment
./dev.sh setup

# Start development servers
./dev.sh dev
```

### **⚡ Manual Setup:**
```bash
# Backend
cd backend && pip install -r requirements.txt && python backend_server.py &

# Frontend  
cd frontend/legal-ai-client && npm install && npm run dev
```

### **🌐 Access Points:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **System Startup**: `./start_system.sh`

## Usage

### Text Analysis
1. Navigate to SCR or PCR tab
2. Enter your legal query in the text area
3. Click "Run Analysis" to get similar cases or precedents

### File Analysis
1. Upload legal documents via drag-drop or file browser
2. Select an uploaded file from your file list
3. Click "Analyze File" to process the document content

### Supported File Types
- **PDF**: Legal documents, case files
- **TXT**: Plain text legal content
- **JSON**: Structured legal data
- **CSV**: Case databases, legal datasets
- **Excel**: Legal spreadsheets, case lists
- **Word**: Legal documents, briefs

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify JWT token

### File Operations
- `POST /api/upload` - Upload legal documents
- `GET /api/files` - List user files
- `POST /api/analyze-file` - Analyze uploaded file

### AI Analysis
- `POST /api/scr` - Similar Case Retrieval
- `POST /api/pcr` - Precedent Case Retrieval
- `GET /api/health` - System health check

## Testing

Run the comprehensive test suite:
```bash
python3 test_system.py
```

Tests include:
- API Health Check
- Authentication (Signup/Login)
- SCR Text Analysis
- PCR Text Analysis
- File Upload
- File Analysis

## System Status

- **Backend**: Running (Port 8000) - Original structure maintained
- **Frontend**: **Consolidated & Optimized** (Port 5173) - 9+ files reduced to 5 core files
- **Database**: SQLite initialized with user authentication
- **AI Models**: SCR & PCR operational with embeddings
- **Architecture**: Streamlined for better maintainability and performance
- **File Storage**: Upload system active with multi-format support

## Configuration

### Environment Variables
```bash
FLASK_SECRET_KEY=your-secret-key-change-in-production
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=50MB
```

### Data Paths
- **Legal Cases**: `~/Documents/data_raw/di_dataset.jsonl` (external data source)
- **Embeddings**: `backend/di_prime_embeddings/` (vector storage)
- **Uploads**: `backend/uploads/` (user files)
- **Database**: `backend/users.db` (authentication)

## Production Ready Features

### Architecture & Performance
- **Consolidated Frontend**: Streamlined from 9+ files to 5 core files for better maintainability
- **Unified Authentication**: Single consolidated auth module with JWT tokens and secure password hashing
- **Fast AI Search**: FAISS indexing for rapid similar case and precedent retrieval
- **Optimized Imports**: Clean dependency structure with no redundant code paths

### Functionality & Security
- **Multi-Format File Processing**: PDF, TXT, JSON, CSV, Excel, Word support with error handling
- **Real-Time Analysis**: SCR/PCR processing with Legal Judgment Prediction UI ready
- **Responsive Design**: Apple-inspired clean UI that works on all devices
- **Security**: CORS enabled, input validation, and JWT-based session management
- **Error Management**: Graceful fallbacks and comprehensive user feedback

## Recent Improvements (December 2024)

- ✅ **Frontend Consolidation**: Reduced complexity from 9+ scattered files to 5 organized core files
- ✅ **Authentication Streamlining**: Combined Login, Signup, useAuth, and ProtectedRoute into single `Auth.jsx`
- ✅ **Style Unification**: Merged all CSS into consolidated `index.css` with Tailwind integration
- ✅ **Import Optimization**: Updated all component imports to use new consolidated structure
- ✅ **UI Enhancements**: Clean Apple-inspired design with Legal Judgment Prediction placeholder
- ✅ **Maintainability**: Improved code organization and reduced redundancy

## Future Enhancements

- **LJP Integration**: Legal Judgment Prediction (UI placeholder ready)
- **Advanced Analytics**: Case outcome prediction with AI models
- **Document Generation**: AI-powered legal document creation
- **Backend Optimization**: Potential consolidation of duplicate code patterns
- **Export Options**: PDF reports, case summaries, analysis results

## License

This project is for educational and research purposes in legal AI technology.

---

## Quick Reference

| Task | Command | Description |
|------|---------|-------------|
| **🚀 Setup** | `./dev.sh setup` | Complete environment setup |
| **💻 Development** | `./dev.sh dev` | Start both servers |
| **🏗️ Build** | `./dev.sh build` | Production build |
| **🧹 Clean** | `./dev.sh clean` | Remove temp files |
| **🎯 Full System** | `./start_system.sh` | Original startup script |

## Development Workflow

1. **Setup**: `./dev.sh setup` (one time)
2. **Develop**: `./dev.sh dev` (daily)
3. **Build**: `./dev.sh build` (for production)
4. **Clean**: `./dev.sh clean` (maintenance)

---

**🎉 AdvocaDabra Legal AI System - Streamlined & Production Ready!**

*Recent frontend consolidation has reduced complexity while maintaining all functionality. Backend architecture preserved as requested for optimal SCR/PCR performance.*