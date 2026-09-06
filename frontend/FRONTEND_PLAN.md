# AI Career Intelligence Platform — Frontend Design Plan

## 1. Current State Summary

### What Exists (reuse, don't rebuild)
- **Framework**: React 19 + Vite 8 + Tailwind CSS 3.4
- **Routing**: react-router-dom v7 (flat routes, no nesting)
- **State**: Local useState only (no Redux/Context)
- **API**: Centralized fetch-based client (`services/api.js`)
- **Auth**: JWT in localStorage, PrivateRoute guard
- **Design System**: Custom CSS variables + Tailwind + DM Serif Display / DM Sans fonts + lucide-react icons + framer-motion
- **Existing Pages**: Landing, Login, Register, Dashboard (7 tabs), ResumeCreateFlow, ResumeEditorWrapper, Pricing, About, Contact
- **Existing Components**: Navbar, Hero, 24 resume templates, ResumeEditor (945 lines), ResumePreview (24 templates), ATSReview, ExportDownload, AIGenerator, PromptEntry, TemplateSelection
- **Backend API**: Auth, Resumes CRUD, Cover Letters CRUD, Templates, ATS Scoring, AI Improve, PDF Export, Career Intelligence (bullets, summary, cover-letter, bullet-feedback, ats-optimize)

### What's Missing (the gap)
- Guest/unauthenticated resume flow
- AI Chat experience
- Google Sign-In
- Unified navigation (landing vs dashboard)
- Error boundaries
- Loading skeletons
- Empty states
- Mobile responsive patterns

---

## 2. Complete Page Hierarchy

```
Public (unauthenticated)
├── Landing Page (/)
├── Login (/login)
├── Register (/register)
├── Pricing (/pricing)
├── About (/about)
└── Contact (/contact)

Guest Flow (unauthenticated, progressive)
├── Guest Chat (/guest/chat)
├── Guest Basic Info (/guest/info)
├── Guest AI Interview (/guest/interview)
├── Guest Resume Generation (/guest/generating)
├── Guest Template Select (/guest/templates)
├── Guest Editor (/guest/editor)
└── Guest Download (/guest/download)

Authenticated Dashboard
├── Dashboard Home (/dashboard)
├── My Resumes (/dashboard/resumes)
├── Cover Letters (/dashboard/cover-letters)
├── AI Chat (/dashboard/chat)
├── Templates (/dashboard/templates)
├── Profile (/dashboard/profile)
└── Settings (/dashboard/settings)

Resume Workflow (authenticated)
├── Create Resume (/resume/create)
├── Edit Resume (/resume/edit/:id)
└── Resume Preview (/resume/preview/:id)
```

---

## 3. Route Structure

| Route | Component | Auth | Layout | Description |
|-------|-----------|------|--------|-------------|
| `/` | LandingPage | No | Public | Marketing landing |
| `/login` | Login | No | Auth | Email/password login |
| `/register` | Register | No | Auth | Registration |
| `/pricing` | PricingPage | No | Public | Pricing plans |
| `/about` | About | No | Public | About page |
| `/contact` | Contact | No | Public | Contact form |
| `/guest/chat` | GuestChat | No | Guest | AI conversation to collect info |
| `/guest/info` | GuestBasicInfo | No | Guest | Basic information form |
| `/guest/interview` | GuestInterview | No | Guest | AI interview questions |
| `/guest/generating` | GuestGenerating | No | Guest | AI generation loading |
| `/guest/templates` | GuestTemplateSelect | No | Guest | Template selection |
| `/guest/editor` | GuestEditor | No | Guest | Editor with preview |
| `/guest/download` | GuestDownload | No | Guest | Download/sign-up gate |
| `/dashboard` | Dashboard | Yes | App | Dashboard home |
| `/dashboard/resumes` | Dashboard (resumes tab) | Yes | App | My resumes list |
| `/dashboard/cover-letters` | Dashboard (cover letters tab) | Yes | App | Cover letters list |
| `/dashboard/chat` | AIChat | Yes | App | AI career advisor chat |
| `/dashboard/templates` | TemplatesHub | Yes | App | Template browser |
| `/dashboard/profile` | Profile | Yes | App | User profile |
| `/dashboard/settings` | Settings | Yes | App | Account settings |
| `/resume/create` | ResumeCreateFlow | Yes | App | AI prompt entry flow |
| `/resume/edit/:id` | ResumeEditorWrapper | Yes | App | Resume editor |
| `*` | Navigate to `/` | No | — | Catch-all |

