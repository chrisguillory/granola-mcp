# Possible Future Features for Granola MCP Server

**Last Updated:** October 29, 2025
**Source:** Proxyman traffic captures and Perplexity research on Granola.ai reverse engineering

---

## Context

Granola's API is completely undocumented and private. All endpoints in this MCP server were discovered through reverse engineering using Proxyman to intercept network traffic. This document tracks features that Granola offers but we haven't yet implemented, based on research into:
- Community reverse engineering projects
- Granola's documented features
- Similar meeting intelligence APIs (Fireflies.ai, Otter.ai, Read.ai)

---

## Discovered API Endpoints (Via Proxyman)

### Authentication
- **Method:** Bearer token authentication
- **Token Source:** WorkOS OAuth tokens from `~/Library/Application Support/Granola/supabase.json`
- **Header:** `Authorization: Bearer {access_token}`

### Implemented Endpoints

#### 1. `/v2/get-documents` (List/Filter)
**Method:** POST
**Purpose:** List and filter meetings with pagination
**Implemented As:** `list_meetings()`

**Request Parameters:**
- `limit` (int) - Max results to return
- `offset` (int) - Pagination offset
- `id` (str) - Get specific document by ID (efficient single-document fetch)
- `list_id` (str) - Filter by meeting list (server-side filtering)
- `include_last_viewed_panel` (bool) - Include last viewed panel data

**Response:** `{docs: [GranolaDocument...], deleted: [str...]}`

**Note:** API does not support server-side search. `list_meetings()` implements client-side title filtering with caching.

---

#### 2. `/v1/get-documents-batch` (Batch Retrieval)
**Method:** POST
**Purpose:** Fetch multiple specific meetings by document IDs
**Implemented As:** `get_meetings(document_ids)`

**Request Parameters:**
- `document_ids` (list[str]) - Array of document IDs to fetch

**Response:** `{docs: [GranolaDocument...]}`

**Note:** More efficient than multiple individual calls when fetching known document IDs.

---

#### 3. `/v1/get-document-panels` (AI Notes)
**Method:** POST
**Purpose:** Get AI-generated meeting notes and summaries
**Implemented As:** `download_note()`

**Request Parameters:**
- `document_id` (str) - Meeting document ID

**Response:** Array of panels with ProseMirror JSON content

**Key Panel:** Template slug `v2:meeting-summary-consolidated` contains main AI notes

---

#### 4. `/v1/get-document-transcript` (Transcripts)
**Method:** POST
**Purpose:** Get meeting transcript with timestamps and speaker labels
**Implemented As:** `download_transcript()`

**Request Parameters:**
- `document_id` (str) - Meeting document ID

**Response:** Array of transcript segments with:
- `start_timestamp` / `end_timestamp`
- `text` - Segment content
- `source` - "microphone" (user) or "system" (others)
- `is_final` - Processing status

---

#### 5. `/v1/get-document-lists-metadata` (Meeting Lists)
**Method:** POST
**Purpose:** Get all meeting lists/collections with document IDs
**Implemented As:** `get_meeting_lists()`

**Request Parameters:**
- `include_document_ids` (bool) - Include array of document IDs in each list
- `include_only_joined_lists` (bool) - Filter for joined lists only

**Response:** `{lists: {list_id: {id, title, document_ids[], ...}}}`

---

#### 6. `/v1/update-document` (Delete/Undelete Meetings)
**Method:** POST
**Purpose:** Update document fields, specifically for deleting and undeleting meetings
**Implemented As:** `delete_meeting()` and `undelete_meeting()`

**Request Parameters:**
- `id` (str) - Document ID to update
- `deleted_at` (str | None) - ISO timestamp for deletion, or None to undelete

**Response:** Success response (exact structure TBD)

**Delete Example:**
```json
{
  "id": "document-id",
  "deleted_at": "2025-10-28T17:39:52.302Z"
}
```

**Undelete Example:**
```json
{
  "id": "document-id",
  "deleted_at": null
}
```

