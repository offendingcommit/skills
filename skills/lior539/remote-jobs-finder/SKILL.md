---
name: remote-rocketship-openclaw
version: 1.0.0
description: Plug Remote Rocketship's curated remote job feed into OpenClaw agents with first-party API access, quota reminders, and RR-style responses.
---

# Remote Rocketship × OpenClaw Skill

Use this skill whenever a user wants their OpenClaw agent to fetch Remote Rocketship jobs via the official `/api/openclaw/*` endpoints.

## Preconditions
- User must have an active Remote Rocketship subscription and be signed in (so `/api/openclaw/key` calls carry their auth cookie).
- Store their API secret as `RR_API_KEY` via `/secrets set RR_API_KEY <key>` once `openclaw.generate_key` or `openclaw.rotate_key` returns the plaintext.
- Respect quotas: 1,000 requests/day per key, max 50 jobs per call.

## Available Commands
| Command | When to use |
| --- | --- |
| `openclaw.generate_key` | No active API key yet. Performs `POST /api/openclaw/key {"action":"create"}` and shows the plaintext once. Remind the user to store it securely. |
| `openclaw.rotate_key` | User wants to replace their key (suspected leak, periodic rotation). Calls `POST /api/openclaw/key {"action":"rotate"}` and returns the new secret once. Update `RR_API_KEY`. |
| `openclaw.revoke_key` | User wants to disable API access immediately. Calls `POST /api/openclaw/key {"action":"revoke"}` and shows usage counters. |
| `openclaw.jobs` | Fetch curated jobs with a JSON filter payload. Includes `Authorization: Bearer <RR_API_KEY>` and enforces `itemsPerPage <= 50`. |

## Filter Hygiene
Before calling `/api/openclaw/jobs`, sanitize the payload:
- **Job titles:** map to canonical `jobTitleOptions` values using value/singular/plural/slug/similarTitles (case-insensitive, trims whitespace).
- **Locations:** only allow countries in `locationOptions`; normalize common aliases (USA/US → United States, UK/Great Britain/England → United Kingdom, UAE → United Arab Emirates). Drop unknown entries.
- **Enums:** seniority, employment type, visa, companySize, requiredLanguages, industries must match the dropdown options; ignore invalid values.
- **Limits:** `itemsPerPage` default 20, max 50. `page` starts at 1.

### Allowed Values
## Monitoring & Logging
- Backend emits `console.warn` events for `request_received` / `request_success` – keep them enabled for debugging.
- PostHog captures `openclaw_jobs_request` with `{ email, filters, jobsReturned, requestCountToday, techStackFilters, industriesFilters }`.
- Future alerting ideas: notify the RR team when `requestCountToday ≥ 800` for a key, and when 5-minute rolling error rate exceeds 20%.

