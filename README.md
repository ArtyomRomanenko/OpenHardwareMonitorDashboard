# OpenHardwareMonitorDashboard

A comprehensive dashboard for analyzing Open Hardware Monitor data with intelligent insights and interactive visualizations.

## Features

- 📊 **Interactive Time Series Plots**: Visualize CPU, GPU, and system metrics across different time periods
- 🧠 **Intelligent Insights**: AI-powered analysis of hardware health and performance
- 📈 **Real-time Monitoring**: Live data updates and historical trend analysis
- 🎯 **Customizable Dashboards**: Create personalized views for different metrics
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **Data Processing**: Pandas + NumPy
- **Charts**: Chart.js
- **Database**: SQLite

## Quick Start

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Configure Data Source**
   - Point the application to your Open Hardware Monitor CSV files
   - Update `config.py` with your data directory path

3. **Run the Application**
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload
   
   # Frontend
   cd frontend
   npm start
   ```

4. **Access Dashboard**
   - Open http://localhost:3000 in your browser

## Data Format

The application expects CSV files from Open Hardware Monitor with the following structure:
- Daily files named by date (YYYY-MM-DD.csv)
- Columns: timestamp, CPU temperature, GPU temperature, fan speeds, etc.

## Project Structure

```
OpenHardwareMonitorDashboard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # Data models
│   │   └── services/       # Business logic
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API calls
│   │   └── utils/          # Utilities
│   ├── package.json
│   └── tailwind.config.js
└── data/                   # CSV data files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License