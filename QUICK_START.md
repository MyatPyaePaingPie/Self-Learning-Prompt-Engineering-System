# 🚀 Quick Start Guide - Unified Frontend

## ✅ What's Consolidated

All features are now in **ONE** authenticated Streamlit app at `frontend/app.py`:

- ✅ **Login/Registration** - Secure authentication with JWT tokens
- ✅ **Prompt Enhancement** - AI-powered prompt optimization
- ✅ **Token Analytics** - Track usage and costs
- ✅ **Security Dashboard** - Monitor security inputs and risk scores
- ✅ **API Testing** - Test endpoints directly

## 🏃 Running the Application

### Step 1: Start the Backend (ONE Backend with Everything)

```bash
cd /Users/ariahan/Documents/persistos/Self-Learning-Prompt-Engineering-System

# Start the ONE authenticated backend on port 8001
python3 -m uvicorn backend.main:app --reload --port 8000
```

**Backend will be available at:** `http://localhost:8001`
**API Docs:** `http://localhost:8001/docs`

### Step 2: Start the Frontend

```bash
# In a new terminal
cd /Users/ariahan/Documents/persistos/Self-Learning-Prompt-Engineering-System

# Run the unified authenticated frontend
python3 -m streamlit run frontend/app.py
```

**Frontend will be available at:** `http://localhost:8501`

## 📱 Using the Application

### 1. **Register an Account**
- Go to `http://localhost:8501`
- Click the "📝 Register" tab
- Create an account with:
  - Username (3-50 characters)
  - Email address
  - Password (min 6 chars, must have letters and numbers)

### 2. **Login**
- Click the "🔑 Login" tab
- Enter your credentials
- You'll be redirected to the dashboard

### 3. **Navigate Features**

In the sidebar, you can access:

- **🚀 Prompt Enhancement** - Optimize your prompts
- **📊 Dashboard** - Overview and quick actions
- **💰 Token Analytics** - View token usage and costs (after enhancing a prompt)
- **🔒 Security Dashboard** - Monitor security inputs
- **🔧 API Testing** - Test API endpoints

## ✅ Fully Integrated

Everything now uses **ONE authenticated backend** (`backend/main.py` on port 8001):
- ✅ Authentication (Login/Register)
- ✅ Prompt Enhancement
- ✅ Token Analytics
- ✅ Security Dashboard (with authentication)
- ✅ API Testing

## 🗂️ Deleted Files

These files have been **removed** (all features consolidated):
- ❌ `backend/api.py` - Merged into `backend/main.py`
- ❌ `apps/web/` - All moved to `frontend/app.py`

## 🐛 Troubleshooting

**Issue:** "Could not connect to API"
- **Fix:** Make sure the backend is running on port 8000

**Issue:** "Authentication failed"
- **Fix:** Check that `backend/main.py` is running on port 8000

**Issue:** "Security Dashboard empty"
- **Fix:** Security inputs are logged when you use prompt enhancement with risk analysis enabled

**Issue:** "Module not found"
- **Fix:** Install requirements: `pip install -r frontend/requirements.txt`

## 🎯 Architecture

**ONE Backend (`backend/main.py` on port 8001):**
- Authentication (JWT tokens)
- Prompt enhancement endpoints
- Security dashboard endpoints
- All features secured with authentication

**ONE Frontend (`frontend/app.py` on port 8501):**
- Login/Registration UI
- Prompt Enhancement
- Token Analytics
- Security Dashboard
- All authenticated

**Simple. Clean. Working.**