- **jobTitleFilters** (201 values):
```json
[
  "2D Artist",
  "3D Artist",
  "AI Engineer",
  "AI Research Scientist",
  "Account Executive",
  "Account Manager",
  "Accountant",
  "Accounting Manager",
  "Accounts Payable",
  "Accounts Receivable",
  "Actuary",
  "Administration",
  "Administrative Assistant",
  "Affiliate Manager",
  "Analyst",
  "Analytics Engineer",
  "Android Engineer",
  "Application Engineer",
  "Appointment Setter",
  "Architect",
  "Art Director",
  "Artificial Intelligence",
  "Attorney",
  "Auditor",
  "Backend Engineer",
  "Bilingual",
  "Billing Specialist",
  "Blockchain Engineer",
  "Bookkeeper",
  "Brand Ambassador",
  "Brand Designer",
  "Brand Manager",
  "Business Analyst",
  "Business Development Rep",
  "Business Intelligence Analyst",
  "Business Intelligence Developer",
  "Business Operations",
  "Call Center Representative",
  "Capture Manager",
  "Chief Marketing Officer",
  "Chief Operating Officer",
  "Chief Technology Officer",
  "Chief of Staff",
  "Civil Engineer",
  "Claims Specialist",
  "Client Partner",
  "Client Services Representative",
  "Clinical Operations",
  "Clinical Research",
  "Cloud Engineer",
  "Collections",
  "Communications",
  "Community Manager",
  "Compliance",
  "Computer Vision Engineer",
  "Consultant",
  "Content Creator",
  "Content Manager",
  "Content Marketing Manager",
  "Content Writer",
  "Controller",
  "Conversion Rate Optimizer",
  "Copywriter",
  "Counselor",
  "Creative Strategist",
  "Crypto",
  "Customer Advocate",
  "Customer Retention Specialist",
  "Customer Success Manager",
  "Customer Support",
  "Data Analyst",
  "Data Engineer",
  "Data Entry",
  "Data Scientist",
  "Database Administrator",
  "DeFi",
  "Designer",
  "DevOps Engineer",
  "Developer Relations",
  "Digital Marketing",
  "Director",
  "Ecommerce",
  "Electrical Engineer",
  "Email Marketing Manager",
  "Engineer",
  "Engineering Manager",
  "Events",
  "Executive Assistant",
  "Field Engineer",
  "Financial Crime",
  "Financial Planning and Analysis",
  "Frontend Engineer",
  "Full-stack Engineer",
  "Game Engineer",
  "General Counsel",
  "Graphics Designer",
  "Growth Marketing",
  "Hardware Engineer",
  "Human Resources",
  "IT Support",
  "Implementation Specialist",
  "Incident Response Analyst",
  "Influencer Marketing",
  "Infrastructure Engineer",
  "Inside Sales",
  "Insurance",
  "Journalist",
  "LLM Engineer",
  "Lead Generation",
  "Learning and Development",
  "Legal Assistant",
  "Machine Learning Engineer",
  "Manager",
  "Marketing",
  "Marketing Analyst",
  "Marketing Operations",
  "Mechanical Engineer",
  "Medical Billing and Coding",
  "Medical Director",
  "Medical Reviewer",
  "Medical writer",
  "NLP Engineer",
  "Network Engineer",
  "Network Operations",
  "Notary",
  "Onboarding Specialist",
  "Operations",
  "Outside Sales",
  "Paralegal",
  "Payroll",
  "People Operations",
  "Performance Marketing",
  "Platform Engineer",
  "Pre-sales Engineer",
  "Pricing Analyst",
  "Procurement",
  "Producer",
  "Product Adoption Specialist",
  "Product Analyst",
  "Product Designer",
  "Product Manager",
  "Product Marketing",
  "Product Operations",
  "Product Specialist",
  "Production Engineer",
  "Program Manager",
  "Project Manager",
  "Proposal Manager",
  "Public Relations",
  "QA Automation Engineer",
  "QA Engineer",
  "Recruitment",
  "Research Analyst",
  "Research Engineer",
  "Research Scientist",
  "Revenue Operations",
  "Risk",
  "Robotics",
  "SAP",
  "SDET",
  "SEO Marketing",
  "Sales",
  "Sales Development Rep",
  "Sales Engineer",
  "Sales Operations Manager",
  "Salesforce Administrator",
  "Salesforce Analyst",
  "Salesforce Consultant",
  "Salesforce Developer",
  "Scrum Master",
  "Security Analyst",
  "Security Engineer",
  "Security Operations",
  "ServiceNow",
  "Smart Contract Engineer",
  "Social Media Manager",
  "Software Engineer",
  "Solutions Engineer",
  "Strategy",
  "Supply Chain",
  "Support Engineer",
  "System Administrator",
  "Systems Engineer",
  "Tax",
  "Technical Account Manager",
  "Technical Customer Success",
  "Technical Product Manager",
  "Technical Program Manager",
  "Technical Project Manager",
  "Technical Recruiter",
  "Technical Writer",
  "Therapist",
  "Threat Intelligence Specialist",
  "Translator",
  "Underwriter",
  "User Researcher",
  "Vice President",
  "Video Editor",
  "Web Designer",
  "Web3",
  "iOS Engineer"
]
```
- **locationFilters** (182 values):
```json
[
  "Africa",
  "Alabama",
  "Alaska",
  "Albania",
  "Algeria",
  "American Samoa",
  "Argentina",
  "Arizona",
  "Arkansas",
  "Armenia",
  "Aruba",
  "Asia",
  "Australia",
  "Austria",
  "Azerbaijan",
  "Bahamas",
  "Bahrain",
  "Bangladesh",
  "Barbados",
  "Belarus",
  "Belgium",
  "Bermuda",
  "Bosnia and Herzegovina",
  "Brazil",
  "Bulgaria",
  "California",
  "Canada",
  "Cape Verde",
  "Chile",
  "Colombia",
  "Colorado",
  "Connecticut",
  "Costa Rica",
  "Croatia",
  "Curaçao",
  "Cyprus",
  "Czech",
  "Delaware",
  "Denmark",
  "Dominica",
  "Dominican Republic",
  "Ecuador",
  "Egypt",
  "El Salvador",
  "Estonia",
  "Ethiopia",
  "Europe",
  "Finland",
  "Florida",
  "France",
  "Georgia",
  "Germany",
  "Ghana",
  "Gibraltar",
  "Greece",
  "Greenland",
  "Guam",
  "Guatemala",
  "Guernsey",
  "Hawaii",
  "Honduras",
  "Hong Kong",
  "Hungary",
  "Iceland",
  "Idaho",
  "Illinois",
  "India",
  "Indiana",
  "Indonesia",
  "Iowa",
  "Ireland",
  "Isle of Man",
  "Israel",
  "Italy",
  "Jamaica",
  "Japan",
  "Jersey",
  "Jordan",
  "Kansas",
  "Kazakhstan",
  "Kentucky",
  "Kenya",
  "Latin America",
  "Latvia",
  "Lebanon",
  "Lesotho",
  "Libya",
  "Liechtenstein",
  "Lithuania",
  "Louisiana",
  "Luxembourg",
  "Macedonia",
  "Madagascar",
  "Maine",
  "Malaysia",
  "Maldives",
  "Malta",
  "Maryland",
  "Massachusetts",
  "Mauritius",
  "Mexico",
  "Michigan",
  "Middle East",
  "Minnesota",
  "Mississippi",
  "Missouri",
  "Moldova",
  "Monaco",
  "Montana",
  "Montenegro",
  "Morocco",
  "Namibia",
  "Nebraska",
  "Netherlands",
  "Nevada",
  "New Hampshire",
  "New Jersey",
  "New Mexico",
  "New York",
  "New Zealand",
  "Nicaragua",
  "Nigeria",
  "North America",
  "North Carolina",
  "North Dakota",
  "Norway",
  "Oceania",
  "Ohio",
  "Oklahoma",
  "Oman",
  "Oregon",
  "Pakistan",
  "Palau",
  "Palestinian Territory",
  "Panama",
  "Paraguay",
  "Pennsylvania",
  "Peru",
  "Philippines",
  "Poland",
  "Portugal",
  "Puerto Rico",
  "Qatar",
  "Rhode Island",
  "Romania",
  "Russia",
  "Saudi Arabia",
  "Serbia",
  "Seychelles",
  "Singapore",
  "Slovakia",
  "Slovenia",
  "South Africa",
  "South Carolina",
  "South Dakota",
  "South Georgia",
  "South Korea",
  "Spain",
  "Sri Lanka",
  "Suriname",
  "Swaziland",
  "Sweden",
  "Switzerland",
  "Taiwan",
  "Tennessee",
  "Texas",
  "Thailand",
  "Trinidad and Tobago",
  "Turkey",
  "Ukraine",
  "United Arab Emirates",
  "United Kingdom",
  "United States",
  "Uruguay",
  "Utah",
  "Vermont",
  "Virginia",
  "Washington",
  "West Virginia",
  "Wisconsin",
  "Worldwide",
  "Wyoming"
]
```
- **seniorityFilters** (5 values):
```json
[
  "entry-level",
  "expert",
  "junior",
  "mid",
  "senior"
]
```
- **employmentTypeFilters** (4 values):
```json
[
  "contract",
  "full-time",
  "internship",
  "part-time"
]
```
- **visaFilter** (2 values):
```json
[
  "h1b",
  "uk-skilled-worker"
]
```
- **companySizeFilters** (8 values):
```json
[
  "1,10",
  "10001,",
  "1001,5000",
  "11,50",
  "201,500",
  "5001,10000",
  "501,1000",
  "51,200"
]
```
- **requiredLanguagesFilters** (29 values):
```json
[
  "ar",
  "cs",
  "da",
  "de",
  "en",
  "es",
  "fi",
  "fr",
  "he",
  "hi",
  "hu",
  "id",
  "is",
  "it",
  "ja",
  "ko",
  "nl",
  "no",
  "pl",
  "pt",
  "ro",
  "ru",
  "sk",
  "sv",
  "th",
  "tr",
  "uk",
  "vi",
  "zh"
]
```
- **industriesFilters** (44 values):
```json
[
  "API",
  "AR/VR",
  "Aerospace",
  "Agriculture",
  "Artificial Intelligence",
  "B2B",
  "B2C",
  "Banking",
  "Beauty",
  "Biotechnology",
  "Charity",
  "Compliance",
  "Crypto",
  "Cybersecurity",
  "Education",
  "Energy",
  "Enterprise",
  "Fashion",
  "Finance",
  "Fintech",
  "Gambling",
  "Gaming",
  "Government",
  "HR Tech",
  "Hardware",
  "Healthcare Insurance",
  "Marketplace",
  "Media",
  "Non-profit",
  "Pharmaceuticals",
  "Productivity",
  "Real Estate",
  "Recruitment",
  "Retail",
  "SaaS",
  "Science",
  "Security",
  "Social Impact",
  "Sports",
  "Telecommunications",
  "Transport",
  "Web 3",
  "Wellness",
  "eCommerce"
]
```

