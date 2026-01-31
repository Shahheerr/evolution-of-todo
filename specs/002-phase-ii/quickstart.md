# Quickstart Guide: Phase-II Full-Stack Todo Application

## Prerequisites

- Node.js 20+ with npm
- Python 3.13+
- UV package manager
- Git
- Neon PostgreSQL account
- Access to terminal/command line

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies

#### Frontend Dependencies:
```bash
cd frontend
npm install
```

#### Backend Dependencies:
```bash
cd backend
uv sync  # or uv install
```

### 3. Configure Environment Variables

#### Create frontend/.env file:
```env
DATABASE_URL=<your-neon-database-url>
BETTER_AUTH_SECRET=<your-secret-key-here>
NEXT_PUBLIC_APP_NAME="Todo App"
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
```

#### Create backend/.env file:
```env
DATABASE_URL=<your-neon-database-url>
BETTER_AUTH_SECRET=<your-secret-key-here>
APP_NAME=Todo API
DEBUG=true
FRONTEND_URL=http://localhost:3000
```

**Important**: The `BETTER_AUTH_SECRET` must be identical in both files as it's used for the JWT bridge between frontend and backend.

## Database Setup

### 1. Initialize Prisma Schema
```bash
cd frontend
npx prisma init
```

### 2. Set Up Database Connection
Update the DATABASE_URL in both frontend/.env and backend/.env with your Neon PostgreSQL connection string.

### 3. Push Schema to Database
```bash
cd frontend
npx prisma db push
```

### 4. Generate Prisma Client
```bash
cd frontend
npx prisma generate
```

## Running the Application

### 1. Start the Backend Server
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend Server
```bash
cd frontend
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Documentation: http://localhost:8000/docs

## Key Features Access

### Authentication Flow
1. Visit http://localhost:3000/auth/register to create an account
2. Log in at http://localhost:3000/auth/login
3. The frontend exchanges your session for a JWT token automatically
4. JWT token is sent to backend with each authenticated request

### Task Management
1. Navigate to the dashboard at http://localhost:3000/dashboard
2. Create new tasks using the "Add Task" button
3. View, update, or delete tasks using the UI controls
4. Filter tasks by status using the filter buttons

### API Endpoints
- `GET /api/tasks` - Retrieve user's tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `GET /api/auth/token` - Get JWT token for backend communication

## Development Commands

### Frontend Commands
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint
```

### Backend Commands
```bash
# Run development server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .
```

## Troubleshooting

### Common Issues

**Issue**: JWT authentication fails between frontend and backend
- **Solution**: Verify that `BETTER_AUTH_SECRET` is identical in both frontend/.env and backend/.env

**Issue**: Database connection fails
- **Solution**: Check that the DATABASE_URL is correctly set and the database is accessible

**Issue**: Frontend can't connect to backend API
- **Solution**: Ensure backend is running on port 8000 and CORS is configured correctly

**Issue**: Prisma schema errors
- **Solution**: Run `npx prisma db pull` to sync with current database, then `npx prisma generate`

### Development Tips

- The backend runs on port 8000, frontend on port 3000
- All authenticated API requests must include `Authorization: Bearer <token>` header
- User data isolation is enforced by the backend using JWT sub claim
- The frontend never accesses the database directly; all data goes through API routes

## Architecture Overview

The application follows a decoupled monorepo architecture:
- **Frontend**: Next.js handles user interface and session management
- **Backend**: FastAPI handles business logic and data access
- **Database**: Neon PostgreSQL stores all data
- **Authentication Bridge**: JWT tokens enable secure communication between frontend and backend
- **Shared Secret**: BETTER_AUTH_SECRET enables the JWT verification between systems