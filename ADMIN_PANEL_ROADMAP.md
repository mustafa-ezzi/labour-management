# LabourPro — Admin + Subscription + Support Roadmap

Execution checklist for a full **app admin panel** (LabourPro staff only), **user subscription UX**, and **support messaging**.  
Check boxes as each task is completed. Do not skip phases that later work depends on.

---

## Core rule (roles)

There are only **two kinds of people** in the system:


| Role      | Who                                          | Access                                                             |
| --------- | -------------------------------------------- | ------------------------------------------------------------------ |
| **Admin** | LabourPro staff — **admin of the whole app** | `/admin/`** panel: manage all users, subscriptions, support        |
| **User**  | Everyone else (customers / company accounts) | Normal app: sites, crew, wages, materials + subscription + support |


**Important**

- There is **no other admin type** (no company admin, no site admin, no multi-admin hierarchy).
- Inside a company, people are just **users** of that company — not admins of the platform.
- The Admin controls the entire product; Users never see or call admin APIs.

---



## PWA + Admin on mobile (how you log in)

LabourPro is a **single PWA** for both Users and the App Admin. There is **no separate Admin app** to install.

### Same app, different account


| Who       | What they install                                      | What they sign in with                       | Where they land                     |
| --------- | ------------------------------------------------------ | -------------------------------------------- | ----------------------------------- |
| **User**  | LabourPro PWA (Add to Home Screen)                     | Their normal email/password                  | `/dashboard` → sites / crew / wages |
| **Admin** | **Same** LabourPro PWA (or Chrome/Safari on the phone) | App Admin email/password (`createsuperuser`) | `/admin` (Admin panel)              |




### Step-by-step (Admin on phone)

1. Open the LabourPro URL in **Chrome** (Android) or **Safari** (iPhone), or open the installed **LabourPro** home-screen icon.
2. If you were signed in as a normal User, **Sign out** first.
3. On the **Sign in** screen, enter the **App Admin** email + password (the `createsuperuser` account).
4. After login, the app detects `is_app_admin` and sends you to `/admin` (Dashboard, Accounts, Subscriptions, Plans, Support, Audit).
5. You manage the whole app from that Admin UI on the phone — same features as desktop, mobile layout already has a top tab strip.



### Important rules

- **Do not use your personal User account** for Admin work — Admin is only the superuser account.
- Normal Users **never** see Admin nav; if they open `/admin` they are redirected away.
- You can keep one PWA icon; switching User ↔ Admin = sign out → sign in with the other account.
- Optional later: bookmark `/admin` or add a second home-screen shortcut titled “LabourPro Admin” pointing at `https://your-app/admin` (still the same PWA).
- Prefer **Chrome/Edge** on Android for PWA install; on iPhone use Safari → Share → Add to Home Screen.



### Checklist (document / polish)

- [x] Same PWA hosts User app + `/admin` (no second install package)
- [x] Admin login on mobile uses the normal Sign in screen → auto-redirect to `/admin`
- [ ] Phase 6 polish: make Admin tables/forms comfortable on small screens (horizontal scroll / stacked rows)
- [ ] Optional: “Open Admin” hint only when `is_app_admin` (never shown to Users)

---



## How to use this file

- Mark a task done: change `- [ ]` → `- [x]`
- Keep notes under a task if scope changes
- Prefer shipping **Phase 0 → 1 → 2…** in order (auth & roles unlock everything else)

---



## Phase 0 — Product decisions (before coding)

> **Status: COMPLETE** — decisions locked below. Proceed to Phase 1.

- [x] Confirm role model: **one Admin (whole app)** vs **Users only** — no other admin roles
- [x] Decide how the single Admin account is bootstrapped (e.g. `is_staff` / `is_superuser` / `is_app_admin` flag)
- [x] Decide subscription unit: bill per **company** (recommended) or per user
- [x] Decide plans: e.g. Free trial / Monthly / Yearly (names, prices, duration)
- [x] Decide payment flow for v1: **manual renew by Admin** only, or online payment gateway later
- [x] Decide soft-disable vs hard-delete rules and recovery window (e.g. 14 days soft-delete)
- [x] Decide support channels: in-app tickets only for v1 (email later optional)
- [x] Sketch **Admin** IA: Dashboard, Users/Accounts, Subscriptions, Support, Settings
- [x] Sketch **User** IA: Subscription status page, Support page, existing site/crew flows unchanged



