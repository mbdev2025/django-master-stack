# ⚡ Enedis Integration Documentation (Linky Monitor)

Current Status: **PRODUCTION CONFIGURED** (Waiting for Keys)
Configuration File: `.env`

---

## 🚀 Environment Configuration

The application supports two environments for interacting with Enedis API: **Sandbox** (Testing) and **Production** (Real Clients).
To switch between them, **only modify the `.env` file**. Do not change the code.

### 1. Production Mode (Current)
Use this mode when deploying to `energysobriete.com` or processing real client data.

**`.env` Settings:**
```ini
# Production Credentials
ENEDIS_CLIENT_ID=REMPLACER_PAR_VOS_CLES_PROD
ENEDIS_CLIENT_SECRET=REMPLACER_PAR_VOS_CLES_PROD
ENEDIS_REDIRECT_URI=https://energysobriete.com/api/energy/auth/callback/

# Production URLs
ENEDIS_API_BASE_URL=https://gw.enedis.fr/v1
ENEDIS_AUTH_URL=https://mon-compte-particulier.enedis.fr/dataconnect/v1/oauth2/authorize
ENEDIS_TOKEN_URL=https://gw.enedis.fr/v1/oauth2/token
```

### 2. Sandbox Mode (Testing)
Use this mode to test the application logic without affecting real clients or production quotas.
This mode bypasses standard user login (OAuth2 Code Flow) and uses **Client Credentials** to fetch simulated data.

**`.env` Settings (Comment out Prod / Uncomment Sandbox):**
```ini
# Sandbox Credentials (Public Test Keys)
ENEDIS_CLIENT_ID=J0Ikt1bIiD9h3r_lJJnr4BziMkIa
ENEDIS_CLIENT_SECRET=aUyKyKpKtSCcgAdKmAzsdOy9STUa
# Redirect URI is irrelevant in Client Credentials flow, but good to keep consistent
ENEDIS_REDIRECT_URI=http://127.0.0.1:8000/api/energy/auth/callback/

# Sandbox URLs
ENEDIS_API_BASE_URL=https://ext.prod-sandbox.api.enedis.fr
ENEDIS_TOKEN_URL=https://ext.prod-sandbox.api.enedis.fr/oauth2/v3/token
# AUTH_URL is not used in Sandbox (no user login simulation needed for backend calls)
```

---

## 🛠️ Sandbox Tools & Scripts

We have implemented several tools to validate the integration before going to production.

### A. Connectivity Test Command
Run this command to verify that the server can authenticate and fetch data from Enedis Sandbox.
```bash
python3 manage.py test_enedis_sandbox
```
**Expected Output:**
- `✅ Token Received`
- `📉 Fetching Load Curve...`
- `✅ Data Received! (336 points)`

### B. Data Synchronization API
The dashboard uses this endpoint to fetch real Sandbox data seamlessly.
- **Endpoint:** `POST /api/energy/sandbox/sync/`
- **Logic:** Authenticates via Client Credentials -> Fetches last 30 days Load Curve -> Stores in DB -> Returns raw points for Chart.
- **View Class:** `apps.energy.views.SyncSandboxDataView`

---

## 🖥️ Simulation Dashboard (`simulation.html`)

The dashboard at `/dashboard/simulation/` has a dual behavior:

1.  **Real Data Mode (Priority):**
    On load, it attempts to call `/api/energy/sandbox/sync/`.
    - If successful (Sandbox Config Active), it displays the **REAL Load Curve** returned by Enedis.
    - Data is aggregated client-side (30-min Watt -> Daily kWh).

2.  **Mock Mode (Fallback):**
    If the API call fails (e.g., restricted network, misconfigured keys), it falls back to **simulated random data**.
    - This ensures the demo NEVER breaks during a presentation.
    - "Connexion Enedis..." simulates a loading delay for realism.

### Client Persistence
- Simulated clients (M. Jean Dupont) are stored in browser `localStorage`.
- To reset: Clear browser cache or run `localStorage.clear()` in console.

---

## ⚠️ Troubleshooting

**Error: 403 Forbidden (Interactive Login)**
- **Cause:** You are trying to use Sandbox keys on Production URL, or vice-versa.
- **Fix:** Check `ENEDIS_API_BASE_URL` in `.env`.

**Error: "URI de redirection incorrecte"**
- **Cause:** The `ENEDIS_REDIRECT_URI` in `.env` does not match exactly what was declared in Enedis DataConnect portal.
- **Fix:** Ensure `https://energysobriete.com/api/energy/auth/callback/` is used in Prod.

**Error: "Client id inconnu"**
- **Cause:** Typo in Client ID or using Sandbox ID in Prod.
- **Fix:** Copy-paste keys carefully without spaces.
