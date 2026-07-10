# LabourPro — Mobile UI Specification (for Replit)

**UI only.** No backend, API, or database details.
**Target:** Mobile phone portrait (375–430px width), touch-first, construction-site supervisors.

This version replaces the earlier flat/white-heavy draft. Direction now: **richer color, icon-first, collapsible sections, fewer full-page redirects** — especially for daily crew attendance + pay, which becomes **one combined screen**.

---

## Design philosophy (updated)

- **Richer color** — purple is no longer just a thin accent. Use it confidently: gradient header bars, colored icon chips, colored badges, colored progress/pending indicators. White is still the base canvas, but the app should feel **branded and vivid**, not sterile.
- **Icons over cards** — for quick actions and secondary info, prefer a **compact icon + label** (icon button / icon row) instead of a large descriptive card with heading + subtitle + padding. Reserve full cards for genuinely important content (forms, summaries, the current focus of the screen).
- **Collapsible, not stacked** — sections that aren't always needed (stats detail, worker history, notes) should be **accordions/expandable rows** — collapsed by default, tap to expand. This keeps first-view screens short.
- **Sleek & clean** — tighter spacing, smaller icon-based headers, fewer borders, more use of subtle background tints instead of outlined boxes.
- **Fewer screens, fewer redirects** — where two actions are done together in real life (marking a worker present *and* paying them), combine them into **one page** instead of two separate flows.

---

## Color system

### Primary = White canvas, richer purple accents

| Token | Value | Use |
|-------|--------|-----|
| `primary-bg` | `#FFFFFF` | Page background |
| `primary-bg-soft` | `#F7F5FC` | Section backgrounds, alternating rows (faint purple tint, not gray) |
| `primary-text` | `#1A1523` | Headings, body text |
| `primary-text-muted` | `#6E6580` | Subtitles, hints |
| `primary-border` | `#E9E4F5` | Card borders, dividers (purple-tinted, not plain gray) |

### Secondary = Rich purple (used generously as accent, not just buttons)

| Token | Value | Use |
|-------|--------|-----|
| `secondary-900` | `#3B0764` | Gradient header end, deep emphasis text |
| `secondary-700` | `#5B21B6` | Primary buttons, active nav, key icons |
| `secondary-500` | `#7C3AED` | Gradient header start, hover states, icon fills |
| `secondary-300` | `#A78BFA` | Secondary icon fills, chart accents |
| `secondary-soft` | `#EDE6FB` | Selected row bg, badge bg, icon chip bg |
| `secondary-muted` | `#DCD1F7` | Subtle highlighted borders |
| `secondary-text` | `#4C1D95` | Text on soft purple backgrounds |

**Gradient header bar** (new): `linear-gradient(135deg, #7C3AED 0%, #5B21B6 60%, #3B0764 100%)` — used behind the top brand bar and/or the site header banner, white text/icons on top. This is where the "richness" mainly lives — most list/content areas stay white/light for readability.

### Supporting colors

| Token | Value | Use |
|-------|--------|-----|
| `wage-earned` | `#5B21B6` (purple) | "Wage today" values |
| `paid` | `#059669` / bg `#ECFDF5` | Amount paid, settled badge |
| `pending` | `#D97706` / bg `#FFFBEB` | Pending / due amount |
| `danger` | `#DC2626` / bg `#FEF2F2` | Errors, delete |

### Rule for Replit
> White canvas + generous, confident purple: gradient header, colored icon chips, colored badges/pills. Not flat/gray. Not full-page dark purple.

---

## Typography

- Font: system UI stack.
- Page title: 18–22px bold, `primary-text`.
- Section label: 11px uppercase, letter-spacing 0.1em, `primary-text-muted`.
- Body: 14–15px.
- Money: tabular nums, bold — purple for wage, green for paid, amber for pending.

---

## Global shell

### Top bar
- **Gradient purple bar** (see above), white "LP" badge (white bg, purple glyph) + white "LabourPro" text.
- Right: small white/translucent "Sign out" text.

### Bottom navigation
- White bar, top border `primary-border`, small shadow.
- Active tab: purple icon + purple label, `secondary-soft` pill behind icon only (not full width).
- Inactive: muted gray icon + label.
- Icons only need a label under them — no extra chrome.

### Page background
- `primary-bg` / `primary-bg-soft` alternating by section — no big color blocks except the header.

---

## Icon-first component patterns