**Behavior:**
- Deleted meetings don't appear in search results
- Deleted meetings appear in the `deleted` array of `/v2/get-documents` responses
- Undeleting fully restores the meeting with all data intact

---

### Discovered But Not Implemented

#### 7. `/v1/set-person`
**Method:** POST

**Request Parameters:**
```json
{
  "id": "user-uuid",
  "created_at": "2025-05-29T22:39:03.024Z",
  "user_id": "user-uuid",
  "name": "string",
  "job_title": "string | null",
  "company_name": "string",
  "company_description": "string",
  "links": [],
  "email": "string",
  "avatar": "string (url)",
  "favorite_panel_templates": [{"template_id": "uuid"}, ...],
  "user_type": "string",
  "subscription_name": "string"
}
```

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/set-person' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]' \
  --data-raw '{"id":"user-id","name":"...",...}'
```

---

#### 8. `/v1/get-feature-flags`
**Method:** POST

**Request Parameters:**
```json
{
  "force_defaults": false
}
```

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-feature-flags' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]' \
  --data-raw '{"force_defaults":false}'
```

---

#### 9. `/v1/get-people`
**Method:** POST

**Request Parameters:** None (empty POST body)

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-people' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]'
```

---

#### 10. `/v1/get-attio-integration`
**Method:** POST

**Request Parameters:** None (empty POST body)

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-attio-integration' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]'
```

---

#### 11. `/v1/get-workspaces`
**Method:** POST

**Request Parameters:**
```json
{}
```

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-workspaces' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]' \
  --data-raw '{}'
```

---

#### 12. `/v1/get-recipes`
**Method:** POST

**Request Parameters:** None (empty POST body)

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-recipes' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]'
```

---

#### 13. `/v1/get-current-subscription`
**Method:** POST

**Request Parameters:**
```json
{
  "include_stripe_data": false
}
```

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-current-subscription' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]' \
  --data-raw '{"include_stripe_data":false}'
```

---

#### 14. `/v1/get-workspace-members`
**Method:** POST

**Request Parameters:**
```json
{
  "workspace_id": "workspace-uuid"
}
```

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-workspace-members' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]' \
  --data-raw '{"workspace_id":"workspace-uuid"}'
```

---

#### 15. `/v1/get-entity-batch`
**Method:** POST

**Request Parameters:**
```json
{
  "entity_type": "string",
  "entity_ids": ["id1", "id2", ...]
}
```

**Response:** `{data: [{id, data: {...}}], entity_type: str}`

**Curl Example:**
```bash
curl 'https://api.granola.ai/v1/get-entity-batch' \
  -X POST \
  -H 'Authorization: Bearer [TOKEN_REDACTED]' \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Version: 6.289.0' \
  -H 'X-Granola-Device-Id: [DEVICE_ID_REDACTED]' \
  -H 'X-Granola-Workspace-Id: [WORKSPACE_ID_REDACTED]' \
  --data-raw '{"entity_type":"chat_message","entity_ids":[...]}'
```

---

### Request Pattern Template

```bash
curl 'https://api.granola.ai/v1/{endpoint}' \
  -X POST \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  --data-raw '{json_payload}'
```

**Headers Used:**
- `Authorization: Bearer {access_token}` (required)
- `Content-Type: application/json` (required for POST with body)
- `X-Client-Version: 6.289.0` (observed, not required)
- `X-Granola-Device-Id: {device_hash}` (observed, not required)
- `X-Granola-Workspace-Id: {workspace_uuid}` (observed, not required)

---

## Community Reverse Engineering Efforts

### Granola-Claude MCP Server (Alternative Approach)
- **Method:** Uses local cache file at `~/Library/Application Support/Granola/cache-v3.json`
- **Architecture:** Parses double-JSON encoded cache with 3 collections: documents, meetingsMetadata, transcripts
- **Tools:** `get_recent_meetings`, `search_meetings`, `get_meeting_details`, `get_statistics`
- **Limitation:** Read-only local cache access, no live API calls
- **Reference:** https://cobblehilldigital.com/articles/how-to-build-a-custom-granola-claude-mcp-integration-for-ai-powered-meeting-intelligence

