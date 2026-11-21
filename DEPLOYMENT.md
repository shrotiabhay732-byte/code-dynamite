# Caraxes Deployment Guide

This document provides step-by-step instructions to deploy **Caraxes** (FastAPI backend + React frontend + Supabase + Gemini AI) into production.

---

## Architecture Overview

- **Frontend**: React 19 + Vite + Tailwind CSS (Deployable on **Vercel**, **Netlify**, or **Render Static Site**).
- **Backend**: FastAPI + Uvicorn Python 3.12 (Deployable on **Render**, **Railway**, **Fly.io**, or **Docker**).
- **Database & Storage**: **Supabase** (Postgres DB, Supabase Auth, and Storage bucket for uploads).
- **AI & OCR Engine**: Google Gemini API (`gemini-3.8-flash` for multi-engine text, vision audit, and serverless OCR).

---

## 1. Supabase Setup (Database & Storage)

1. Sign up or log into [supabase.com](https://supabase.com) and create a new project.
2. In the Supabase dashboard:
   - Navigate to the **SQL Editor**.
   - Copy the contents of [`db/schema.sql`](./db/schema.sql) and paste it into the query editor, then click **Run**.
   - (Optional) Run any additional migration files from [`db/migrations/`](./db/migrations/).
3. Navigate to **Storage**:
   - Create a new bucket named `caraxes-files`.
   - Set public access or standard RLS policies according to your privacy requirements.
4. Navigate to **Project Settings** $\to$ **API**:
   - Copy **Project URL** (this is `SUPABASE_URL`).
   - Copy the **`service_role`** secret key (this is `SUPABASE_SERVICE_KEY`).

---

## 2. Backend Deployment

### Option A: Render (Recommended)
1. Push your repository to GitHub.
2. Log into [render.com](https://render.com) and select **New +** $\to$ **Web Service**.
3. Connect your GitHub repository:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add the following **Environment Variables** in Render:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `SUPABASE_URL` | `https://xxxx.supabase.co` | Your Supabase project URL |
   | `SUPABASE_SERVICE_KEY` | `eyJhbGci...` | Supabase `service_role` secret key |
   | `SUPABASE_BUCKET` | `caraxes-files` | Storage bucket name |
   | `FRONTEND_ORIGIN` | `https://your-app.vercel.app,http://localhost:5173` | Allowed CORS origins (comma-separated, or `*` temporarily) |
   | `GEMINI_API_KEY` | `AIzaSy...` | Your Google Gemini API key |
   | `GEMINI_MODEL` | `gemini-3.8-flash` | Gemini model for RAG & visual audit |
   | `OCR_BACKEND` | `gemini` | **Crucial for Cloud**: Uses serverless Gemini OCR instead of heavy local C++ PaddleOCR |
   | `PYTHON_VERSION` | `3.12.0` | Python runtime version |
5. Click **Deploy Web Service**.
6. Once deployed, test your backend health:
   ```bash
   curl https://your-backend.onrender.com/health
   # Response: {"status":"ok","service":"caraxes-api"}
   ```

---

### Option B: Railway / Docker
1. Railway detects the [`backend/Dockerfile`](./backend/Dockerfile) automatically.
2. Set the same environment variables listed above in the Railway service settings.
3. Expose port `8000`.

---

## 3. Frontend Deployment

### Option A: Vercel (Recommended)
1. Log into [vercel.com](https://vercel.com) and click **Add New** $\to$ **Project**.
2. Select your Caraxes GitHub repository.
3. Configure project settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. In **Environment Variables**, add:
   | Variable | Value |
   | :--- | :--- |
   | `VITE_API_URL` | `https://your-backend.onrender.com` *(your live backend URL without trailing slash)* |
5. Click **Deploy**.
   *(SPA route rewrites are automatically handled by [`frontend/vercel.json`](./frontend/vercel.json)).*

---

### Option B: Netlify
1. Connect repository in Netlify.
2. Set **Base directory** to `frontend`.
3. Set **Build command** to `npm run build` and **Publish directory** to `dist`.
4. Add environment variable `VITE_API_URL=https://your-backend.onrender.com`.
   *(Client-side route fallback is automatically handled by [`frontend/public/_redirects`](./frontend/public/_redirects)).*

---

## 4. Post-Deployment Verification Checklist

- [ ] **Backend Health Probe**:
  `GET https://your-backend.onrender.com/health` returns HTTP 200 `{"status":"ok","service":"caraxes-api"}`.
- [ ] **Interactive Product Tour**:
  Visiting `https://your-frontend.vercel.app/` loads the Product Tour & Guide with live simulator and animations.
- [ ] **Company Authentication**:
  Click **Sign In** or **Get Started** to register a company account and verify the token.
- [ ] **Workspace Pre-Publication Check**:
  Paste marketing copy or upload an asset and run pre-publication check; verify findings and diff auto-fix work.
- [ ] **CORS Verification**:
  Ensure the browser console shows no CORS errors on API calls. If blocked, verify `FRONTEND_ORIGIN` on your backend includes your frontend domain.
