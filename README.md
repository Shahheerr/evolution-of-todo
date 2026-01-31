# 🚀 TaskFlow - Production-Grade Todo Application

A full-stack todo application with Next.js frontend, FastAPI backend, and JWT-based authentication using Better Auth.

## 📋 Features

- ✅ **Full CRUD Operations** - Create, Read, Update, Delete tasks
- 🏷️ **Priority Levels** - High, Medium, Low with color coding
- 📊 **Status Management** - Pending, In Progress, Completed
- 🔖 **Tags** - Organize tasks with custom tags
- 🔍 **Smart Search** - Search tasks by title or description
- 🎯 **Advanced Filtering** - Filter by status, priority, and tags
- 📈 **Sorting** - Sort by date, priority, or title
- 🔐 **Secure Authentication** - JWT-based stateless authentication
- 🔒 **Data Isolation** - All queries filtered by user ID
- 🌙 **Premium Dark Theme** - Beautiful, modern UI design

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Next.js       │      │   FastAPI        │      │   PostgreSQL    │
│   (Frontend)    │◄────►│   (Backend)      │◄────►│   (Neon DB)     │
│   Port 3000     │ JWT  │   Port 8000      │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

### JWT Authentication Flow
1. User signs up/logs in via Better Auth (Frontend)
2. Better Auth creates a session and generates a JWT token
3. Frontend attaches JWT to all API requests (`Authorization: Bearer <token>`)
4. FastAPI verifies JWT using the same secret key
5. Backend extracts `user_id` from token and filters all queries

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Authentication**: Better Auth
- **Styling**: Custom CSS (Modern Dark Theme)
- **Database Client**: Prisma

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.13
- **Package Manager**: UV
- **Database**: asyncpg (async PostgreSQL driver)
- **Authentication**: PyJWT (JWT verification)

### Database
- **Provider**: Neon (Serverless PostgreSQL)
- **ORM**: Prisma (schema management)

## 📁 Project Structure

```
Phase-II/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        # Environment configuration
│   │   │   ├── database.py      # Database connection
│   │   │   └── security.py      # JWT verification ⭐
│   │   ├── models/
│   │   │   └── task.py          # Pydantic schemas
│   │   ├── routes/
│   │   │   └── tasks.py         # Task CRUD endpoints
│   │   └── main.py              # FastAPI application
│   ├── .env                     # Backend environment variables
│   └── pyproject.toml           # Python dependencies
│
├── neon-db-testing/             # Next.js Frontend
│   ├── app/
│   │   ├── api/auth/           # Better Auth API routes
│   │   ├── auth/               # Login/Register pages
│   │   ├── dashboard/          # Main application
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Landing page
│   ├── lib/
│   │   ├── auth.ts             # Better Auth server
│   │   ├── auth-client.ts      # Better Auth client
│   │   └── api.ts              # FastAPI client
│   ├── prisma/
│   │   └── schema.prisma       # Database schema
│   ├── .env                    # Frontend environment variables
│   └── package.json            # Node dependencies
│
├── run_servers.bat             # Run both servers (Windows)
├── run_backend.bat             # Run backend only
└── run_frontend.bat            # Run frontend only
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **UV** package manager ([Install UV](https://docs.astral.sh/uv/))
- **Neon Database** account ([Get one free](https://neon.tech/))

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd "d:\web development\Hackathon-II-testing\Phase-II"
   ```

2. **Setup Environment Variables**
   
   Both `.env` files are already configured with:
   - `DATABASE_URL` - Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET` - Shared secret for JWT signing/verification

### Running the Application

#### Option 1: Run Both Servers (Recommended)
Double-click `run_servers.bat` or run:
```bash
.\run_servers.bat
```
This opens both frontend and backend in separate windows.

#### Option 2: Run Servers Separately

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd neon-db-testing
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Create an Account
1. Open http://localhost:3000
2. Click **"Get Started"** or **"Sign up"**
3. Fill in your details and create an account

### 2. Manage Tasks
- **Create**: Click the **"+ New Task"** button
- **Edit**: Click the ✏️ icon on any task
- **Delete**: Click the 🗑️ icon
- **Complete**: Click the checkbox to mark complete/incomplete

### 3. Organize Tasks
- **Set Priority**: High (🔴), Medium (🟡), Low (🟢)
- **Add Tags**: Separate tags with commas (e.g., "Work, Urgent")
- **Set Due Date**: Use the date picker
- **Update Status**: Pending, In Progress, or Completed

### 4. Find Tasks
- **Search**: Type keywords in the search box
- **Filter**: Use dropdowns to filter by status/priority
- **Sort**: Sort by date created, due date, priority, or title

## 🔧 Database Schema

```prisma
model user {
  id            String    @id @default(cuid())
  name          String
  email         String    @unique
  emailVerified Boolean   @default(false)
  sessions      Session[]
  accounts      Account[]
  tasks         Task[]
}