**Our Advantage:** We use actual API endpoints, providing live data and potential for write operations.

### Obsidian Integration
- **Developer:** Joseph Thacker
- **Purpose:** Export Granola notes to Obsidian vaults
- **Method:** Local cache parsing and markdown conversion
- **Reference:** https://josephthacker.com/hacking/2025/05/08/reverse-engineering-granola-notes.html

---

## Current Implementation Status

### ✅ Implemented (Core Read Operations)
- **List & Discovery:** `list_meetings(title_contains, case_sensitive, list_id, limit)` with client-side filtering and caching
- **Lists:** `get_meeting_lists()` - All collections with document IDs
- **Batch Retrieval:** `get_meetings(document_ids)` - Fetch multiple meetings at once
- **AI Notes:** `download_note()` - AI-generated meeting summaries
- **Private Notes:** `download_private_notes()` - User's personal notes
- **Transcripts:** `download_transcript()` - Full conversation with speaker labels
- **Delete/Undelete:** `delete_meeting()` and `undelete_meeting()` - Soft delete meetings

All download tools produce byte-for-byte identical markdown to Granola's official export.

---

## Granola Features Not Yet Implemented

### 🔥 High Priority

#### 1. Action Items Extraction
**Feature:** Granola automatically extracts action items from meetings
**Use Case:** Users can view action items in Granola and flow them to task management systems via Zapier
**Likely Endpoint:** `POST /v1/get-action-items` or embedded in document panels
**Expected Data:**
- Action item text
- Status (completed/pending)
- Assignee information
- Deadline/due date
- Source meeting reference

**Implementation Notes:**
- May be part of existing panels endpoint with different template_slug
- Could be separate endpoint like transcripts
- Test with Proxyman during meeting with clear action items

---

#### 2. Meeting Templates
**Feature:** Pre-built and custom templates for structuring different meeting types
**Use Case:** One-on-ones, stand-ups, weekly syncs have different formats
**Likely Endpoints:**
- `GET /v1/templates` - List available templates
- `GET /v1/templates/{id}` - Get template details
- `POST /v1/create-template` - Create custom template

**Expected Data:**
- Template ID and name
- Template content/structure
- Meeting type association
- User-created vs system templates

**Implementation Notes:**
- Would complement `download_note()` by showing which template was used
- Could enable applying templates to meetings programmatically

---

### 📊 Medium Priority

**Note:** Granola only supports real-time transcription during live meetings. It does NOT support uploading pre-recorded audio/video files.

#### 3. Folder Analytics
**Feature:** Analyze entire folders of meetings, source-cited insights
**Use Case:** "What themes emerged across all Q4 sales calls?"
**Likely Endpoint:** `POST /v1/analyze-folder`

**Expected Data:**
- Folder ID
- Analysis query/prompt
- Aggregated statistics
- Source citations with meeting references

**Implementation Notes:**
- Granola 2.0 feature for team collaboration
- May require specific permission levels

---

#### 4. AI Chat Interface
**Feature:** "Ask Granola" - Natural language queries about meetings
**Use Case:** "What questions did they have?" "Who needs follow-up?"
**Likely Endpoint:** `POST /v1/chat` or `POST /v1/query`

**Expected Data:**
- Meeting context (document_ids)
- User query
- AI-generated response
- Source references

**Implementation Notes:**
- Complex feature, likely requires managing conversation state
- May support multi-model routing (OpenAI/Anthropic/Google)
- Lower priority since we already enable this via MCP + Claude

---

### 🔧 Low Priority (Enterprise/Integration)

#### 5. Team & Workspace Management
**Features:**
- Create/manage workspaces
- Add/remove team members
- Assign roles and permissions
- Browse domain-wide public folders

