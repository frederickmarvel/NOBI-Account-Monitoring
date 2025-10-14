# 📂 Folder Structure Guide

## Overview

The project has been reorganized into a clean, modular structure for better maintainability.

## Directory Tree

```
Blockchain Monitoring/
│
├── 📱 frontend/                   # Web Interface (Client-side)
│   ├── index.html                # Main application UI
│   ├── app.js                    # Chart rendering & UI logic
│   ├── api-service-new.js        # API client (calls backend)
│   └── style.css                 # CSS styling
│
├── 🐍 backend/                    # Python Flask API (Server-side)
│   ├── backend.py                # Main Flask server (port 8085)
│   ├── blockchain_service.py     # Blockchain data fetching
│   │                             # - Token whitelist (50+ tokens)
│   │                             # - Etherscan V2 API integration
│   │                             # - Bitcoin blockchain.info API
│   │
│   ├── currency_service.py       # Currency conversion
│   │                             # - CoinGecko API for crypto prices
│   │                             # - USD to AED conversion (3.67 rate)
│   │
│   ├── pdf_generator.py          # PDF report generation
│   │                             # - ReportLab library
│   │                             # - Professional formatting
│   │                             # - Complete transaction history
│   │
│   └── requirements.txt          # Python dependencies
│
├── 📚 docs/                       # Documentation
│   ├── BACKEND_README.md         # Backend API endpoints & usage
│   ├── DEPLOYMENT.md             # Production deployment guide
│   ├── PDF_EXPORT_README.md      # PDF generation system docs
│   ├── TOKEN_FILTERING_README.md # Token whitelist configuration
│   └── V2_UPGRADE.md             # Etherscan V2 migration guide
│
├── 🗄️ archive/                    # Deprecated/Old Files
│   ├── test.html                 # Old testing interface
│   ├── QUICKSTART_OLD.md         # Outdated quick start
│   ├── FIXED_COMPLETE.md         # Old changelog
│   └── README_OLD.md             # Previous README version
│
├── 🔧 Configuration Files
│   ├── .env                      # API keys (git-ignored, create from .env.example)
│   ├── .env.example              # Environment variables template
│   └── .gitignore                # Git ignore rules
│
├── 📄 Root Files
│   ├── README.md                 # Main documentation (YOU ARE HERE)
│   └── start.sh                  # Quick start script
│
└── 🎯 Purpose: Generate professional PDF account statements for crypto wallets
```

## File Purposes

### Frontend Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `index.html` | Main UI | Form inputs, blockchain selector, chart containers |
| `app.js` | Frontend logic | Chart.js integration, form handling, PDF export trigger |
| `api-service-new.js` | API client | Calls backend REST API, handles responses |
| `style.css` | Styling | Modern UI, responsive design |

### Backend Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `backend.py` | Flask server | REST API endpoints, CORS, routing |
| `blockchain_service.py` | Data fetching | Etherscan V2 API, token whitelist (50+ tokens), spam filtering |
| `currency_service.py` | Price conversion | CoinGecko API, USD/AED rates, caching |
| `pdf_generator.py` | PDF creation | ReportLab, professional formatting, all transactions |
| `requirements.txt` | Dependencies | Flask, requests, reportlab, python-dotenv |

### Documentation Files

| File | Purpose |
|------|---------|
| `BACKEND_README.md` | API endpoints, request/response formats |
| `DEPLOYMENT.md` | Production deployment, server setup |
| `PDF_EXPORT_README.md` | PDF generation system, customization |
| `TOKEN_FILTERING_README.md` | Whitelist configuration, adding tokens |
| `V2_UPGRADE.md` | Migration guide from old API structure |

## Key Changes from Old Structure

### Before (Messy)
```
Root/
├── index.html
├── app.js
├── api-service-new.js
├── style.css
├── backend.py
├── blockchain_service.py
├── currency_service.py
├── pdf_generator.py
├── requirements.txt
├── test.html (outdated)
├── BACKEND_README.md
├── DEPLOYMENT.md
├── PDF_EXPORT_README.md
├── TOKEN_FILTERING_README.md
├── V2_UPGRADE.md
├── QUICKSTART_OLD.md (outdated)
├── FIXED_COMPLETE.md (outdated)
└── README.md
```

### After (Clean)
```
Root/
├── frontend/          ← All frontend files
├── backend/           ← All backend files
├── docs/              ← All documentation
├── archive/           ← Old/unused files
├── .env
├── .env.example
├── .gitignore
├── start.sh
└── README.md
```

## Benefits of New Structure

✅ **Clear Separation** - Frontend and backend are separate  
✅ **Easy Navigation** - Find files by category  
✅ **Better Maintenance** - Logical grouping  
✅ **Cleaner Root** - Only essential files in root  
✅ **Scalability** - Easy to add new features  
✅ **Documentation** - All docs in one place  

## How to Navigate

### Working on Frontend
```bash
cd frontend/
# Edit: index.html, app.js, api-service-new.js, style.css
```

### Working on Backend
```bash
cd backend/
# Edit: backend.py, blockchain_service.py, currency_service.py, pdf_generator.py
```

### Reading Documentation
```bash
cd docs/
# Read: *.md files
```

### Running the System
```bash
# From root directory
./start.sh

# Or manually:
cd backend && python3 backend.py &
open frontend/index.html
```

## File Relationships

```
frontend/index.html
    └─> Loads: app.js, api-service-new.js, style.css
            └─> API calls ─────┐
                               ├─> backend/backend.py (Flask Server)
                               │       └─> blockchain_service.py
                               │       └─> currency_service.py
                               │       └─> pdf_generator.py
                               │
                               └─> Returns: JSON data or PDF file
```

## What's in Archive?

Files that are **no longer needed** but kept for reference:

- `test.html` - Old testing interface (replaced by main app)
- `QUICKSTART_OLD.md` - Outdated documentation
- `FIXED_COMPLETE.md` - Old changelog
- `README_OLD.md` - Previous README before reorganization

You can safely delete the `archive/` folder if you don't need these files.

## Adding New Files

### Adding a new backend module
```bash
# Create in backend/
cd backend/
touch new_service.py

# Import in backend.py
from new_service import NewService
```

### Adding new documentation
```bash
# Create in docs/
cd docs/
touch NEW_FEATURE.md
```

### Adding new frontend components
```bash
# Create in frontend/
cd frontend/
touch new-component.js

# Reference in index.html
<script src="new-component.js"></script>
```

## Summary

The new structure makes the project:
- **Professional** - Clear organization
- **Maintainable** - Easy to update
- **Scalable** - Ready for growth
- **Clean** - Minimal clutter

All old files are preserved in `archive/` for safety.
