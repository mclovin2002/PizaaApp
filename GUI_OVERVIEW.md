# PizzaApp GUI Overview

## Visual Design

### Color Scheme
- **Background**: Pure white (#FFFFFF) for a clean, professional look
- **Accent**: Pizza orange (#FF6B35) for buttons and headers
- **Secondary**: Light gray (#F7F7F7) for subtle elements
- **Text**: Dark gray (#333333) for optimal readability

### Logo
- Custom-generated pizza with a bite taken out
- 256x256px PNG with transparency
- Displayed in header (50x50) and credential setup (80x80)

## Layout Structure

```
┌─────────────────────────────────────────────────────┐
│  🍕 PizzaApp                                        │  ← Header (orange)
├─────────────────────────────────────────────────────┤
│  📝 Post  ⏰ Schedule  📦 Bulk  🔄 Auto-Reply  ⚙️   │  ← Tabs
├─────────────────────────────────────────────────────┤
│                                                     │
│                  Tab Content                        │
│              (Forms, buttons, inputs)               │
│                                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## First Launch Experience

1. **Credential Setup Screen**
   - Large pizza logo
   - "PizzaApp Setup" title
   - Link to developer.x.com
   - 4 input fields (API Key, API Secret, Access Token, Access Token Secret)
   - Secrets are masked with asterisks
   - Orange "Save and Continue" button

2. **Main Interface** (after credentials saved)
   - Compact header with logo and app name
   - Tab-based navigation
   - Each tab focused on a single task

## Tab Details

### 📝 Post Now
- Large text area for composing tweet
- Single action button: "Post Tweet"
- Instant feedback via message boxes

### ⏰ Schedule
- Text area for tweet message
- Radio buttons to choose scheduling method:
  - Minutes from now (number input)
  - Today at time (HH:MM input)
  - Day of month (day number + time input)
- "Schedule Tweet" button
- Calendar display for monthly scheduling

### 📦 Bulk
- File browser with "Browse" button
- File path display (read-only)
- Operation type radio buttons:
  - Post immediately with delay
  - Schedule with frequency
- Delay/frequency input (minutes)
- "Execute Bulk Operation" button

### 🔄 Auto-Reply
- Check interval input (minutes)
- Reply message text area
- Toggle button: "Start Auto-Reply" / "Stop Auto-Reply"
- Status indicator: Active (green) / Inactive (gray)

### ⚙️ Settings
- "Reconfigure Credentials" button
- About section with app info and features list

## User Flow Examples

### Posting a Tweet
1. Click "Post Now" tab
2. Type message
3. Click "Post Tweet"
4. See success message

### Scheduling Monthly Tweet
1. Click "Schedule" tab
2. Type message
3. Select "Day of month" radio
4. View calendar display
5. Enter day number and time
6. Click "Schedule Tweet"
7. See confirmation with scheduled time

### Bulk Operations
1. Click "Bulk" tab
2. Click "Browse" and select file
3. Choose operation type
4. Set delay/frequency
5. Click "Execute Bulk Operation"
6. Background thread handles posting
7. See completion message

## Error Handling

All operations include:
- Input validation (empty checks, format checks)
- API error handling with specific messages:
  - Unauthorized (bad credentials)
  - Forbidden (permissions issue)
  - Rate limit exceeded
  - General API errors
- User-friendly error dialogs
- No crashes - graceful degradation

## Threading

- Long-running operations use background threads
- GUI remains responsive during:
  - Scheduled tweet timers
  - Bulk posting
  - Auto-reply loops
- Daemon threads for cleanup on exit

## Persistence

- Credentials saved to `twitter_credentials.py`
- Last mention ID saved to `last_mention_id.txt` (auto-reply)
- Logo cached as `logo.png`

## Accessibility

- High contrast text
- Large, readable fonts (11-18pt)
- Clear button labels
- Consistent spacing (40px padding)
- Logical tab order
