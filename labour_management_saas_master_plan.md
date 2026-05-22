# Labour Management SaaS App — Complete Product & Technical Plan

# Overview

This application is a mobile-first SaaS platform designed for contractors, construction companies, site supervisors, and labour managers.

The system will help users manage:

- Sites
- Labour attendance
- Labour wages
- Partial/full payments
- Material purchases
- Material payments
- Tool management
- Offline work mode
- Multi-user company accounts
- Reports & analytics

The app is designed primarily for:

- Construction businesses
- Contractors
- Labour supervisors
- Site managers
- Factory supervisors
- Civil work companies

---

# Core Vision

The goal is to replace:

- physical registers
- notebooks
- Excel sheets
- WhatsApp records
- manual calculations

with a modern:

- mobile-first
- offline-capable
- real-time synced
- installable PWA SaaS application

---

# Execution roadmap (milestones)

Use `**- [ ]**` for todo and `**- [x]**` when done. Work **top to bottom within each phase** before moving on; phases are ordered so the app stays coherent (API → UI → offline → polish).

## Phase 0 — Foundation and environments

- Repo layout chosen (monorepo vs `frontend/` + `backend/`) and created
- Python and Node versions pinned (e.g. `.python-version`, `engines` in `package.json`, or README)
- Local PostgreSQL (Docker or install) documented and working
- Backend: Django project bootstrapped; settings split (`base` / `dev` / `prod`); `.env.example`
- Frontend: Nuxt 3 bootstrapped with Pinia, Tailwind, API base URL config
- Path from dev machine to “one command” run for API + web documented
- Optional: CI on push (lint / tests)

## Phase 1 — Authentication, companies, first deploy

- Registration strategy decided (open signup vs invite-only vs admin-created companies)
- User registration and login APIs; JWT access + refresh (`/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`)
- Forgot / reset password flow
- `Company` model and `company_id` on every tenant-owned table; migrations applied
- All list/detail/create APIs scoped by `company_id` (no cross-tenant leakage)
- Frontend: login, register, logout, axios/fetch interceptor for refresh
- Staging deploy: API + PostgreSQL + frontend (e.g. Railway + Vercel or your chosen pair)

## Phase 2 — Sites module (first vertical slice)

- Site model matches plan (`company_id`, name, location, dates, audit fields)
- CRUD API: `/api/sites`, `/api/sites/:id` with company scoping
- Frontend: site list, create, edit, detail (mobile-first)
- Validation for `from_date` / `to_date`; optional computed `total_work_days` if in MVP scope

## Phase 3 — Labour module

- Labour model (attendance **not** embedded); links to `company_id`, `site_id`
- CRUD API for labour; list filter by site
- Frontend: labour list, add, edit, detail; active/inactive status

## Phase 4 — Attendance module

- Attendance model + API for daily mark (labour, site, date, present, optional overtime/notes)
- Bulk attendance API (`/api/attendance/bulk-mark`) and supervisor-friendly UI
- Date navigation suitable for cheap Android devices
- Monthly attendance view (summary or grid — define minimal MVP)

## Phase 5 — Labour payments and balances

- Labour payment model + API (full/partial, amounts, dates, notes, links as per your rules)
- Server-side balance / `remaining_amount` rules implemented and documented (including edits and corrections)
- Frontend: payment entry and per-labour payment history
- Pending wages visible where useful (dashboard or labour detail)

## Phase 6 — Materials and material payments

- Material model + CRUD API (`company_id`, `site_id`, quantity, unit, totals, supplier optional)
- Material payment model + API; partial and full payments
- Frontend: material list, add, payment tracking
- Bulk “selected materials” payment flow (totals for checked rows only)

## Phase 7 — Dashboard and reports (MVP)

- Dashboard cards: total sites, active sites, labour count, today’s attendance, pending wages, material spend (as data exists)
- Minimum report set: e.g. attendance for a range + pending payments (on-screen; export can follow)
- Pagination on large lists; basic API pagination

## Phase 8 — PWA and offline-first

