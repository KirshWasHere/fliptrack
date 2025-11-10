# Application Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                         (Textual TUI)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │ DashboardScreen  │         │ ItemFormScreen   │            │
│  │                  │         │                  │            │
│  │ - Stats Panel    │◄────────┤ - Input Fields   │            │
│  │ - Items Table    │         │ - Radio Buttons  │            │
│  │ - Action Buttons │         │ - Profit Display │            │
│  └────────┬─────────┘         └────────┬─────────┘            │
│           │                            │                       │
└───────────┼────────────────────────────┼───────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LOGIC                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  database.py │  │  scraper.py  │  │report_gen.py │         │
│  │              │  │              │  │              │         │
│  │ - CRUD Ops   │  │ - Web Scrape │  │ - HTML Gen   │         │
│  │ - Queries    │  │ - Download   │  │ - QR Codes   │         │
│  │ - Stats      │  │ - Cache URLs │  │ - Templates  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                 │
│  ┌──────┴─────────────────┴──────────────────┴───────┐         │
│  │              utils.py & config.py                 │         │
│  │  - Helper Functions  - Settings  - Validation    │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
            │                 │                  │
            ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ tracker.db   │  │data/images/  │  │  reports/    │         │
│  │  (SQLite)    │  │              │  │              │         │
│  │              │  │ item_1/      │  │ index.html   │         │
│  │ - items      │  │ item_2/      │  │ item_1.html  │         │
│  │   table      │  │ item_3/      │  │ item_2.html  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### 1. Adding a New Item

```
User Input (ItemFormScreen)
    │
    ├─► Enter item details
    │   (name, prices, URL, category)
    │
    ├─► Click "Scrape Images"
    │   │
    │   └─► scraper.py
    │       │
    │       ├─► Determine category
    │       ├─► Fetch from appropriate site
    │       ├─► Parse HTML with BeautifulSoup
    │       └─► Return image URLs
    │
    ├─► Display scraped URLs
    │
    ├─► Click "Save Item"
    │   │
    │   └─► database.py
    │       │
    │       ├─► Validate data
    │       ├─► Download first 3 images
    │       ├─► Save to data/images/item_[ID]/
    │       ├─► Insert into database
    │       └─► Return item ID
    │
    └─► Return to Dashboard
        │
        └─► Refresh table display
```

### 2. Generating a Report

```
User Action (Dashboard)
    │
    ├─► Select item from table
    │
    ├─► Press 'r' key
    │   │
    │   └─► report_generator.py
    │       │
    │       ├─► Fetch item from database
    │       │
    │       ├─► Load images from disk
    │       │   └─► Convert to Base64
    │       │
    │       ├─► Generate QR code
    │       │   └─► Encode product URL
    │       │
    │       ├─► Calculate profits
    │       │
    │       ├─► Render Jinja2 template
    │       │   ├─► Inject item data
    │       │   ├─► Embed images
    │       │   └─► Add QR code
    │       │
    │       └─► Save HTML to reports/
    │
    ├─► Update database with report path
    │
    └─► Show success notification
```

### 3. Master Index Generation

```
User Action (Dashboard)
    │
    ├─► Press 'm' key
    │   │
    │   └─► report_generator.py
    │       │
    │       ├─► Fetch all items from database
    │       │
    │       ├─► Calculate profits for each
    │       │
    │       ├─► Render index template
    │       │   ├─► Create table rows
    │       │   ├─► Link to individual reports
    │       │   └─► Add summary stats
    │       │
    │       └─► Save to reports/index.html
    │
    └─► Show success notification
```

## Data Flow Diagram

```
┌──────────┐
│   User   │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│   Textual UI    │
│  (main.py)      │
└────┬────────────┘
     │
     ├─────────────────────┐
     │                     │
     ▼                     ▼
┌──────────┐         ┌──────────┐
│ Database │◄────────┤ Scraper  │
│ (SQLite) │         │ (httpx)  │
└────┬─────┘         └──────────┘
     │                     │
     │                     ▼
     │              ┌──────────────┐
     │              │ Image Files  │
     │              │ (data/images)│
     │              └──────┬───────┘
     │                     │
     ▼                     ▼
┌──────────────────────────────┐
│    Report Generator          │
│    (Jinja2 + QR Code)        │
└──────────────┬───────────────┘
               │
               ▼
        ┌──────────────┐
        │ HTML Reports │
        │ (reports/)   │
        └──────────────┘
```

## Module Dependencies

```
main.py
├── database.py
│   └── sqlite3 (stdlib)
├── scraper.py
│   ├── httpx
│   └── beautifulsoup4
├── report_generator.py
│   ├── jinja2
│   ├── qrcode
│   └── PIL (Pillow)
├── utils.py
│   ├── PIL (Pillow)
│   └── subprocess (stdlib)
└── config.py
    └── pathlib (stdlib)

External Dependencies:
├── textual (TUI framework)
├── rich (styling)
├── httpx (HTTP client)
├── beautifulsoup4 (HTML parsing)
├── jinja2 (templating)
├── qrcode (QR generation)
└── pillow (image processing)
```

