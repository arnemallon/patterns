# Bitcoin Address Classifier

A web application that classifies Bitcoin addresses for illegal activity detection using machine learning.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL

### Setup
1. **Clone and setup the project:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Set up the database:**
   ```bash
   createdb bitcoin_classifier
   psql -d bitcoin_classifier -f database/schema.sql
   ```

3. **Configure environment:**
   ```bash
   cd backend
   cp env.example .env
   # Edit .env with your database credentials
   ```

4. **Start the application:**
   ```bash
   # Terminal 1: Start backend
   cd backend
   source venv/bin/activate
   python run.py
   
   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

5. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🔬 Research-Based Feature Calculation

The system now supports **exact research-based feature calculations** using the original research code from `moduleG.py`. This ensures feature values match your research exactly.

### Two Calculation Modes:

1. **Research Mode (Recommended)**: Uses graph-tool and exact research functions
   - Requires graph-tool installation
   - Uses the original Bitcoin graph and reverse map
   - Calculates features exactly as in your research

2. **API Mode (Fallback)**: Uses BlockCypher API
   - No additional dependencies
   - Approximates features using transaction data
   - Works when research files are not available

### Installing Research Mode:

```bash
# Install graph-tool for exact calculations
cd backend
./install_graph_tool.sh

# Or manually install graph-tool:
conda install -c conda-forge graph-tool
```

### Research Files Required:

For exact calculations, place these files in `backend/scripts/`:
- `BitcoinGraph.gt` - The Bitcoin transaction graph
- `revmap.pkl` - Address to vertex mapping

The system will automatically detect these files and use research mode when available.

## 🏗️ Project Structure

```
BlockChainAnalysis/
├── backend/                    # Flask API server
│   ├── app/
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   │   ├── feature_service.py    # Feature extraction (research + API)
│   │   │   └── ml_service.py         # ML predictions
│   │   └── models/            # Database models
│   ├── scripts/               # Research code
│   │   ├── moduleG.py         # Original research functions
│   │   ├── BitcoinGraph.gt    # Bitcoin transaction graph
│   │   └── revmap.pkl         # Address mapping
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Application entry point
├── frontend/                  # Svelte web application
│   ├── src/
│   │   ├── components/        # Svelte components
│   │   └── services/          # API client
│   ├── package.json
│   └── vite.config.js
├── database/                  # Database schema
│   └── schema.sql
├── ml-models/                 # Trained ML models
├── FeatureExtraction/         # Original feature extraction code
├── NonStructuralTraining/     # Original ML training code
└── setup.sh                   # Setup script
```

## 🔧 Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Svelte + Vite
- **Database**: PostgreSQL
- **ML**: TensorFlow (with fallback classification)
- **Research**: graph-tool + moduleG.py (exact calculations)
- **API**: BlockCypher for Bitcoin data (fallback)

## 📊 Features

- **Address Classification**: Analyze Bitcoin addresses for suspicious activity
- **Research-Based Features**: Extract 8 key features using exact research calculations
- **Dual Mode**: Research mode (exact) + API mode (approximate)
- **Caching**: Store results to avoid re-processing
- **History**: View classification history
- **Real-time Analysis**: Live blockchain data via BlockCypher API

## 🔌 API Endpoints

- `POST /api/classify` - Classify a Bitcoin address
- `GET /api/history` - Get classification history
- `GET /api/health` - Health check

## 🎯 ML Model Integration

The application currently uses a fallback classification system. To integrate your trained model:

1. **Export your model:**
   ```python
   # In your Jupyter notebook
   model.save('ml-models/bitcoin_classifier.keras')
   
   # Save the scaler's data as a JSON file
   import json
   scaler_data = {
       'mean': scaler.mean_.tolist(),
       'scale': scaler.scale_.tolist()
   }
   with open('ml-models/scaler.json', 'w') as f:
       json.dump(scaler_data, f)
   ```

2. **Update the ML service:**
   ```python
   # In backend/app/services/ml_service.py
   ml_service = MLService(
       model_path='ml-models/bitcoin_classifier.keras',
       scaler_path='ml-models/scaler.json'
   )
   ```

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend
source venv/bin/activate
python run.py

# Frontend
cd frontend
npm run dev
```

### Production
```bash
# Build frontend
cd frontend
npm run build

# Run backend with gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📝 Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/bitcoin_classifier
BLOCKCYPHER_API_TOKEN=your-blockcypher-token-here
MODEL_PATH=../ml-models/bitcoin_classifier.keras
SCALER_PATH=../ml-models/scaler.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure compliance with applicable laws and regulations when using this tool.