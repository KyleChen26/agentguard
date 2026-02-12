# Zero-Cost Deployment Plan

**Date:** 2026-02-12  
**Goal:** Run AgentGuard completely free  
**Estimated Monthly Cost:** $0

---

## Free Architecture

```
User
  ↓ HTTPS
GitHub Pages / Vercel (Frontend)
  ↓ API Calls
Render / Fly.io (Backend)
  ↓ Queries
Supabase / Neon (PostgreSQL)
```

---

## Frontend: GitHub Pages (Free Forever)

**Why GitHub Pages:**
- ✅ 100% free, no limits
- ✅ Custom domain support
- ✅ Automatic deploy from GitHub
- ✅ CDN via CloudFlare
- ✅ SSL certificate included

**Implementation:**
- Static site (React/Vue/Svelte)
- Build with GitHub Actions
- Deploy to `gh-pages` branch

**Limitations:**
- Static only (no server-side rendering)
- No API routes (backend needed)

**Workaround:**
- Pure frontend app
- Call backend API directly
- Host docs/landing pages

---

## Backend: Render Free Tier

**Why Render:**
- ✅ Free tier: 512MB RAM, shared CPU
- ✅ Unlimited bandwidth
- ✅ Automatic deploy from GitHub
- ✅ Persistent disk (for logs)

**Free Tier Limits:**
- 512MB RAM
- 0.1 CPU
- Spins down after 15 min idle (30s cold start)

**Optimization:**
- Keep alive with cron job (ping every 10 min)
- Use for API + lightweight scanning
- Background jobs on GitHub Actions

**Alternative:**
- **Fly.io free tier**: 3 shared CPUs, 256MB RAM
- **Railway trial**: $5 credit, then need to pay
- **AWS Lambda**: 1M requests free (pay per use)

---

## Database: Supabase Free Tier

**Why Supabase:**
- ✅ 500MB database (PostgreSQL)
- ✅ 2GB bandwidth
- ✅ Unlimited API requests
- ✅ Real-time subscriptions
- ✅ Auth included

**Free Tier:**
- 500MB database
- 2GB bandwidth
- 200MB file storage
- Paused after 7 days inactivity (can unpause)

**Alternative:**
- **Neon**: 3GB storage, 190 compute hours
- **CockroachDB**: 5GB storage
- **PlanetScale**: MySQL-compatible

---

## Alternative: SQLite on Backend

For true zero-cost:
- SQLite database on Render disk
- No separate database service
- Limitations: Single server, no concurrent writes
- Good enough for MVP

---

## Complete Free Stack

### Option A: Minimal (No DB)

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | GitHub Pages | $0 |
| Backend | Render | $0 |
| Database | SQLite (on disk) | $0 |
| **Total** | | **$0** |

**Pros:** Simple, truly free  
**Cons:** No horizontal scaling, data on single server

---

### Option B: With PostgreSQL

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | Vercel Free | $0 |
| Backend | Render Free | $0 |
| Database | Supabase Free | $0 |
| **Total** | | **$0** |

**Pros:** Real PostgreSQL, better data model  
**Cons:** Supabase pauses after 7 days inactivity

---

### Option C: GitHub Actions for Scanning

**Innovation:** Use GitHub Actions as scanning backend

```yaml
# .github/workflows/agentguard-scan.yml
name: AgentGuard Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AgentGuard
        run: |
          pip install agentguard
          agentguard scan . --format json --output results.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: results.json
```

**Architecture:**
```
Frontend (Vercel)
  ↓ Triggers
GitHub Actions (Scanning)
  ↓ Stores results
GitHub Artifacts / Gist
  ↓ Displays
Frontend (Vercel)
```

**Pros:**
- ✅ Completely free (2000 minutes/month)
- ✅ No backend server needed
- ✅ GitHub-native integration

**Cons:**
- ❌ 6-hour job limit
- ❌ Not real-time
- ❌ Limited to GitHub repos

---

## Free Tier Comparison

