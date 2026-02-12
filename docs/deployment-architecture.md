# Deployment Architecture

**Date:** 2026-02-12  
**Status:** Architecture decision for AgentGuard infrastructure

---

## System Architecture

```
User
  ↓ HTTPS
Vercel (Frontend - Next.js)
  ↓ API Calls
Railway/Render (Backend - FastAPI)
  ↓ Queries
PostgreSQL (Database)
  ↓ Stores
Scan Results, User Data
```

---

## Frontend: Vercel

**Why Vercel:**
1. **Next.js Native** — Zero-config deployment for Next.js apps
2. **Automatic CI/CD** — Push to GitHub → automatic deploy
3. **Global CDN** — Edge network, fast worldwide
4. **Serverless Functions** — API routes handled at edge
5. **Free Tier Generous** —
   - 100GB bandwidth
   - 6,000 build minutes
   - Perfect for MVP

**What Runs on Vercel:**
- Next.js dashboard
- Static pages (landing, docs)
- API routes (lightweight, < 30s)

**What Does NOT Run on Vercel:**
- Heavy scanning engine (30s limit)
- Background jobs
- Long-running processes

**Alternatives Considered:**
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Cloudflare Pages** | Edge network, fast | Limited Next.js features | Good alternative |
| **Netlify** | Similar to Vercel | Slightly slower builds | Good alternative |
| **AWS Amplify** | AWS integration | Complex, overkill | Too complex |
| **Self-hosted** | Full control | Maintenance burden | Not for MVP |

**Decision:** Vercel (or Cloudflare Pages if issues)

---

## Backend: Railway (or Render)

**Why NOT Vercel for Backend:**
1. **30-second timeout** — Scanning can take minutes
2. **Serverless limitations** — Not designed for CPU-intensive tasks
3. **Cold starts** — Bad for consistent API performance
4. **No persistent storage** — Need database connection

**Why Railway:**
1. **Python-native** — First-class Python support
2. **PostgreSQL included** — One-click database
3. **Persistent processes** — Long-running containers
4. **Simple deployment** — Git push → deploy
5. **Cheap** — $5/month starter

**What Runs on Railway:**
- FastAPI application server
- Celery workers (background scanning)
- PostgreSQL database
- Redis (caching, job queue)

**Alternatives Considered:**
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Render** | Similar to Railway | Slightly more expensive | Good alternative |
| **Fly.io** | Edge deployment | Learning curve | Overkill |
| **AWS ECS** | Scalable | Complex, expensive | Too complex |
| **Google Cloud Run** | Serverless containers | Cold starts, timeouts | Not suitable |
| **Hetzner/VPS** | Cheap, full control | Maintenance burden | Not for MVP |

**Decision:** Railway (or Render if issues)

---

## Database: PostgreSQL (via Railway)

**Why PostgreSQL:**
- Relational data (users, scans, findings)
- JSONB for flexible scan results
- ACID compliance
- Well-supported in Python (SQLAlchemy)

**Hosting:** Railway provides managed PostgreSQL
- Automatic backups
- Connection pooling
- $0 included in $5 plan

---

## Cost Breakdown

### MVP Stage (Months 1-6)

| Service | Plan | Cost | Notes |
|---------|------|------|-------|
| **Vercel** | Free | $0 | 100GB bandwidth, enough for MVP |
| **Railway** | Starter | $5/mo | 512MB RAM, shared CPU |
| **PostgreSQL** | Included | $0 | 1GB storage, via Railway |
| **Domain** | - | $12/yr | Custom domain |
| **Stripe** | - | $0 | Pay per transaction (2.9% + $0.30) |
| **Total** | - | **$5/mo** | + domain yearly |

### Scale Stage (Months 6+)

If traction:
- Railway → $20/mo (2GB RAM, dedicated CPU)
- Vercel → $20/mo (Pro plan, more bandwidth)
- PostgreSQL → $15/mo (larger instance)
- **Total: ~$55/mo**

Still cheap compared to AWS ($200+/mo for equivalent).

---

## Deployment Flow

### 1. Developer pushes code
```bash
git push origin main
```

### 2. Frontend deploys (Vercel)
- Vercel detects push
- Builds Next.js app
- Deploys to global CDN
- ~30 seconds

### 3. Backend deploys (Railway)
- Railway detects push
- Builds Docker container
- Runs migrations
- Deploys new version
- ~2 minutes

### 4. Zero-downtime
- Rolling deployments
- Health checks
- Automatic rollback if fails

---

## Why This Architecture?

**Principles:**
1. **Serverless where possible** (frontend) — scales to zero, cheap
2. **Containers where needed** (backend) — persistent, flexible
3. **Managed services** — focus on product, not infrastructure
4. **Cheap to start** — $5/mo, scale as needed

**Trade-offs:**
- ✅ Fast time to market
- ✅ Low operational burden
- ✅ Scales with usage
- ⚠️ Vendor lock-in (acceptable for MVP)
- ⚠️ Not cheapest at scale (migrate later if needed)

---

## Migration Path (Future)

If we need to migrate off these platforms:

**Frontend:**
- Next.js export → static files
- Host on Cloudflare Pages, S3, or any CDN
- ~1 day migration

**Backend:**
- Docker container → any container host
- AWS ECS, GCP Cloud Run, or VPS
- ~2 days migration

**Database:**
- pg_dump → import to new PostgreSQL
- AWS RDS, GCP Cloud SQL, or self-hosted
- ~1 day migration

**Conclusion:** Not locked in forever. Easy to migrate if needed.

---

## Decision Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Frontend** | Vercel | Next.js native, free, fast |
| **Backend** | Railway | Python support, cheap, persistent |
| **Database** | Railway PostgreSQL | Included, managed, simple |
| **Total Cost** | $5/mo | Affordable for bootstrapping |

**Alternative if issues:**
- Frontend → Cloudflare Pages
- Backend → Render
- Database → Supabase

---

*Deployment architecture for AgentGuard MVP.*