---

## 4. Component Hierarchy

### Layout Components
```
App
├── PublicLayout          (Navbar + content + Footer)
│   ├── Navbar            (logo, nav links, auth CTA)
│   ├── Footer            (links, copyright)
│   └── {children}
├── AuthLayout            (centered card for login/register)
│   └── {children}
├── GuestLayout           (stepper + content)
│   ├── GuestStepper      (progress indicator)
│   └── {children}
└── AppLayout             (sidebar + content)
    ├── Sidebar           (navigation + user menu)
    ├── TopBar            (search, notifications, profile)
    └── {children}
```

### Shared Components
```
components/shared/
├── Button.jsx            (variants: primary, secondary, ghost, danger)
├── Card.jsx              (configurable card container)
├── Modal.jsx             (reusable modal overlay)
├── Input.jsx             (text input with label, error, helper)
├── Select.jsx            (dropdown select)
├── TextArea.jsx          (multi-line input)
├── Badge.jsx             (status badges)
├── Avatar.jsx            (user avatar)
├── Spinner.jsx           (loading spinner)
├── Skeleton.jsx          (loading skeleton)
├── EmptyState.jsx        (empty state illustration + message)
├── ErrorBoundary.jsx     (React error boundary)
├── Toast.jsx             (notification toasts)
├── ProgressBar.jsx       (step/progress indicator)
├── ScoreGauge.jsx        (circular score display)
└── Stepper.jsx           (multi-step progress)
```

### Landing Page Components
```
components/landing/
├── Navbar.jsx            (existing, enhanced)
├── Hero.jsx              (existing, enhanced)
├── Features.jsx          (NEW - 6 feature cards)
├── Templates.jsx         (existing)
├── Workflow.jsx          (existing)
├── Testimonials.jsx      (existing)
├── Pricing.jsx           (existing)
├── FAQ.jsx               (existing)
├── FinalCTA.jsx          (existing)
└── Footer.jsx            (existing)
```

### Dashboard Components
```
components/dashboard/
├── Sidebar.jsx           (navigation + user menu)
├── TopBar.jsx            (search + notifications)
├── StatsCards.jsx        (summary statistics)
├── ResumeGrid.jsx        (resume cards grid)
├── CoverLetterGrid.jsx   (cover letter cards)
├── ActivityFeed.jsx      (recent activity list)
└── QuickActions.jsx      (quick action buttons)
```

### Resume Flow Components
```
components/resume/
├── ResumeFlowHeader.jsx  (existing - stepper)
├── PromptEntry.jsx       (existing - AI prompt)
├── AIGenerator.jsx       (existing - loading)
├── TemplateSelection.jsx (existing - template gallery)
├── ResumeEditor.jsx      (existing - editor)
├── ResumePreview.jsx     (existing - 24 templates)
├── ATSReview.jsx         (existing - ATS scoring)
└── ExportDownload.jsx    (existing - download)
```

### AI Chat Components
```
components/chat/
├── ChatWindow.jsx        (main chat container)
├── ChatMessage.jsx       (individual message bubble)
├── ChatInput.jsx         (text input + send button)
├── ChatSuggestions.jsx   (quick reply suggestions)
└── ChatTyping.jsx        (typing indicator)
```

### Guest Flow Components
```
components/guest/
├── GuestStepper.jsx      (progress stepper)
├── GuestChat.jsx         (AI conversation)
├── GuestBasicInfo.jsx    (basic info form)
├── GuestInterview.jsx    (AI interview)
├── GuestGenerating.jsx   (generation loading)
├── GuestTemplateSelect.jsx (template picker)
├── GuestEditor.jsx       (editor + preview)
└── GuestDownload.jsx     (download + sign-up gate)
```