_Note: `excludeRequiredLanguagesFilters` uses the same codes as `requiredLanguagesFilters`._

## Response Template
```
**{job.title}** at {job.company.name}
🗓 {timeAgo} · 📍 {location/flag emojis} · 💰 {salaryLabel}{optional chips: ✈️ visa, 🎯 seniority}
{summary line 1}
{summary line 2}
```
- Use RR tone: concise, friendly, light emoji flair.
- If salary missing, say “Salary undisclosed”.
- Append quota reminders when `requestCountToday ≥ 800`.

## Rate Limits & Error Handling
| Status | Meaning | Agent Guidance |
| --- | --- | --- |
| 401 | Missing/invalid API key (includes revoked or never created) | Ask user to generate or paste a valid key via the account instructions, then update `RR_API_KEY`. |
| 403 | Subscription inactive | Prompt user to renew their Remote Rocketship plan (`/sign-up`) before retrying. |
| 429 | Daily request limit exceeded | Inform user the quota resets daily (1,000 calls). Suggest waiting or rotating the key if abuse is suspected. |
| 5xx | Backend issue | Apologize, retry with exponential backoff, and escalate if the issue persists. |

## Workflow Cheat Sheet
1. **Provision key** (if needed):
   - `/openclaw.generate_key`
   - `/secrets set RR_API_KEY <plaintext>`
2. **Fetch jobs:**
   - `/openclaw.jobs { "filters": { ... } }`
   - Render cards via the template above.
3. **Rotate / revoke** when requested.

## Sample Agent Copy
> “🪐 Pulled 20 fresh roles. Reminder: your RR API plan allows 1,000 calls/day and you’ve used 610 so far.”