### Locked decisions



#### 1. Role model

- **Admin** = LabourPro staff only — sole controller of the whole app (`/admin/`**).
- **User** = everyone else (company accounts). No company-admin / site-admin / multi-admin roles.
- Company membership roles (`owner`, `manager`, etc.) stay for **in-company permissions only** — they are **not** platform admins.



#### 2. Admin bootstrap

- Use Django flags already on `User`: `is_staff=True` **+** `is_superuser=True` identifies the App Admin.
- Create via `python manage.py createsuperuser` (email + password).
- Gate admin APIs/UI with `IsAppAdmin` = `user.is_authenticated and user.is_superuser`.
- Do **not** add a separate `is_app_admin` column in v1 (avoids dual sources of truth). Revisit only if we need staff who are not full superusers.



#### 3. Subscription unit

- Bill / attach subscription to the **Company** (one subscription per company).
- All users under that company share the same plan status and end date.
- Matches existing `Company.subscription_plan` field (will be replaced/extended by a proper `Subscription` model in Phase 3).



#### 4. Plans (v1)


| Plan key  | Name       | Duration     | Notes                                     |
| --------- | ---------- | ------------ | ----------------------------------------- |
| `trial`   | Free trial | **14 days**  | Auto-assigned on new company registration |
| `monthly` | Monthly    | **30 days**  | Default paid plan                         |
| `yearly`  | Yearly     | **365 days** | Optional; Admin can assign                |


- Prices: store on `Plan` model but **v1 has no online checkout** — Admin sets/renews manually after payment outside the app (bank/JazzCash/etc.).
- Placeholder prices can be documented in admin (e.g. PKR amounts) without charging in-app.



#### 5. Payment flow (v1)

- **Manual renew by Admin only** — no Stripe/JazzCash gateway in v1.
- User sees plan + end date + “Contact support / pay to renew” messaging.
- Optional: User can open a support ticket or “renew request”; Admin marks paid via **Renew** action.
- Online payments = Phase 3b / Milestone E (parked).



#### 6. Disable vs delete


| Action      | Effect                                                                                                   | Reversible?      |
| ----------- | -------------------------------------------------------------------------------------------------------- | ---------------- |
| **Disable** | User cannot log in; company treated as inactive; data kept                                               | **Yes** (Enable) |
| **Delete**  | Hard-delete company + all related sites/crew/attendance/materials/payments/memberships/user(s) as scoped | **No**           |


- No soft-delete recovery window in v1 (keeps scope small). Disable is the reversible path.
- Delete requires typed confirmation (company name or `DELETE`) and an audit log entry.
- Do not allow Admin to delete their own Admin account.



#### 7. Support channels (v1)

- **In-app tickets only** (User ↔ Admin).
- No email/WhatsApp/SMS in v1 (optional later).
- Ticket statuses: `open` → `pending` → `resolved` → `closed`.



#### 8. Admin information architecture

```
/admin
├── Dashboard          KPIs: users, companies, active/expired subs, open tickets
├── Accounts           List → Detail (edit, disable/enable, delete)
├── Subscriptions      List ending-soon / expired; Renew / Cancel / set dates
                        (Cancel marks plan only — use Accounts to disable login)
├── Plans              CRUD for trial / monthly / yearly
├── Support            Inbox → Ticket thread + company/sub sidebar
└── Audit (optional)   Recent Admin actions
```

- Desktop-first Admin UI is OK for v1; **must still work on mobile PWA** (Admin logs in on phone — see “PWA + Admin on mobile” above).
- Admin never uses the normal site/crew bottom nav as their primary home.
- Same installed PWA; Admin vs User is only which account signs in.