**Likely Endpoints:**
- `GET /v1/workspaces`
- `POST /v1/workspace/{id}/members`
- `PUT /v1/workspace/{id}/permissions`

**Implementation Notes:**
- Granola 2.0 enterprise features
- Write operations with potential security implications
- Most users won't need programmatic workspace management

---

#### 6. Sharing & Collaboration
**Features:**
- Create share links
- Manage folder permissions
- Invite guests without accounts

**Likely Endpoints:**
- `POST /v1/share`
- `PUT /v1/folder/{id}/permissions`

**Implementation Notes:**
- Write operations
- Security-sensitive (permission management)

---

#### 7. External Integrations
**Features Already in Granola:**
- Slack auto-posting
- CRM sync (HubSpot, Affinity, Attio)
- Notion database creation
- Zapier webhooks

**Implementation Notes:**
- These exist as Granola → External integrations
- Not relevant for MCP server (we consume Granola data, not push to external systems)
- Users should use Granola's native integrations for these

---

## Testing Strategy with Proxyman

When testing for new endpoints:

1. **Trigger the feature in Granola app** (e.g., view action items, select template)
2. **Capture network traffic** with Proxyman
3. **Identify API call patterns** (URL, method, payload, response)
4. **Validate with test data** (multiple meetings to confirm schema)
5. **Implement in MCP server** with strict Pydantic models

---

## API Pattern Observations (From Similar Platforms)

### Fireflies.ai (GraphQL)
- Single endpoint for all queries
- Rich transcript query with sentence-level data
- Custom NLP for domain-specific extraction
- Webhooks for event notifications

### Otter.ai (REST)
- OAuth 2.0 authentication
- Versioned endpoints
- Webhook support with HMAC signing
- Scoped access control

### Read.ai
- Webhook-first architecture
- Pushes data to clients on meeting completion
- Comprehensive payload with all meeting artifacts

**Granola Likely Pattern:** REST API (based on endpoints discovered) with OAuth for official tier, but currently using WorkOS tokens from local storage.

---

## Write Operations: Risk Assessment

### Potential Write Operations
- Update meeting notes
- Mark action items complete
- Create/modify lists
- Apply templates to meetings
- Upload audio for transcription

### Risks
- **API Changes:** Undocumented API can change without notice
- **Rate Limiting:** Unknown limits, could break with heavy usage
- **Data Corruption:** Write operations could corrupt user data
- **Terms of Service:** Potential violation if Granola prohibits API access

### Recommendations
- **Start with read operations only** (current approach)
- **Add write operations** only if:
  - Clear user demand exists
  - Test thoroughly with non-production data
  - Implement safeguards (confirmation prompts, backups)
  - Monitor for API changes

---

## Next Steps

1. **User-Driven Priorities:** Wait for feature requests before implementing
2. **Proxyman Testing:** If implementing action items, test endpoint discovery first
3. **Incremental Additions:** Add one feature at a time, test thoroughly
4. **Community Collaboration:** Monitor for other reverse engineering efforts
5. **Official API Watch:** Check periodically if Granola releases official documentation

---

## References

- [Cobble Hill: Granola-Claude MCP Integration](https://cobblehilldigital.com/articles/how-to-build-a-custom-granola-claude-mcp-integration-for-ai-powered-meeting-intelligence)
- [Joseph Thacker: Reverse Engineering Granola Notes](https://josephthacker.com/hacking/2025/05/08/reverse-engineering-granola-notes.html)
- [Granola Blog: 2.0 Launch](https://www.granola.ai/blog/two-dot-zero)
- [Fireflies API Documentation](https://docs.fireflies.ai/getting-started/introduction)
- [Otter.ai API Reference](https://developer-guides-staging.tryotter.com/api-reference/)
- [Read.ai Webhooks Guide](https://support.read.ai/hc/en-us/articles/16352415827219-Getting-Started-with-Webhooks)

---

## Community Contributions

If you discover new endpoints or implement additional features, please document them here or open an issue on the repository.