### Icon button (replaces small action cards)
- Circular or rounded-square chip, 40–44px, `secondary-soft` bg, purple icon.
- Label directly below in 11px text, or beside it inline for list rows.
- Used for: quick actions row, list-row leading icons, status indicators.

### Collapsible section (accordion)
- Header row: icon + title + chevron (rotates on expand) + optional right-aligned summary value (e.g. total).
- Collapsed by default for: worker payment history, site stats breakdown, notes fields, "advanced" filters.
- Expanded content indented slightly or on a `primary-bg-soft` panel.

### Compact list row (replaces big cards for lists)
- Single line height ~56–64px: leading icon chip → name/title (+ small muted subtitle) → trailing value/badge → optional chevron.
- Divider line (`primary-border`) between rows instead of card gaps/shadows.
- Tap row → expand inline (accordion) or navigate, per context (see Daily Wages below — expands inline).

---

## Authentication (login / register)

- White canvas.
- Top: gradient purple banner (~100px) with white "LP" badge centered, rounded bottom corners.
- Below: white form area — dark title, muted subtitle, inputs with `primary-border`, purple focus ring.
- Primary button: purple gradient (`secondary-500` → `secondary-700`), white text.
- Switch link: purple text.

---

## Dashboard

- Gradient header strip with company name + role (white text on purple).
- Below: compact icon-row stats (icon chip + number + label) instead of big stat cards.
- **Continue** row: icon (site) + "Resume last site" text + chevron — single compact row, `secondary-soft` bg.
- "Sites" entry: single icon row, not a full card.

---

## Sites list

- Header: "Sites" + purple **+ Add** icon button (icon only or icon+short label, top right, no need for full-width button).
- Site rows (compact list, not grid of big cards):
  - Leading icon chip (site glyph).
  - Name (bold) + location/dates (muted, one line, truncate).
  - Trailing: calendar-days badge in `secondary-soft`.
  - Divider between rows.
- Tap row → site overview.

---

## Inside a site

### Site header
- Gradient purple banner (compact, ~72px): white back chevron + "All sites", white site name, small white muted meta line (location · dates).

### Site overview
- **Quick actions row** (icon-first, horizontal, 3–4 icons in a row, NOT big tiles):
  1. 🗓️ **Daily Wages** (combined attendance + pay — see below)
  2. 📦 **Log usage**
  3. 💳 **Pay materials**
  - Each: icon chip (`secondary-soft` bg, purple icon) + label underneath, tap target ~64px wide.
- **Collapsible "Site stats"** accordion: total pending wages, total material cost, etc. Collapsed by default, tap to expand into small stat rows.
- **Browse** compact rows: Workers · Materials (icon + label + chevron, single line each).

---

## Crew — Daily Wages (combined attendance + pay, replaces two screens)

This is the key simplification: **no separate "Mark attendance" and "Pay crew" pages**. One page handles both per day.

### Concept
For each worker, on a selected date, the supervisor enters:
- **Wage of the day** — the amount the worker earned today. Entering any value **> 0 automatically marks the worker present** for that date. Leaving it blank/zero means absent (no wage, no attendance).
- **Amount paid** — how much was actually handed to the worker that day (can be less than, equal to, or the same as wage of the day).
- **Pending (auto-calculated, read-only)** = `wage of the day − amount paid`, shown live as the supervisor types. (Running/carried-forward balance across days is shown separately in the collapsed detail — see below.)

### Layout
- Header: "Daily Wages" + date picker (compact, tap to change date) at top, sticky.
- Small summary row under date: total wage today · total paid today · total pending today (3 compact stat chips, not big cards).
- **List of workers**, one compact row each:
  - Leading: worker initial avatar or icon chip — chip turns **purple filled** when wage > 0 (present), stays outline/gray when empty (absent).
  - Name + daily rate hint (muted, e.g. "Rate: 1700/day").
  - Two small inline inputs side-by-side on the row (or on a second line if space is tight):
    - **Wage today** input (purple accent border when focused).
    - **Paid today** input (green accent border when focused).
  - **Pending** shown as a small badge at the row's end: amber if > 0, green "Settled" if 0.
  - Tap the row (not the inputs) to **expand inline (accordion)**: shows running balance to date, last 5 payment/attendance entries, and a notes field. Collapsed by default.
- Sticky **Save all** button at the bottom (purple), saves every row that changed in one action — no page navigation required.
- Optional helper: "Fill full wage as paid" quick action (icon button) to set Paid = Wage for all selected rows at once.

