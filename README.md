# Granola MCP Server

MCP server for accessing Granola meeting notes and data via Claude Code.

## API Research Findings

### Authentication
Granola uses WorkOS OAuth tokens stored locally:
- **Location**: `~/Library/Application Support/Granola/supabase.json`
- **Format**: JSON file with `workos_tokens` field (JSON string)
- **Token fields**: `access_token`, `refresh_token`, `expires_in`, `session_id`
- **Auth method**: Bearer token in Authorization header

### Available API Endpoints

**Primary endpoint**: `POST https://api.granola.ai/v2/get-documents`
- Parameters: `limit` (int), `offset` (int), `include_last_viewed_panel` (bool)
- Returns: `{"docs": [...]}`
- Pagination: Use offset for additional results

**Headers required**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Document Structure

Each document contains:
- `id` (str): Unique document identifier
- `title` (str | None): Meeting title
- `created_at` (str): ISO timestamp
- `updated_at` (str): ISO timestamp
- `notes` (dict): ProseMirror JSON format (AI-generated notes)
- `notes_markdown` (str | None): Markdown version of notes
- `people` (dict): Meeting participants
- `google_calendar_event` (dict | None): Calendar metadata
- `transcribe` (bool): Whether transcript was enabled
- `type` (str): Usually "meeting"

### ProseMirror Format

Notes are stored in ProseMirror JSON:
```json
{
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 3, "id": "..."},
      "content": [{"type": "text", "text": "..."}]
    },
    {
      "type": "bulletList",
      "attrs": {"tight": true},
      "content": [...]
    }
  ]
}
```

### What Works
✅ List all meetings with pagination
✅ Get AI-generated notes (ProseMirror/Markdown)
✅ Meeting metadata (title, date, participants)
✅ Search by filtering documents

### What Doesn't Work
❌ Raw meeting transcripts (not exposed via API)
❌ Individual document GET endpoints (404 errors)
❌ Separate transcript/chapters endpoints (404 errors)

**Note**: Granola's API is private and undocumented. All endpoints discovered through reverse engineering.

## Installation

```bash
# Add to Claude Code MCP config (user scope)
claude mcp add --user --transport stdio granola -- uv run --script ~/granola-mcp/granola-mcp.py
```

## Available Tools

- **`list_meetings`**: List meetings with pagination/filtering
- **`get_notes`**: Get AI notes for specific meeting (Markdown format)
- **`search_meetings`**: Search meetings by keyword
- **`export_note`**: Export meeting notes to temp file

## Implementation Notes

- Uses `httpx` for async HTTP requests
- Strict Pydantic validation (fail fast on API changes)
- Temp directory for exports (auto-cleanup on shutdown)
- Follows browser-automation-mcp.py patterns

## Development

**Formatting:**
```bash
uvx ruff format .
```