---

## 5. State Management Plan

### Approach: Lightweight React Context + Local State

**No Redux/Zustand** — keep it simple with:

1. **AuthContext** — Global auth state
   ```jsx
   { user, token, isAuthenticated, login(), logout(), register() }
   ```
   - Wraps entire app
   - Reads JWT from localStorage on mount
   - Provides user profile data
   - Handles token refresh (future)

2. **ToastContext** — Global notification system
   ```jsx
   { toasts, addToast(), removeToast() }
   ```
   - Success/error/info notifications
   - Auto-dismiss after timeout

3. **Local state** for everything else
   - Dashboard tab state: `useState` in Dashboard component
   - Resume editor state: `useState` in ResumeEditorWrapper
   - Chat messages: `useState` in ChatWindow
   - Guest flow state: `useState` in GuestFlow wrapper
   - Form state: `useState` in each form component

### State Flow
```
AuthContext (global)
├── user: { id, email, fullName, avatar }
├── token: string
├── isAuthenticated: boolean
├── login(email, password) -> redirect
├── register(email, password, name) -> redirect
└── logout() -> redirect

ToastContext (global)
├── toasts: [{ id, type, message, duration }]
├── addToast(type, message, duration)
└── removeToast(id)

Page-level state (local)
├── Dashboard: activeTab, resumes[], coverLetters[]
├── ResumeEditor: resumeData, activeSection, selectedTemplate
├── Chat: messages[], inputValue, isTyping
└── Guest: step, formData, generatedResume
```

---

## 6. API Integration Map

### Existing Endpoints (already in api.js)
| Endpoint | Method | Used By |
|----------|--------|---------|
| `/api/auth/register` | POST | Register page |
| `/api/auth/login` | POST | Login page |
| `/api/auth/me` | GET | AuthContext |
| `/api/user/profile` | GET/PUT | Profile page |
| `/api/user/subscription` | GET | Settings page |
| `/api/resume/create` | POST | ResumeCreateFlow |
| `/api/resume/list` | GET | Dashboard |
| `/api/resume/:id` | GET/PUT/DELETE | ResumeEditor, Dashboard |
| `/api/resume/:id/sections` | PUT | ResumeEditor |
| `/api/resume/generate` | POST | ResumeCreateFlow |
| `/api/cover-letter/generate` | POST | CoverLetterModal |
| `/api/cover-letter/list` | GET | Dashboard |
| `/api/cover-letter/:id` | GET/PUT/DELETE | Dashboard |
| `/api/templates` | GET | TemplateSelection, Dashboard |
| `/api/ats/analyze/:id` | POST | ATSReview |
| `/api/ats/improve-text` | POST | ResumeEditor AI rewrite |
| `/api/pdf/export` | POST | ExportDownload |

### New Endpoints to Add (backend)
| Endpoint | Method | Used By |
|----------|--------|---------|
| `/api/v1/career/bullets` | POST | Guest flow, ResumeEditor |
| `/api/v1/career/summary` | POST | Guest flow, ResumeEditor |
| `/api/v1/career/cover-letter` | POST | CoverLetter generation |
| `/api/v1/career/bullet-feedback` | POST | ResumeEditor bullet rewrite |
| `/api/v1/career/ats-optimize` | POST | ATSReview optimization |
| `/api/v1/career/health` | GET | Health check |

### API Service Updates
Add to `services/api.js`:
```javascript
// Career Intelligence
async generateBullets(data) { ... }
async generateSummary(data) { ... }
async generateCareerCoverLetter(data) { ... }
async getBulletFeedback(data) { ... }
async optimizeForATS(data) { ... }

// Career Health
async careerHealth() { ... }
```

---

## 7. Authentication Flow

### Current Flow (keep as-is)
1. User clicks "Get Started" → `/register`
2. User fills form → `api.register()` → `api.login()` → store token → `/dashboard`
3. User clicks "Sign In" → `/login`
4. User fills form → `api.login()` → store token → `/dashboard`
5. PrivateRoute checks `api.isAuthenticated()` (localStorage token)