- Installable PWA: manifest + service worker (Workbox or Nuxt PWA module)
- Dexie (IndexedDB) schema: sites, labour, attendance, materials, payments, **sync queue**
- Offline: writes saved locally and marked pending sync
- Sync engine: upload queue on reconnect; retries; user-visible errors for permanent failures
- Written **conflict policy** (e.g. server wins vs last-write-wins per resource type)

## Phase 9 — Roles, security, launch hardening

- Role-based permissions MVP (Owner / Manager / Supervisor / Accountant — start with smallest set you need)
- HTTPS everywhere; JWT lifetimes tuned; CORS locked to known origins
- Baseline rate limiting or throttling on auth endpoints
- Backup and restore verified on hosting; smoke-test checklist for staging

## Phase 10 — Post-MVP (commercial and scale)

Pick items when Phase 0–9 are stable.

### SaaS and product maturity

- Subscription plans and billing provider integration
- Full multi-role matrix and invitation flows
- Rich reports; PDF export; Excel export
- Analytics dashboards
- Push or email notifications

### Enterprise and long-term (from “Future features” in this doc)

- Tools module (issue, return, damage, maintenance)
- Urdu UI; photo uploads; WhatsApp-friendly summaries
- GPS / biometric attendance (if required by customers)
- Advanced accounting, invoicing, inventory, payroll automation
- Redis + Celery when background jobs are required; Django Channels or similar when realtime is required

---

# Main System Architecture

The app consists of:

1. Frontend (PWA)
2. Backend API
3. Database
4. Offline Local Database
5. Sync Engine
6. Authentication System
7. Multi-Tenant SaaS Layer

---

# Recommended Technology Stack

# Frontend Stack


| Technology   | Purpose                   |
| ------------ | ------------------------- |
| Nuxt 3       | Frontend framework        |
| Vue 3        | UI framework              |
| Tailwind CSS | Styling                   |
| Pinia        | State management          |
| Dexie.js     | Offline IndexedDB wrapper |
| Workbox      | PWA & caching             |
| VueUse       | Utility composables       |
| Axios        | API requests              |
| Day.js       | Date handling             |


---

# Why Nuxt 3?

Nuxt 3 is ideal because:

- excellent mobile performance
- SEO ready if needed later
- built-in routing
- layouts support
- middleware support
- easy PWA integration
- scalable structure
- Vue ecosystem familiarity

---

# Backend Stack


| Technology              | Purpose            |
| ----------------------- | ------------------ |
| Django                  | Backend framework  |
| Django REST Framework   | API layer          |
| PostgreSQL              | Main database      |
| Redis                   | Caching & queues   |
| Celery                  | Background jobs    |
| JWT Authentication      | Secure auth        |
| Django Channels (later) | Real-time features |


---

# Why Django?

This application behaves similarly to ERP software.

Django is perfect because it provides:

- secure authentication
- admin panel
- ORM
- scalable architecture
- financial data handling
- fast CRUD development
- mature ecosystem
- multi-user permission support

---

# Hosting Stack

# Frontend Hosting

Recommended:

- Vercel

---

# Backend Hosting

Recommended:

- Railway

Alternative:

- Render
- DigitalOcean
- AWS ECS

---

# Database Hosting

Recommended:

- Railway PostgreSQL

Alternative:

- Supabase PostgreSQL
- Neon PostgreSQL

---

# PWA Requirements

The application MUST support:

- installable app
- offline mode
- app-like behavior
- background sync
- cache management
- local data storage
- mobile optimization
- low network usage

---

# Offline First Architecture

# Why Offline Matters

Construction sites often have:

- poor internet
- unstable signals
- remote locations

The app should continue working even without internet.

---

# Offline Flow

User Action
↓
Stored in IndexedDB
↓
Marked as Pending Sync
↓
Internet Restored
↓
Sync Engine Uploads Data
↓
Backend Saves Data
↓
Sync Completed

---

# Local Database Strategy

Use:

- IndexedDB
- Dexie.js wrapper

Local storage should include:

- sites
- labour
- attendance
- materials
- tools
- payments
- sync queue

---

# Multi-Tenant SaaS Architecture

# Core Idea

Each company should only access its own data.

---

# Company Structure

Every table should include:

- company_id

Example:

## Company Table


| Field             | Type        |
| ----------------- | ----------- |
| id                | UUID        |
| name              | String      |
| owner             | Foreign Key |
| subscription_plan | String      |
| created_at        | DateTime    |


