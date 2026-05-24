# Deploy HSUSMS Live

## 1. Push to GitHub

Create a new repository on [GitHub](https://github.com/new) named `harare-smart-security` (public, no README).

Then run:

```powershell
cd C:\Users\PC\Projects\harare-smart-security
git remote add origin https://github.com/YOUR_USERNAME/harare-smart-security.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## 2. Host live on Render (free)

1. Go to [https://dashboard.render.com](https://dashboard.render.com) and sign in (GitHub login works).
2. Click **New +** → **Blueprint** (or **Web Service**).
3. Connect your `harare-smart-security` repository.
4. Render reads `render.yaml` automatically.
5. Click **Apply** / **Create Web Service**.
6. Wait ~5–10 minutes for the build.

Your live URL will be like: `https://hsusms-harare.onrender.com`

- Dashboard: `https://hsusms-harare.onrender.com/`
- Citizen app: `https://hsusms-harare.onrender.com/citizen.html`
- API docs: `https://hsusms-harare.onrender.com/docs`

> **Note:** Free tier sleeps after inactivity; first load may take ~30 seconds.

## 3. Update Flutter app (optional)

In `mobile/hsusms_citizen/lib/services/api_service.dart`:

```dart
static String baseUrl = 'https://hsusms-harare.onrender.com/api';
```

## 4. Alternative: Railway

1. [https://railway.app](https://railway.app) → New Project → Deploy from GitHub repo.
2. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add variable `PORT` = `8000` if needed.