| Service | CPU | RAM | Storage | Bandwidth | Limitations |
|---------|-----|-----|---------|-----------|-------------|
| **Render** | Shared | 512MB | N/A | Unlimited | Spins down after 15min |
| **Fly.io** | 3 shared | 256MB | N/A | 160GB/mo | Requires credit card |
| **Railway** | Shared | 512MB | 1GB | 100GB | $5 trial only |
| **Vercel** | N/A | N/A | N/A | 100GB/mo | Functions 30s limit |
| **Netlify** | N/A | N/A | N/A | 100GB/mo | 125k function calls |
| **Supabase** | N/A | N/A | 500MB | 2GB/mo | Pauses after 7 days |
| **Neon** | N/A | N/A | 3GB | N/A | 190 compute hours |

---

## Recommended Free Architecture

### MVP (Months 1-3)

```
┌─────────────────┐
│  GitHub Pages   │  ← Landing, docs (free forever)
│  (Static site)  │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Render │  ← API, lightweight scanning
    │  (Free) │     512MB RAM, spins down
    └────┬────┘
         │
    ┌────▼──────┐
    │  Supabase │  ← PostgreSQL (500MB)
    │  (Free)   │     Pauses after 7 days
    └───────────┘
```

**Cost:** $0/month

**Trade-offs:**
- Cold starts (30s) after idle
- Supabase pauses (can unpause manually)
- Limited resources (but enough for MVP)

---

### Optimization for Free Tier

**1. Keep Backend Alive**
```bash
# Cron job (GitHub Actions) pings every 10 min
curl https://agentguard-api.onrender.com/health
```

**2. Prevent Supabase Pausing**
- Weekly automated query via GitHub Actions
- Or use SQLite on Render disk instead

**3. CDN Optimization**
- Static assets on GitHub Pages (unlimited)
- API responses cached (Render doesn't charge for cache)

**4. Rate Limiting**
- 100 requests/minute per IP
- Prevents abuse, stays within free tiers

---

## When to Upgrade (Pay)

**Render → Paid ($7/mo) when:**
- Consistent traffic (cold starts annoying)
- Need > 512MB RAM
- Background jobs exceed free limits

**Supabase → Paid ($25/mo) when:**
- Database > 500MB
- Need backups/HA
- Can't tolerate pausing

**Vercel → Pro ($20/mo) when:**
- Bandwidth > 100GB
- Need team features
- Analytics important

**Expected:** Month 4-6 if traction

---

## Complete Free Setup Guide

### 1. GitHub Pages (Frontend)

```bash
# Create gh-pages branch
git checkout --orphan gh-pages

# Add index.html
echo "<!DOCTYPE html><html><body><h1>AgentGuard</h1></body></html>" > index.html

git add index.html
git commit -m "Initial page"
git push origin gh-pages

# Enable GitHub Pages in repo settings
# Source: Deploy from branch → gh-pages
```

### 2. Render (Backend)

```bash
# Create render.yaml
services:
  - type: web
    name: agentguard-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    plan: free
```

### 3. Supabase (Database)

```bash
# Sign up at supabase.com
# Create new project (free tier)
# Get connection string
# Run migrations
```

### 4. Custom Domain (Optional)

```
Cloudflare (free) → DNS → GitHub Pages + Render
```

---

## Cost Comparison: Free vs Paid

| Stage | Free | Paid | Difference |
|-------|------|------|------------|
| **MVP** | $0 | $25/mo | Save $25/mo |
| **Scale** | $0* | $55/mo | Save $55/mo |
| **Growth** | $0** | $150/mo | Save $150/mo |

*With limitations: cold starts, pausing  
**Will eventually need to pay

---

## Realistic Free Timeline

**Months 1-3:** Pure free tier  
**Month 4:** Consider Render paid ($7) if traction  
**Month 6:** Consider Supabase paid ($25) if database grows  
**Month 12:** Full paid stack ($55) if revenue supports

**Bootstrapping advantage:** Run free until revenue justifies costs.

---

## Final Recommendation

**Use Free Tier for MVP.**

**Architecture:**
- Frontend: GitHub Pages (free forever)
- Backend: Render Free (with keep-alive)
- Database: Supabase Free (or SQLite on Render)

**Total: $0/month**

**Upgrade path:** Clear and easy when needed.

---

*Zero-cost deployment plan for bootstrapped MVP.*