### New Flows to Add

#### Google Sign-In Flow
1. User clicks "Continue with Google" on Login/Register
2. Google OAuth popup opens
3. On success: receive Google ID token
4. POST to `/api/auth/google` with ID token
5. Backend verifies, creates/links user, returns JWT
6. Store JWT, redirect to `/dashboard`

#### Guest Flow
1. User clicks "Build My Resume" (not authenticated)
2. Navigate to `/guest/chat`
3. AI Chat collects information conversationally
4. AI Interview asks follow-up questions
5. Generation screen shows progress
6. Template selection
7. Editor with preview
8. Download page → gate: "Sign up to download" → `/register`
9. After registration, resume is saved and download starts

---

## 8. Dashboard Structure

### Sidebar Navigation
```
Dashboard
├── 🏠 Home          (/dashboard)
├── 📄 My Resumes    (/dashboard/resumes)
├── ✉️ Cover Letters (/dashboard/cover-letters)
├── 💬 AI Chat       (/dashboard/chat)
├── 🎨 Templates     (/dashboard/templates)
├── ─────────────
├── 👤 Profile       (/dashboard/profile)
├── ⚙️ Settings      (/dashboard/settings)
└── 🚪 Logout
```

### Home Tab
- Welcome message with user name
- 4 stat cards: Total Resumes, Cover Letters, ATS Score Avg, Plan Type
- Recent resumes (last 5) with quick actions
- Recent activity feed
- Quick actions: New Resume, New Cover Letter

### My Resumes Tab
- Grid of resume cards with:
  - Template thumbnail
  - Resume title
  - Last updated date
  - ATS score badge
  - Actions: Edit, Download, Delete
- Empty state: "No resumes yet" with CTA

### Cover Letters Tab
- Grid of cover letter cards with:
  - Company name
  - Job role
  - Created date
  - Actions: Edit, Download, Delete
- Empty state: "No cover letters yet" with CTA

### AI Chat Tab
- Full-width chat interface
- Message history
- Quick suggestion chips
- Typing indicator
- Context-aware responses

### Templates Tab
- Category filter tabs (All, ATS, Corporate, Technology, Creative)
- Template grid with preview
- "Use Template" button
- Preview modal

### Profile Tab
- Edit profile form
- Job title, phone, location, website, LinkedIn, summary
- Avatar upload (future)

### Settings Tab
- Account settings (email, password)
- Subscription plan display
- Billing history
- Danger zone (delete account)

---

## 9. User Journey — Detailed Flow

### Primary Journey: Guest → Resume → Signup

```
1. LANDING PAGE
   ├── Hero: "Build Your Resume with AI"
   ├── CTA: "Build My Resume" → /guest/chat
   └── Features, Templates, Workflow, Testimonials, Pricing

2. GUEST AI CHAT (/guest/chat)
   ├── AI greeting: "Hi! I'll help you build a great resume."
   ├── AI asks: "What role are you targeting?"
   ├── User types: "Senior Software Engineer"
   ├── AI asks: "What companies have you worked at?"
   ├── User types response
   ├── AI asks about technologies, achievements
   ├── User responds
   └── AI: "Great! Let me generate your resume." → /guest/generating

3. GUEST BASIC INFO (/guest/info)
   ├── Form: Full name, email, phone, location
   ├── Optional: LinkedIn, website
   └── Continue → /guest/interview

4. GUEST AI INTERVIEW (/guest/interview)
   ├── AI asks follow-up questions based on chat
   ├── 3-5 targeted questions
   ├── User answers each
   └── AI: "Perfect! Generating your resume..." → /guest/generating

5. GUEST GENERATION (/guest/generating)
   ├── Animated loading screen
   ├── Steps: Knowledge → AI → Rules → Quality
   ├── Progress bar with status messages
   └── Complete → /guest/templates

6. GUEST TEMPLATE SELECT (/guest/templates)
   ├── Template grid
   ├── Live preview with generated data
   ├── User selects template
   └── Continue → /guest/editor

7. GUEST EDITOR (/guest/editor)
   ├── Left: Tabbed editor (Personal, Summary, Experience, etc.)
   ├── Right: Live resume preview
   ├── AI rewrite buttons per section
   ├── ATS score panel
   └── "Download" button → /guest/download

8. GUEST DOWNLOAD (/guest/download)
   ├── Resume preview
   ├── Download options (PDF, DOCX, TXT)
   ├── GATE: "Sign up to download your resume"
   ├── Sign-up form (pre-filled with guest info)
   ├── After signup: resume saved, download starts
   └── Redirect to /dashboard
```