#### 9. User information architecture

```
Existing app (unchanged core)
├── Sites / Crew / Wages / Materials / History …

New User pages
├── Subscription       Plan name, status, end date, days left, renew guidance
├── Support            Ticket list → New ticket → Thread
└── (Gate)             Full-page only when Admin has **disabled** the account
```

- Soft banner when < 7 days remaining; stronger alert when plan is expired.
- **Expired subscription does NOT auto-disable or lock the account.** App keeps working; User only sees alerts / renew messaging.
- To cut off access, Admin uses **Accounts → Disable** manually.
- Support + Subscription entries in app nav / settings area (exact placement in Phase 4/6).



### Phase 0 exit criteria

- [x] All decisions above written and agreed for v1
- [x] No code required for Phase 0 — ready for **Phase 1** (roles & `/admin` access control)

---



## Phase 1 — Roles, permissions & access control

> **Status: COMPLETE** — App Admin access control, audit log, `/admin` shell.



### Backend

- [x] App Admin = Django `is_superuser` (no separate `is_app_admin` column; Phase 0)
- [x] Do **not** invent company-level or site-level admin roles
- [x] DRF permission: `IsAppAdmin` for all `/api/admin/*` routes
- [x] Ensure **Users cannot** call any admin APIs
- [x] Admin can access admin APIs without needing a company membership (`/api/admin/me/`, dashboard)
- [x] Block login / API access for **disabled** user accounts (clear error message)
- [x] Subscription-expired enforcement **deferred to Phase 3**; gate page stub + API 403 redirect hook added
- [x] Audit log model (`AdminAuditLog`) + `/api/admin/audit/` list



### Frontend

- [x] Route guard: `/admin/**` only if current user is the App Admin (`middleware/admin.ts`)
- [x] Separate Admin layout (nav: Dashboard, Accounts, Plans, Support, Audit)
- [x] Never show Admin nav to normal Users
- [x] User-facing gate page stub: `/subscription-ended` (full subscription UI in Phase 3)



login?admin=1

### Phase 1 API surface


| Method | Path                    | Purpose           |
| ------ | ----------------------- | ----------------- |
| GET    | `/api/admin/me/`        | Admin identity    |
| GET    | `/api/admin/dashboard/` | KPI shell         |
| GET    | `/api/admin/audit/`     | Recent audit rows |
| GET    | `/api/admin/gate/`      | Permission probe  |


JWT claim: `is_app_admin` (true for active superusers).  
Bootstrap Admin: `python manage.py createsuperuser`  
**Mobile / PWA:** install LabourPro → Sign in with that Admin account → lands on `/admin` (see section above).

---



## Phase 2 — Account management (Admin only)

> **Status: COMPLETE** — list/search, edit, disable/enable, hard delete + audit. Soft-delete deferred (Phase 0).



### Data model

- [x] User profile fields editable by Admin: name, email, status (`is_active`)
- [x] Company name editable by Admin (owner reassignment deferred)
- [x] Account status: `active` | `disabled` (`pending_delete` skipped for v1)
- [x] Cascade map for delete (implemented in `account_admin.hard_delete_account`):
  - Owned Company → Sites → Labour → Attendance → LabourPayments (DB CASCADE)
  - Owned Company → Sites → Materials → MaterialUsage → MaterialPayments (DB CASCADE)
  - CompanyMemberships removed; owned companies deleted before user (`owner` is PROTECT)
  - User row deleted last (auth tokens / sessions follow user FK cascade)



### Admin APIs

- [x] `GET /api/admin/accounts/` — list users (search `q`, filter `status`)
- [x] `GET /api/admin/accounts/:id/` — detail (user + company + plan + usage counts)
- [x] `PATCH /api/admin/accounts/:id/` — update name, email, company name, `is_active`
- [x] `POST /api/admin/accounts/:id/disable/` — disable login
- [x] `POST /api/admin/accounts/:id/enable/` — re-enable
- [x] `DELETE /api/admin/accounts/:id/` — **hard delete** all related data (transactional)
- [ ] Soft-delete option (optional): anonymize + schedule purge job — **skipped for v1**
- [x] Confirmation payload required for delete (type company name / `DELETE`)
- [x] Write audit entries for every disable / enable / update / delete