---

# Authentication System

# Recommended Auth

Use:

- JWT Access Token
- JWT Refresh Token

Features:

- secure login
- mobile sessions
- API protection
- multi-device support

---

# User Roles

# Suggested Roles


| Role       | Access                  |
| ---------- | ----------------------- |
| Owner      | Full access             |
| Manager    | Site management         |
| Supervisor | Attendance management   |
| Accountant | Financial reports       |
| Worker     | Optional future feature |


---

# Core Modules

# 1. Site Module

# Purpose

Each company can create multiple sites.

---

# Site Fields


| Field           | Type        |
| --------------- | ----------- |
| id              | UUID        |
| company_id      | Foreign Key |
| name            | String      |
| location        | String      |
| from_date       | Date        |
| to_date         | Date        |
| total_work_days | Integer     |
| created_by      | User        |
| created_at      | DateTime    |


---

# Auto Calculated Fields

The system should automatically calculate:

- total working days
- active duration
- completed duration

---

# Example

Name: Defence Project
Location: Karachi
From Date: 1 April
To Date: 30 April
Total Work Days: 29

---

# 2. Labour Module

# Purpose

Manage labour workers for each site.

---

# Labour Table


| Field        | Type            |
| ------------ | --------------- |
| id           | UUID            |
| company_id   | Foreign Key     |
| site_id      | Foreign Key     |
| name         | String          |
| daily_wage   | Decimal         |
| phone_number | Optional        |
| status       | Active/Inactive |
| created_at   | DateTime        |


---

# Important Design Decision

DO NOT store attendance inside labour table.

Attendance should be stored separately.

---

# 3. Attendance Module

# Purpose

Track daily labour presence.

---

# Attendance Table


| Field          | Type        |
| -------------- | ----------- |
| id             | UUID        |
| labour_id      | Foreign Key |
| site_id        | Foreign Key |
| date           | Date        |
| present        | Boolean     |
| overtime_hours | Optional    |
| notes          | Optional    |
| created_at     | DateTime    |


---

# Attendance Features

- mark daily attendance
- bulk attendance marking
- monthly attendance reports
- present/absent tracking
- overtime support later

---

# 4. Labour Payment Module

# Purpose

Handle:

- full payments
- partial payments
- pending balances
- salary history

---

# Labour Payment Table


| Field            | Type         |
| ---------------- | ------------ |
| id               | UUID         |
| labour_id        | Foreign Key  |
| attendance_id    | Foreign Key  |
| payment_type     | Full/Partial |
| amount_paid      | Decimal      |
| payment_date     | Date         |
| remaining_amount | Decimal      |
| notes            | Optional     |


---

# Labour Payment Logic

Example:

Daily Wage = 2000

Case 1:

Worker receives full 2000
Remaining = 0

payment_type = completed

Case 2:

Worker receives 1000
Remaining = 1000

payment_type = partial 

System should automatically calculate pending balance.

---

# 5. Material Module

# Purpose

Manage site material purchases.

---

# Material Table


| Field           | Type        |
| --------------- | ----------- |
| id              | UUID        |
| company_id      | Foreign Key |
| site_id         | Foreign Key |
| name            | String      |
| quantity        | Decimal     |
| unit_of_measure | String      |
| total_amount    | Decimal     |
| supplier        | Optional    |
| created_at      | DateTime    |


---

# Material Features

- add material entries
- quantity tracking
- supplier tracking
- material history
- pending payment support

---

# 6. Material Payment Module

# Purpose

Track payments against materials.

---

# Material Payment Table


| Field        | Type        |
| ------------ | ----------- |
| id           | UUID        |
| material_id  | Foreign Key |
| amount_paid  | Decimal     |
| payment_date | Date        |
| notes        | Optional    |


---

# Material Payment Features

- partial payments
- full payments
- bulk selected payments
- pending calculation

---

# Bulk Payment Workflow

Example:

Materials:

- Cement
- Sand
- Steel
- Bricks

User checks:

- Cement
- Steel

System calculates:

Selected total amount only.

---

# 7. Tools Module

# Status

Requirements pending.