### Example (from spec)
```
Javed        Rate: 1700/day
Wage today:  [ 1700 ]     Paid today: [ 1500 ]     Pending: 200
```
Tap row → expand → "Balance to date: 1,850 · Last paid: Jul 9 – 1500 · Notes: —"

### Why this matters
- One page = one mental action ("log today's wages"), not attendance then a second pay screen.
- Presence is *implied* by wage entry — no separate checkbox step.
- Pending is always visible immediately, no calculation step for the supervisor.

### Worker list (roster) — still separate, but simplified
- "Workers" screen keeps the roster (add/edit worker, rate, status) — this is admin, not daily-use, so it stays a simple compact list with a purple **+ Add worker** icon button.
- Remove the old separate "Attendance" and "Pay" quick-action tiles from this screen — both now live inside **Daily Wages**.

---

## Materials

- Keep **Log usage** and **Pay materials** as-is for now (not merged in this pass — only crew flow described above), but apply the same visual rules:
  - Compact list rows, not big cards.
  - Icon chip leading each material row (purple).
  - Pending shown as amber trailing badge.
  - Collapsible "Usage history" / "Payment history" per material (accordion, collapsed by default).
- If useful later, the same combined pattern (qty used + amount paid in one row) can be applied to materials too — flag as a future simplification, not required now.

---

## Touch & spacing

- Min tap target: 44×44px (icon buttons, row taps, inline inputs).
- Page horizontal padding: 16px.
- List rows: no card gaps/shadows — use dividers (`primary-border`), row height 56–64px.
- Reserve elevated cards (shadow + border) for: forms, the Daily Wages summary strip, expanded accordion content.
- Sticky action buttons (Save all, Pay N) pinned to bottom with safe-area padding.

---

## States

| State | Treatment |
|-------|-----------|
| Absent (no wage entered) | Row stays neutral/outline, no colored chip |
| Present (wage entered) | Icon chip fills purple, pending badge appears |
| Settled (pending = 0) | Green "Settled" badge instead of amber |
| Loading | Muted centered text, no full-screen spinner |
| Empty list | Compact icon + message + purple inline "Add" action (not a big empty-state card) |
| Error | Red text / red-tinted inline banner |
| Expanded row | Slight `primary-bg-soft` panel under the row, chevron rotated |

---

## Screen map (updated — fewer redirects)

```
Login / Register
    └── Dashboard
            └── Sites list
                    └── Site overview
                            ├── Daily Wages   (attendance + pay combined, single page)
                            ├── Log usage
                            ├── Pay materials
                            ├── Workers (roster admin) → worker detail
                            └── Materials → detail / new
```

Bottom nav: **Site · Crew · Materials · All sites** — unchanged. "Crew" now opens the roster with a prominent shortcut into **Daily Wages** rather than separate Attendance/Pay entries.

---

## Quick copy-paste tokens for Replit

```css
:root {
  /* Primary — white canvas */
  --color-primary-bg: #FFFFFF;
  --color-primary-bg-soft: #F7F5FC;
  --color-primary-text: #1A1523;
  --color-primary-text-muted: #6E6580;
  --color-primary-border: #E9E4F5;

  /* Secondary — rich purple */
  --color-secondary-900: #3B0764;
  --color-secondary-700: #5B21B6;
  --color-secondary-500: #7C3AED;
  --color-secondary-300: #A78BFA;
  --color-secondary-soft: #EDE6FB;
  --color-secondary-muted: #DCD1F7;
  --color-secondary-text: #4C1D95;

  --gradient-header: linear-gradient(135deg, #7C3AED 0%, #5B21B6 60%, #3B0764 100%);

  /* Semantic */
  --color-wage: #5B21B6;
  --color-paid: #059669;
  --color-paid-bg: #ECFDF5;
  --color-pending: #D97706;
  --color-pending-bg: #FFFBEB;
  --color-danger: #DC2626;
  --color-danger-bg: #FEF2F2;
}
```

---

## What NOT to build

- No big descriptive cards for simple quick actions — use icon chips + label.
- No separate "Mark attendance" screen and "Pay crew" screen for daily crew work — **one Daily Wages screen** does both.
- No flat all-gray UI — purple should be visibly present (header gradient, icon chips, badges).
- No always-expanded secondary info (history, notes, stats breakdown) — make it collapsible.
- No full-page dark purple backgrounds.