### Admin UI

- [x] Accounts list: search, status badges, plan badge
- [x] Account detail: profile edit form, company summary, counts (sites, workers, materials)
- [x] Actions: Disable, Enable, Delete (danger zone with typed confirm)
- [x] Error handling for failed cascade deletes
- [x] Empty and loading states



### Safety

- [x] Prevent Admin from deleting their own Admin account (and any superuser)
- [x] DB transaction around hard delete; rollback on failure
- [x] Ops note: take a DB backup before using hard-delete in production

### Phase 2 API surface

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET | `/api/admin/accounts/` | List / search accounts |
| GET | `/api/admin/accounts/:id/` | Account detail |
| PATCH | `/api/admin/accounts/:id/` | Update profile / company name |
| POST | `/api/admin/accounts/:id/disable/` | Disable login |
| POST | `/api/admin/accounts/:id/enable/` | Re-enable |
| DELETE | `/api/admin/accounts/:id/` | Hard-delete workspace + user |
---



## Phase 3 — Subscriptions & billing lifecycle

> **Status: COMPLETE** (v1 manual renew). Enforcement: alerts only — never auto-disable.
>
> **Enforcement rule (locked):** plan expiry = **alerts only**. Never auto-disable login or block APIs.
> Cutting off a customer is always **Accounts → Disable** by Admin.



### Data model

- [x] `Plan` model: name, price, currency, duration_days, features JSON (optional)
- [x] `Subscription` model (per company): plan, status (`trialing` | `active` | `past_due` | `expired` | `cancelled`), `starts_at`, `ends_at`, `renewed_at`, notes
- [x] Seed default plans (trial / monthly / yearly)
- [x] On new company registration: auto-create trial subscription
- [x] Migration for existing companies: assign plan with an end date



### Admin APIs

- [x] `GET /api/admin/plans/` / `POST` / `PATCH` — manage plans
- [x] `GET /api/admin/subscriptions/` — list by status / ending soon
- [x] `POST /api/admin/subscriptions/:id/renew/` — extend `ends_at` by plan duration
- [x] `POST /api/admin/subscriptions/:id/cancel/` — mark cancelled (does **not** disable login)
- [x] `POST /api/admin/subscriptions/:id/set-dates/` — manual start/end override
- [x] Filter: subscriptions ending in N days



### User APIs

- [x] `GET /api/subscription/me/` — current plan, end date, days remaining, status
- [x] `GET /api/subscription/plans/` — plan list (for “pay / renew” info)
- [ ] Optional v1: `POST /api/subscription/renew-request/` — deferred (support tickets in Phase 4)



### Admin UI

- [x] Plans CRUD page
- [x] Subscriptions list: ending soon, expired, active
- [x] Per-company: Renew, Cancel, Change plan, Edit end date
- [x] Dashboard widgets: active subs, expiring this week, expired count



### User UI

- [x] **Subscription** page: plan name, status, **end date**, days left, renew guidance
- [x] Soft banners when < 7 days remaining; expired alert (app still usable)
- [x] `/subscription-ended` only for **disabled accounts** (not plan expiry)
- [x] Nav entry: Subscription



### Enforcement

- [x] Cron / management command: `mark_expired_subscriptions` (status only)
- [x] ~~API block when expired~~ — **won’t do** (alerts only)
- [x] ~~Frontend hard gate when expired~~ — **won’t do** (alerts only)



### Payments (later / optional Phase 3b)

- [ ] Choose gateway (Stripe / JazzCash / bank transfer manual)
- [ ] PaymentIntent / checkout session OR “mark paid” Admin workflow
- [ ] Payment history table linked to subscription renewals
- [ ] Receipts / invoice PDF (optional)