Future possibilities:

- assigned tools
- damaged tools
- issued tools
- return tracking
- tool inventory
- maintenance logs

---

# Dashboard Features

# Main Dashboard

Should show:

- total sites
- active sites
- labour count
- today attendance
- pending wages
- material expenses
- total site expenses

---

# Reports Module

# Recommended Reports


| Report                 | Purpose              |
| ---------------------- | -------------------- |
| Labour Wage Report     | Worker payments      |
| Attendance Report      | Presence tracking    |
| Site Expense Report    | Cost tracking        |
| Material Report        | Purchase analysis    |
| Pending Payment Report | Outstanding balances |
| Monthly Summary        | Financial overview   |


---

# Mobile First UI Strategy

# Design Goals

The UI should:

- work on cheap Android devices
- support one-hand use
- use large touch targets
- minimize typing
- use fast navigation
- support dark mode later

---

# UI Recommendations

Use:

- bottom navigation
- card-based UI
- large buttons
- swipe interactions later
- floating quick actions

---

# Suggested Pages

# Authentication

- Login
- Register
- Forgot Password

---

# Dashboard

- Summary cards
- Recent activity
- Quick actions

---

# Sites

- Site list
- Site details
- Create site
- Edit site

---

# Labour

- Labour list
- Labour details
- Add labour
- Payment history

---

# Attendance

- Daily attendance page
- Monthly attendance view
- Bulk attendance marking

---

# Materials

- Material list
- Add material
- Payment tracking

---

# Reports

- Financial summaries
- Export PDF later
- Export Excel later

---

# API Structure Recommendation

# Example Endpoints

## Auth

/api/auth/login
/api/auth/register
/api/auth/refresh

---

## Sites

/api/sites
/api/sites/:id

---

## Labour

/api/labours
/api/labours/:id

---

## Attendance

/api/attendance
/api/attendance/bulk-mark

---

## Materials

/api/materials
/api/material-payments

---

# Suggested Folder Structure

# Frontend Structure

src/
├── components/
├── pages/
├── layouts/
├── composables/
├── stores/
├── services/
├── offline/
├── utils/
├── types/
└── middleware/

---

# Backend Structure

backend/
├── apps/
│   ├── authentication/
│   ├── companies/
│   ├── sites/
│   ├── labour/
│   ├── attendance/
│   ├── materials/
│   ├── payments/
│   └── reports/
├── config/
└── requirements/

---

# Security Recommendations

# Required Security

- HTTPS
- JWT expiration
- role permissions
- API validation
- rate limiting later
- encrypted passwords
- secure refresh tokens

---

# Performance Optimization

# Important Optimizations

- lazy loading
- route splitting
- IndexedDB caching
- pagination
- optimized API queries
- background sync queues

---

# Future Features Roadmap

# Phase 2 Features

- push notifications
- WhatsApp reports
- Urdu language support
- photo uploads
- salary slips
- biometric attendance
- GPS attendance
- expense analytics
- AI insights later

---

# Phase 3 Features

- accounting module
- invoice generation
- inventory management
- payroll automation
- contractor marketplace
- worker profiles
- subcontractor system

---

# Development roadmap (reference)

**Authoritative build order and tick boxes:** see [Execution roadmap (milestones)](#execution-roadmap-milestones) above. The lists below stay as quick product-memory only (not the checklist).

- **MVP:** auth, company, sites, labour, attendance, labour payments, materials + material payments, offline + PWA, minimal dashboard/reports.
- **SaaS next:** subscriptions, roles, richer reports/exports, analytics, notifications.
- **Enterprise later:** accounting depth, tools, inventory, payroll automation, AI analytics.

---

# Final Recommended Stack Summary

# Frontend

- Nuxt 3
- Vue 3
- Tailwind CSS
- Pinia
- Dexie.js
- Workbox

---

# Backend

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT Authentication

---

# Infrastructure

- Vercel
- Railway
- PostgreSQL
- IndexedDB

---

# Final Product Goal

A modern offline-first labour and construction management SaaS platform optimized for:

- Pakistan market
- contractors
- site supervisors
- labour-intensive businesses
- mobile usage
- low internet environments

with the ability to scale into a full ERP ecosystem later.