### Authenticated Journey: Dashboard → Resume

```
1. DASHBOARD (/dashboard)
   ├── View existing resumes
   ├── Click "New Resume" → /resume/create
   └── Or click existing resume → /resume/edit/:id

2. RESUME CREATE (/resume/create)
   ├── PromptEntry: Describe your experience
   ├── AIGenerator: Loading animation
   └── Redirect to /resume/edit/:id

3. RESUME EDIT (/resume/edit/:id)
   ├── Tabbed editor + live preview
   ├── AI rewrite capabilities
   ├── ATS scoring
   ├── Template switching
   └── Save + Download
```

---

## 10. Error, Loading, Empty States

### Error States
| State | Component | Behavior |
|-------|-----------|----------|
| API Error | Toast | Red toast notification, auto-dismiss |
| 401 Unauthorized | AuthContext | Clear token, redirect to /login |
| 404 Not Found | ErrorPage | "Page not found" with back button |
| 500 Server Error | ErrorPage | "Something went wrong" with retry |
| Network Error | Toast | "Connection lost" toast |
| Validation Error | Inline | Red border + message below input |
| Component Crash | ErrorBoundary | "Something broke" with reset button |

### Loading States
| State | Component | Behavior |
|-------|-----------|----------|
| Page Load | Skeleton | Skeleton layout matching page structure |
| API Call | Spinner | Centered spinner or inline spinner |
| AI Generation | AIGenerator | Animated progress with steps |
| Resume Save | Button | Button shows spinner, disabled |
| PDF Export | Button | Button shows "Exporting..." |
| Template Load | Skeleton | Grid of skeleton cards |

### Empty States
| State | Component | Behavior |
|-------|-----------|----------|
| No Resumes | EmptyState | Illustration + "Create your first resume" CTA |
| No Cover Letters | EmptyState | Illustration + "Write a cover letter" CTA |
| No Chat History | EmptyState | "Start a conversation with AI" |
| No Search Results | EmptyState | "No results found" |
| No Templates | EmptyState | "No templates available" |

---

## 11. Mobile Responsiveness

### Breakpoints (matching existing Tailwind)
- `sm`: 640px (large phones)
- `md`: 768px (tablets)
- `lg`: 1024px (small laptops)
- `xl`: 1280px (desktops)

### Mobile Patterns
| Component | Desktop | Mobile |
|-----------|---------|--------|
| Navbar | Full nav links | Hamburger menu |
| Dashboard | Sidebar + content | Bottom tab bar + content |
| Resume Editor | Side-by-side | Tab toggle (editor/preview) |
| Chat | Side panel | Full screen |
| Template Grid | 3-4 columns | 1-2 columns |
| Landing Page | Full sections | Stacked sections |
| Forms | Side-by-side fields | Stacked fields |
| Modals | Centered overlay | Full-screen sheet |

### Mobile-Specific Components
- **BottomTabBar**: Fixed bottom navigation for dashboard on mobile
- **MobileMenu**: Slide-out hamburger menu
- **FullScreenModal**: Modals that take full screen on mobile
- **SwipeableCards**: Swipe between resume templates on mobile

---

## 12. Frontend Implementation Order

### Phase 1: Foundation (Week 1)
1. **Shared Components** — Button, Card, Input, Modal, Toast, Skeleton, EmptyState, ErrorBoundary
2. **AuthContext** — Global auth state management
3. **ToastContext** — Global notification system
4. **Layout Components** — PublicLayout, AuthLayout, AppLayout with Sidebar