model Task {
  id          String    @id @default(cuid())
  title       String
  description String?
  status      Status    @default(PENDING)
  priority    Priority  @default(MEDIUM)
  dueDate     DateTime?
  tags        String[]
  userId      String
  user        user      @relation(...)
}

enum Priority { HIGH, MEDIUM, LOW }
enum Status { PENDING, IN_PROGRESS, COMPLETED }
```

## 🔐 Security Features

- **JWT Authentication**: Stateless, secure token-based auth
- **Password Hashing**: Passwords hashed via Better Auth
- **Data Isolation**: All database queries filtered by user ID
- **CORS Protection**: Configured for localhost only
- **Environment Variables**: Sensitive data in `.env` files

## 📡 API Endpoints

### Authentication (Better Auth)
- `POST /api/auth/sign-up` - Register new user
- `POST /api/auth/sign-in` - Login
- `POST /api/auth/sign-out` - Logout
- `GET /api/auth/session` - Get current session
- `GET /api/auth/token` - Get JWT token

### Tasks (FastAPI)
- `GET /api/tasks` - List tasks (with filters)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task by ID
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/status` - Update status only
- `DELETE /api/tasks/{id}` - Delete task
- `DELETE /api/tasks` - Delete all completed tasks

All task endpoints require authentication via JWT token.

## 🧪 Testing

### Backend Health Check
```bash
Invoke-RestMethod -Uri http://localhost:8000/health | ConvertTo-Json
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "app": "Todo API"
}
```

### Frontend Test
Open http://localhost:3000 and verify:
- Landing page loads
- Registration works
- Login works
- Dashboard displays

## 🎨 Design Highlights

- **Premium Dark Theme** with gradient accents
- **Glassmorphism** effects on cards
- **Smooth Animations** on hover and interactions
- **Color-Coded Badges** for priority and status
- **Responsive Design** (mobile-friendly)
- **Modern Typography** using Inter font

## 🔄 Development Workflow

### Update Database Schema
1. Edit `prisma/schema.prisma`
2. Run: `npm run db:push` (in neon-db-testing folder)
3. Prisma Client auto-regenerates

### Add New Backend Feature
1. Create Pydantic model in `app/models/`
2. Add route in `app/routes/`
3. Register route in `app/main.py`

### Add New Frontend Page
1. Create `app/[page-name]/page.tsx`
2. Use `useSession()` to check auth
3. Use `taskApi` to call backend

## 📦 Dependencies

### Frontend (package.json)
- next: 16.1.4
- better-auth: ^1.4.17
- @prisma/client: ^7.3.0
- jose: ^5.2.0 (JWT signing)
- react: 19.2.3

### Backend (pyproject.toml)
- fastapi: >=0.115.0
- uvicorn: >=0.32.0
- asyncpg: >=0.30.0 (async PostgreSQL)
- pyjwt: >=2.9.0 (JWT verification)
- pydantic-settings: >=2.6.0

## 🐛 Troubleshooting

### Backend won't start
- Ensure you're in the `backend` folder when running uvicorn
- Check `.env` file exists with correct DATABASE_URL
- Run: `uv sync` to install dependencies

### Frontend won't start
- Run: `npm install` in neon-db-testing folder
- Check Node.js version (18+)
- Clear `.next` folder and rebuild

### Authentication issues
- Verify both `.env` files have the same `BETTER_AUTH_SECRET`
- Clear browser cookies/localStorage
- Check console for errors

### Database connection failed
- Verify Neon database is active
- Check DATABASE_URL format
- Test connection: `npx prisma db push`

## 📝 License

This project is built for educational purposes as part of a hackathon.

## 👏 Acknowledgments

- **Better Auth** for authentication
- **Neon** for serverless PostgreSQL
- **FastAPI** for the amazing Python framework
- **Next.js** for the React framework

---

**Built with ❤️ using Next.js, FastAPI, and Better Auth**