### Phase 3 API surface

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET/POST | `/api/admin/plans/` | List / create plans |
| PATCH | `/api/admin/plans/:id/` | Update plan |
| GET | `/api/admin/subscriptions/` | List / filter subscriptions |
| GET | `/api/admin/subscriptions/:id/` | Detail |
| POST | `/api/admin/subscriptions/:id/renew/` | Extend end date |
| POST | `/api/admin/subscriptions/:id/cancel/` | Mark cancelled (login unchanged) |
| POST | `/api/admin/subscriptions/:id/set-dates/` | Override dates |
| POST | `/api/admin/subscriptions/:id/change-plan/` | Switch plan |
| GET | `/api/subscription/me/` | User plan status |
| GET | `/api/subscription/plans/` | Public plan catalog |

---



## Phase 4 — Support messaging (User ↔ Admin)

> **Status: COMPLETE** — in-app tickets User ↔ Admin. Email notify optional later.



### Data model

- [x] `SupportTicket`: company, created_by (User), subject, status (`open` | `pending` | `resolved` | `closed`), priority, created_at, updated_at
- [x] `SupportMessage`: ticket, sender (User or Admin), body, attachments (optional later), created_at, `is_admin_reply`
- [x] Indexes for unread / open tickets



### User APIs

- [x] `GET /api/support/tickets/` — my company’s tickets
- [x] `POST /api/support/tickets/` — create ticket + first message
- [x] `GET /api/support/tickets/:id/` — thread
- [x] `POST /api/support/tickets/:id/messages/` — reply



### Admin APIs

- [x] `GET /api/admin/support/tickets/` — all tickets (filter status, company)
- [x] `GET /api/admin/support/tickets/:id/` — thread + company context
- [x] `POST /api/admin/support/tickets/:id/messages/` — Admin reply
- [x] `PATCH /api/admin/support/tickets/:id/` — change status / priority
- [x] Unread counts for Admin badge



### User UI

- [x] Support tab / page: list tickets
- [x] New ticket form (subject + message)
- [x] Conversation thread view
- [x] Status badges



### Admin UI

- [x] Support inbox (open first)
- [x] Ticket detail with company + subscription sidebar
- [x] Reply box + mark resolved / close
- [x] Optional: quick actions “renew plan” / “open account” from ticket



### Notifications (optional)

- [x] In-app unread badge (dot on unread tickets)
- [ ] Email notify Admin on new ticket
- [ ] Email notify User on Admin reply

### Phase 4 API surface

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET/POST | `/api/support/tickets/` | User list / create |
| GET | `/api/support/tickets/:id/` | User thread |
| POST | `/api/support/tickets/:id/messages/` | User reply |
| GET | `/api/admin/support/tickets/` | Admin inbox |
| GET/PATCH | `/api/admin/support/tickets/:id/` | Admin thread / status |
| POST | `/api/admin/support/tickets/:id/messages/` | Admin reply |
---



## Phase 5 — Admin dashboard & extra whole-app features

> **Status: COMPLETE** (v1) — KPIs, charts, search, CSV export, light rate limits.
> Skipped for v1: impersonate, feature flags, announcement banner.



- [x] KPI cards: total companies, active users, active subs, estimated MRR, open tickets
- [x] Charts: signups over time (30d bar chart), expiring subscriptions list
- [x] Recent audit log feed (on dashboard + full Audit page)
- [ ] Impersonate / “view as company” (read-only) — optional, deferred
- [x] Global search: company, user email, ticket id
- [x] Export CSV: accounts, subscriptions
- [ ] Feature flags per company (optional) — deferred
- [ ] Announcement banner for all Users (optional) — deferred
- [x] Rate limits on Admin delete / User support create

### Phase 5 API surface

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET | `/api/admin/dashboard/` | KPIs, signup series, expiring, audit, tickets |
| GET | `/api/admin/search/?q=` | Global search |
| GET | `/api/admin/exports/accounts/` | Accounts CSV |
| GET | `/api/admin/exports/subscriptions/` | Subscriptions CSV |
---