### Phase 2: Authentication (Week 1)
5. **Login Page** — Refactor existing with new design system
6. **Register Page** — Refactor existing with new design system
7. **Google Sign-In** — OAuth integration (backend endpoint needed)

### Phase 3: Landing Page (Week 2)
8. **Landing Page Refactor** — Consistent design system, mobile responsive
9. **Features Section** — NEW section showcasing AI capabilities
10. **Navigation** — Unified navbar with auth state

### Phase 4: Dashboard (Week 2)
11. **Dashboard Layout** — Sidebar + content area
12. **Home Tab** — Stats cards, recent resumes, activity
13. **My Resumes Tab** — Grid with CRUD actions
14. **Cover Letters Tab** — Grid with CRUD actions
15. **Profile Tab** — Edit profile form
16. **Settings Tab** — Account settings

### Phase 5: Resume Workflow (Week 3)
17. **ResumeCreateFlow** — Prompt entry with AI generation
18. **ResumeEditorWrapper** — Editor orchestration
19. **ResumeEditor** — Enhanced with AI rewrite, scoring
20. **TemplateSelection** — Live preview integration
21. **ATSReview** — Scoring and recommendations
22. **ExportDownload** — PDF/DOCX/TXT export

### Phase 6: AI Chat (Week 3)
23. **ChatWindow** — Full chat interface
24. **ChatMessage** — Message bubbles with AI/user styling
25. **ChatInput** — Text input with send
26. **ChatSuggestions** — Quick reply chips
27. **Integration** — Connect to career API endpoints

### Phase 7: Guest Flow (Week 4)
28. **GuestStepper** — Progress indicator
29. **GuestChat** — AI conversation flow
30. **GuestBasicInfo** — Info collection form
31. **GuestInterview** — AI follow-up questions
32. **GuestGenerating** — Loading animation
33. **GuestTemplateSelect** — Template picker
34. **GuestEditor** — Simplified editor
35. **GuestDownload** — Download + signup gate

### Phase 8: Polish (Week 4)
36. **Mobile Responsive** — All pages responsive
37. **Error Boundaries** — Component error handling
38. **Loading Skeletons** — All pages skeleton loading
39. **Empty States** — All empty states
40. **Toast Notifications** — Success/error feedback

---

## 13. Design Tokens (CSS Variables)

```css
:root {
  /* Primary - Teal */
  --color-primary: #7BC4BE;
  --color-primary-light: #A8D8D3;
  --color-primary-dark: #4A9E98;
  --color-primary-deep: #2D7A74;

  /* Accent - Amber */
  --color-accent: #F6B233;
  --color-accent-light: #FAD07A;
  --color-accent-dark: #D4920F;

  /* Neutrals */
  --color-text: #1A2B2A;
  --color-text-mid: #3D5552;
  --color-text-muted: #6B8A87;
  --color-bg-ivory: #F4F1EA;
  --color-bg-cream: #FFFDF8;
  --color-border: rgba(123, 196, 190, 0.25);
  --color-border-strong: rgba(123, 196, 190, 0.45);

  /* Semantic */
  --color-success: #22C55E;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* Typography */
  --font-serif: 'DM Serif Display', serif;
  --font-sans: 'DM Sans', sans-serif;

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;

  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
}
```

---

## 14. Key Design Decisions

1. **No new dependencies** — Use existing Tailwind + CSS variables + lucide-react + framer-motion
2. **Consistent design system** — Unify landing page (global CSS) and dashboard (Tailwind) via shared CSS variables
3. **Component-driven** — Build shared components first, compose into pages
4. **Progressive enhancement** — Guest flow works without auth, upgrades gracefully
5. **Mobile-first** — Design for mobile, enhance for desktop
6. **Existing components preserved** — ResumeEditor, ResumePreview, ATSReview, ExportDownload kept as-is
7. **Backend untouched** — All API calls go through existing api.js, no backend changes