## Database Schema Relationships

```
┌─────────────────────────────────────────┐
│              items table                │
├─────────────────────────────────────────┤
│ id (PK)                    INTEGER      │
│ item_name                  TEXT         │
│ purchase_price             REAL         │
│ shipping_cost              REAL         │
│ target_price               REAL         │
│ product_url                TEXT         │
│ status                     TEXT         │
│ final_sold_price           REAL         │
│ report_path                TEXT         │◄─── Links to HTML file
│ image_urls_cache           TEXT         │◄─── JSON array
│ category                   TEXT         │
│ selected_images            TEXT         │◄─── JSON array
└─────────────────────────────────────────┘
         │                    │
         │                    │
         ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│  Image Files     │  │  Report Files    │
│  data/images/    │  │  reports/        │
│  item_[id]/      │  │  item_[id].html  │
└──────────────────┘  └──────────────────┘
```

## File System Structure

```
project_root/
│
├── Application Code
│   ├── main.py              (Entry point, TUI)
│   ├── database.py          (Data layer)
│   ├── scraper.py           (Web scraping)
│   ├── report_generator.py  (HTML generation)
│   ├── utils.py             (Helpers)
│   └── config.py            (Settings)
│
├── Support Scripts
│   ├── test_setup.py        (Verification)
│   ├── sample_data.py       (Demo data)
│   └── run.bat              (Launcher)
│
├── Documentation
│   ├── README.md            (Main docs)
│   ├── QUICKSTART.md        (Quick guide)
│   ├── INSTALL.md           (Installation)
│   ├── PROJECT_OVERVIEW.md  (Overview)
│   ├── FEATURES_CHECKLIST.md (Requirements)
│   └── ARCHITECTURE.md      (This file)
│
├── Configuration
│   ├── requirements.txt     (Dependencies)
│   └── .gitignore          (Git exclusions)
│
└── Runtime Data (created on first run)
    ├── tracker.db          (SQLite database)
    ├── data/
    │   └── images/
    │       ├── item_1/
    │       ├── item_2/
    │       └── ...
    └── reports/
        ├── index.html
        ├── item_1_report.html
        ├── item_2_report.html
        └── ...
```

## State Management

### Application State
```
┌─────────────────────────────────────┐
│        Textual App State            │
├─────────────────────────────────────┤
│ - Current Screen                    │
│ - Selected Item ID                  │
│ - Form Input Values                 │
│ - Scraped Image URLs (temp)         │
└─────────────────────────────────────┘
```

### Persistent State
```
┌─────────────────────────────────────┐
│        Database State               │
├─────────────────────────────────────┤
│ - All Items                         │
│ - Cached Image URLs                 │
│ - Report Paths                      │
│ - Item Status                       │
└─────────────────────────────────────┘
```

### File System State
```
┌─────────────────────────────────────┐
│      File System State              │
├─────────────────────────────────────┤
│ - Downloaded Images                 │
│ - Generated Reports                 │
│ - Master Index                      │
└─────────────────────────────────────┘
```

## Event Flow

### User Events → Actions

```
Keyboard/Mouse Event
    │
    ├─► Key Press 'a' → action_add_item()
    ├─► Key Press 'e' → action_edit_item()
    ├─► Key Press 'd' → action_delete_item()
    ├─► Key Press 'r' → action_generate_report()
    ├─► Key Press 'm' → action_master_index()
    ├─► Key Press 'q' → action_quit()
    │
    ├─► Button Click → on_button_pressed()
    ├─► Input Change → on_input_changed()
    └─► Radio Change → on_radio_set_changed()
```

## Performance Characteristics

### Time Complexity
- Database queries: O(n) for full table scan, O(1) for ID lookup
- Image scraping: O(1) per request (network bound)
- Report generation: O(m) where m = number of images
- Master index: O(n) where n = number of items

### Space Complexity
- Database: O(n) where n = number of items
- Images: O(n*m) where m = images per item
- Reports: O(n) HTML files
- Memory: O(1) - constant for UI state

### Bottlenecks
1. **Network**: Image scraping (mitigated by caching)
2. **Disk I/O**: Image downloads (async possible)
3. **Base64 Encoding**: Large images (optimized with compression)

## Security Considerations

### Input Validation
```
User Input
    │
    ├─► Price validation (utils.validate_price)
    ├─► URL validation (utils.validate_url)
    ├─► Filename sanitization (utils.sanitize_filename)
    └─► SQL injection prevention (parameterized queries)
```

### Data Protection
- Local storage only (no cloud)
- No authentication required
- No sensitive data encryption
- Safe HTML generation (no script injection)

---

**Architecture designed for simplicity, maintainability, and extensibility**