## Phase 6 — Frontend architecture (Admin panel + User app)

- [x] Same Nuxt **PWA** with `/admin` routes for Admin only (Users never enter)
- [ ] Admin design system: tables, filters, confirm dialogs, danger zones
- [ ] **Mobile-first Admin UX** — Admin operates from the phone PWA (not desktop-only)
- [ ] User Subscription + Support pages match existing LabourPro purple/white theme
- [ ] Empty states, skeletons, error banners
- [ ] Optional: second home-screen shortcut to `/admin` documented for LabourPro staff
- [ ] i18n not required for v1 unless needed

---



## Phase 7 — Testing, security & launch



### Testing

- [ ] Unit tests: cascade delete removes all company-linked rows
- [ ] Unit tests: disabled user cannot authenticate
- [ ] Unit tests: expired subscription enforcement
- [ ] API tests: normal **Users** cannot hit `/api/admin/`*
- [ ] Manual QA script: create user/company → trial → expire → Admin renew → support ticket → Admin delete account



### Security

- [ ] Confirm CSRF / JWT / session rules for Admin
- [ ] Confirm no PII leak in list endpoints
- [ ] Confirm delete is irreversible and logged
- [ ] Document how to create the **one App Admin** account (`createsuperuser` + `is_app_admin`)



### Deploy

- [ ] Migrations on Railway (plans, subscriptions, support, audit)
- [ ] Env vars for any payment/email providers
- [ ] Seed plans in production
- [ ] Create the App Admin account
- [ ] Update README / ops notes for Admin access
- [ ] Announce subscription end page to existing Users

---



## Suggested delivery milestones (ship slices)



### Milestone A — Admin foundation

- [x] Phase 1 complete (Admin vs User only)
- [x] Phase 2 (list / disable / edit / hard delete) complete



### Milestone B — Subscriptions

- [x] Phase 3 core (models, Admin renew/cancel, User alerts, no auto-disable)



### Milestone C — Support

- [x] Phase 4 complete (User tickets + Admin inbox)



### Milestone D — Hard delete + polish

- [x] Full cascade delete (shipped with Phase 2)
- [x] Phase 5 dashboard KPIs
- [ ] Phase 7 tests + production launch



### Milestone E — Payments (optional)

- [ ] Phase 3b online or semi-automated payments

---



## Out of scope for first release (park here)

- [ ] Extra admin roles (company admin, site admin, multi-staff RBAC) — **not in product**
- [ ] Multi-currency tax invoices
- [ ] WhatsApp / SMS support
- [ ] Full accounting ERP
- [ ] Multi-tenant white-label domains
- [ ] Mobile native stores (keep PWA)

---



## Progress summary


| Area            | Status                    |
| --------------- | ------------------------- |
| Decisions       | **Done** (Phase 0 locked) |
| Roles / access  | **Done** (Phase 1)        |
| Account admin   | **Done** (Phase 2)        |
| Subscriptions   | **Done** (Phase 3 — alerts only) |
| Support         | **Done** (Phase 4)        |
| Admin dashboard | **Done** (Phase 5)        |
| Launch / QA     | Not started               |


Update this table as milestones complete.

---



## Notes for implementers

1. **Admin** = LabourPro staff, sole controller of the whole app (`is_superuser`). **Users** = everyone else.
2. Do not build company/site “admin” roles for the platform — out of scope.
3. **PWA:** one install for everyone. Admin logs in on mobile with the Admin account and is routed to `/admin`; Users never see Admin UI.
4. **Delete entire account** = delete the **company tenant** and all site/crew/attendance/material/payment data owned by that company, plus memberships and related user record(s) as implemented in Phase 2.
5. **Disable** is reversible; **delete** is not. No soft-delete purge window in v1.
6. Subscriptions are **per company**; Admin renews manually in v1.
7. Support is **in-app tickets** only in v1.
8. Support tickets should show company + subscription context on the Admin side.
9. **Expired plan ≠ disabled account.** Expiry shows banners/alerts only; Admin disables login manually via Accounts when needed.

