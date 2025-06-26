# DORA Metrics Dashboard

A full-stack web application for tracking and visualizing DORA (DevOps Research and Assessment) metrics. The dashboard helps organizations monitor four key metrics:
- Deployment Frequency
- Lead Time for Changes
- Change Failure Rate
- Time to Restore Service

## Tech Stack

### Backend
- Python/Flask
- PostgreSQL
- SQLAlchemy
- Flask-Login for authentication
- pytest for testing

### Frontend
- React with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Radix UI components
- Recharts for data visualization

## Prerequisites
- Python 3.11 or higher
- Node.js and npm
- PostgreSQL database
- Git

## Local Development Setup

### Backend Setup
1. Create and activate virtual environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
Create a `.env` file in the `backend` directory with:
```env
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/dbname
```

4. Initialize database
```bash
python init_db.py
```

5. Run development server
```bash
python run.py
```
The backend server will start at http://localhost:5001

### Frontend Setup
1. Install dependencies
```bash
cd frontend/dora-ui
npm install
```

2. Configure environment variables
Create a `.env` file in the `frontend` directory with:
```env
VITE_API_URL=http://localhost:5001
```

3. Run development server
```bash
npm run dev
```
The frontend development server will start at http://localhost:5173

## Testing
```bash
# Backend tests
cd backend
pytest tests/
```

## Production Deployment

The application is deployed on Render.com:
- Frontend: https://dora-ui.onrender.com
- Backend: https://dora-backend-prod.onrender.com

Deployment is automated via GitHub Actions:
- Push to `pre-prod` branch triggers tests
- Push to `main` branch triggers tests and deployment to production

### Production Environment Variables

For production deployment, ensure the following environment variables are configured in your Render.com dashboard:

Backend:
```env
SECRET_KEY=your_production_secret_key
SQLALCHEMY_DATABASE_URI=your_production_database_url
```

Frontend:
```env
VITE_API_URL=https://dora-backend-prod.onrender.com
```

## Development Workflow

1. Create a new branch from `main`
2. Make your changes
3. Push to `pre-prod` branch to run tests
4. Once tests pass, create a pull request to merge into `main`
5. After merge, GitHub Actions will automatically deploy to production
