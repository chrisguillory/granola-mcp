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

## Discovered API Endpoints (Not Yet Implemented)

### Authentication
- **Method:** Bearer token authentication
- **Token Source:** WorkOS OAuth tokens from `~/Library/Application Support/Granola/supabase.json`
- **Header:** `Authorization: Bearer {access_token}`

### Endpoints Discovered via Proxyman

#### `/v1/get-users-with-access` (Document Sharing)
**Method:** POST
**Purpose:** Get list of users who have access to a specific document
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_id": "39e93a7b-dd9b-4c06-be70-d5aabd0569fe"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Show who has access to meeting notes
- Implement access control management
- Display sharing status in meeting list

**Implementation Priority:** Medium - useful for collaboration features

---

#### `/v1/get-workspace-invite-links` (Workspace Invitations)
**Method:** POST
**Purpose:** Get workspace invite links for sharing
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "workspace_id": "1858c68b-4bed-4110-a70c-c4819dab05f0"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Generate workspace invite links
- Manage team member invitations
- Implement workspace sharing features

**Implementation Priority:** Low - workspace management feature

---

#### `/v1/get-workspaces-for-slug` (Workspace Lookup)
**Method:** POST
**Purpose:** Look up workspace information by slug
**Discovered:** January 2025 via Proxyman

**Request Parameters:** TBD (no body in captured request)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Resolve workspace by friendly slug
- Workspace discovery
- Multi-workspace navigation

**Implementation Priority:** Low - workspace navigation feature

---

#### `/v1/get-notion-integration` (Notion Integration)
**Method:** POST
**Purpose:** Get Notion integration settings for the workspace
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Check if Notion integration is enabled
- Get Notion connection status
- Display integration settings
- Could extend to other integrations (Slack, etc.)

**Implementation Priority:** Low - integration management feature

---

#### `/v1/refresh-google-events` (Calendar Sync)
**Method:** POST
**Purpose:** Refresh/sync Google Calendar events for meeting data
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "selected_calendars_only": true
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")
- `sentry-trace` - Sentry distributed tracing header
- `baggage` - Sentry context propagation

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Manually trigger calendar sync
- Refresh meeting metadata from Google Calendar
- Update attendee information
- Sync after calendar permissions change

**Implementation Priority:** Medium - useful for keeping meeting data fresh

---

#### `/v1/check-for-update/latest-mac.yml` (App Updates)
**Method:** GET
**Purpose:** Check for Granola desktop app updates (Electron auto-updater)
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (GET request)

**Additional Headers:**
- `x-user-staging-id` - User staging identifier
- `User-Agent: electron-builder` - Identifies as Electron updater
- `sentry-trace` - Sentry distributed tracing

**Response:** YAML file with latest version info (Electron updater format)

**Potential Use Cases:**
- Check current Granola app version
- Monitor for new releases

**Implementation Priority:** Very Low - not relevant for MCP server (app infrastructure only)

**Note:** Similar endpoints likely exist for other platforms (`latest-win.yml`, `latest-linux.yml`)

---

#### `/v1/get-panel-templates` (Meeting Note Templates)
**Method:** POST
**Purpose:** Get available panel templates for meeting notes
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- List available meeting note templates
- Show which templates are available for a workspace
- Apply templates programmatically to meetings
- Create custom templates

**Implementation Priority:** High - directly related to Meeting Templates feature (see below in "Granola Features Not Yet Implemented")

**Related:** This is likely the endpoint for the "Meeting Templates" feature mentioned in the high-priority section. Templates structure different meeting types (1:1s, stand-ups, etc.)

---

#### `/v1/get-document-metadata` (Document Metadata)
**Method:** POST
**Purpose:** Get metadata for a specific document (lightweight alternative to full document fetch)
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_id": "f09c551a-eef2-4cc4-8ea0-39a1ee765ba8"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Quick metadata lookup without fetching full document
- Check document status/existence
- Get document title, date, participants without notes/transcript
- More efficient than `/v2/get-documents` when you only need metadata

**Implementation Priority:** Medium - useful optimization for metadata-only queries

**Note:** This is likely a lighter-weight alternative to fetching the full document via `/v2/get-documents` with `id` parameter.

---

#### `/v1/get-free-trial-data` (Free Trial Status)
**Method:** POST
**Purpose:** Get free trial information and status for the user
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Check free trial status and remaining time
- Display trial expiration warnings
- Show upgrade prompts when trial expires
- Track trial usage metrics

**Implementation Priority:** Low - account/billing feature, not core functionality

---

#### `/v1/sync-push` (Sync Engine - Push)
**Method:** POST
**Purpose:** Push local changes/operations to the server (part of sync engine)
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "operations": [
    {
      "type": "add",
      "workspace_id": "uuid",
      "user_id": "uuid",
      "entity": {
        "id": "uuid",
        "created_at": "2025-11-01T15:55:03.198Z",
        "updated_at": "2025-11-01T15:55:03.198Z",
        "deleted_at": null,
        "workspace_id": "uuid",
        "type": "chat_thread",
        "data": {}
      },
      "operation_id": "uuid",
      "status": "pending",
      "created_at": "2025-11-01T15:55:03.199Z"
    }
  ]
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Operation Types Observed:**
- `add` - Create new entity
- Likely: `update`, `delete` - Modify/remove entities

**Entity Types Observed:**
- `chat_thread` - Chat/conversation threads
- Likely others: documents, notes, etc.

**Potential Use Cases:**
- Sync local changes to server
- Create chat threads programmatically
- Update document metadata
- Implement offline-first sync

**Implementation Priority:** High - write operations, enables creating/modifying data

**IMPORTANT:** This is a write operation. Use with extreme caution. Could potentially:
- Create documents/threads
- Modify existing data
- Part of the sync engine mentioned in Amplitude flags (`flag_sync_engine_push_enabled: true`)

**Related:** Likely paired with `/v1/sync-pull` for bidirectional sync

---

#### `/v1/create-document-list` (Create Meeting List/Folder)
**Method:** POST
**Purpose:** Create a new meeting list/folder/collection
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "id": "f6c77f90-55cc-43c5-a721-91ab4f4e0851",
  "title": "User interviews",
  "icon": {
    "type": "icon",
    "value": "UserIcon",
    "color": "amber"
  },
  "visibility": "workspace",
  "description": "Deep research conversations to uncover user behaviors, workarounds, and feature requirements",
  "is_default_folder": false
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Parameters:**
- `id` - UUID for the new list (client-generated)
- `title` - Display name for the list
- `icon` - Icon configuration (type, value, color)
- `visibility` - Access level ("workspace", "private", etc.)
- `description` - Optional description text
- `is_default_folder` - Whether this is a default/system folder

**Icon Types Observed:**
- `UserIcon` with color `amber`
- Likely others from Heroicons or similar library

**Potential Use Cases:**
- Programmatically create meeting collections
- Organize meetings by project/client/topic
- Auto-create folders based on meeting metadata
- Integration with project management tools

**Implementation Priority:** High - write operation, enables folder management

**IMPORTANT:** This is a write operation. Use with caution. Creates persistent folder structure in user's Granola workspace.

**Related:** Pairs with `get_meeting_lists()` for read operations

---

#### `/v1/get-user-info` (User Information)
**Method:** POST
**Purpose:** Get current user's profile information
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Get user profile data
- Display current user information
- User account management

**Implementation Priority:** Low - user metadata

---

#### `/v1/get-user-preferences` (User Preferences)
**Method:** POST
**Purpose:** Get user's application preferences and settings
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Get user settings
- Display preferences
- Sync settings across devices

**Implementation Priority:** Low - settings management

---

#### `/v1/get-document-set` (Document Set)
**Method:** POST
**Purpose:** Get a set of documents (batch operation alternative)
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Batch document retrieval
- Alternative to get-documents-batch
- Efficient document fetching

**Implementation Priority:** Medium - batch operations

**Related:** Similar to `/v1/get-documents-batch` but different API pattern

---

#### `/v1/get-entity-set` (Entity Set)
**Method:** POST
**Purpose:** Get a set of entities by type (e.g., chat threads, documents)
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "entity_type": "chat_thread"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Entity Types Observed:**
- `chat_thread` - Chat/conversation threads

**Potential Use Cases:**
- Fetch all chat threads
- Retrieve entity collections by type
- Generic entity fetching

**Implementation Priority:** Medium - entity management

**Related:** Works with `/v1/get-entity-batch` which fetches specific entities by IDs

---

#### `/v1/get-integrations` (Get Integrations)
**Method:** POST
**Purpose:** Get all configured integrations for the workspace
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- List enabled integrations (Notion, Attio, HubSpot, etc.)
- Check integration status
- Display integration settings

**Implementation Priority:** Low - integration management

---

#### `/v1/upsert-integrations` (Update Integrations)
**Method:** POST
**Purpose:** Create or update integration settings
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "affinity_domain": null
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Configure CRM integrations
- Update integration settings
- Enable/disable integrations

**Implementation Priority:** Low - integration management

**IMPORTANT:** This is a write operation. Use with caution when modifying integration settings.

---

#### `/v1/get-selected-calendars` (Selected Calendars)
**Method:** POST
**Purpose:** Get user's selected Google Calendar calendars
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- List calendars enabled for Granola
- Display calendar sync settings
- Manage calendar selection

**Implementation Priority:** Medium - calendar integration

**Related:** Works with `/v1/refresh-google-events` for calendar sync

---

#### `/v1/get-chat-models` (Available Chat Models)
**Method:** POST
**Purpose:** Get list of available AI models for chat
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Expected Data:**
- Available models (Claude, GPT-4, Gemini, etc.)
- Model capabilities
- Model availability by subscription tier

**Potential Use Cases:**
- Show available AI models
- Model selection UI
- Feature availability check

**Implementation Priority:** High - shows which AI models are available for chat

**Note:** Granola supports multiple LLM providers. This endpoint likely returns the available models based on subscription and feature flags.

---

#### `/v1/get-invite-list` (Invite List)
**Method:** POST
**Purpose:** Get list of people for invitation suggestions
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "include_external_people": false,
  "include_granola_users": false
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Get invitation suggestions
- Show people to invite to meetings
- Contact list management

**Implementation Priority:** Low - invitation features

---

#### `/v1/upsert-document` (Create/Update Document)
**Method:** POST
**Purpose:** Create or update entire document with full payload
**Discovered:** January 2025 via Proxyman

**Request Parameters:** Full document object with all fields:
```json
{
  "id": "document-uuid",
  "created_at": "2025-10-20T14:42:15.887Z",
  "updated_at": "2025-11-01T15:25:54.795Z",
  "deleted_at": "2025-11-01T15:25:54.795Z",
  "user_id": "user-uuid",
  "workspace_id": "workspace-uuid",
  "type": "meeting",
  "title": "Meeting Title",
  "notes": {
    "type": "doc",
    "content": []
  },
  "notes_markdown": "",
  "notes_plain": "",
  "people": {},
  "transcribe": false,
  "google_calendar_event": null,
  "subscription_plan_id": "granola.plan.free-trial.v1",
  ...
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Create new meetings programmatically
- Update existing meeting data
- Modify meeting notes
- Delete meetings (via `deleted_at`)
- Full document management

**Implementation Priority:** **CRITICAL** - Full document write operation

**IMPORTANT:** This is the main document write endpoint. Extremely powerful and dangerous:
- Can create entire new meetings
- Can update any document field
- Can delete documents (via `deleted_at` field)
- Can modify notes, transcripts, metadata
- Requires full document payload

**Related:** More comprehensive than `/v1/update-document` which only updates specific fields. This is "upsert" (update or insert) for entire documents.

**DANGER:** Use with extreme caution. Test thoroughly before implementing. Could corrupt user data if used incorrectly.

---

#### `/v1/get-attachments` (Get Attachments)
**Method:** POST
**Purpose:** Get file attachments for a document list/folder
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_list_id": "f6c77f90-55cc-43c5-a721-91ab4f4e0851"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- List all attachments in a folder
- Display attached files for meetings
- Download meeting attachments
- File management for meeting lists

**Implementation Priority:** Medium - file/attachment management

**Note:** Granola supports attaching files to meetings (images, documents, etc.). This endpoint retrieves those attachments for a specific list/folder.

---

#### `/v1/get-slack-integration` (Slack Integration)
**Method:** POST
**Purpose:** Get Slack integration settings and status
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Check if Slack integration is enabled
- Get Slack workspace connection status
- Display Slack posting settings
- Auto-post meeting notes to Slack channels

**Implementation Priority:** Low - integration management

**Related:** Similar to `/v1/get-notion-integration`, `/v1/get-attio-integration`, `/v1/get-hubspot-integration`

---

#### `/v1/refresh-access-token` (Token Refresh)
**Method:** POST
**Purpose:** Refresh OAuth access token using refresh token
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "refresh_token": "sFr9MEIZr9SPJZL2bv3GmS5a9",
  "provider": "workos"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")
- `sentry-trace` - Sentry distributed tracing
- `baggage` - Sentry context propagation

**Response:** TBD (needs capture to document structure - likely returns new access_token)

**Potential Use Cases:**
- Refresh expired access tokens
- Maintain long-running MCP server sessions
- Implement token rotation for security

**Implementation Priority:** High - critical for authentication management

**Note:** This is the token refresh mechanism. The MCP server currently reads tokens from local storage but could use this to refresh them when they expire.

---

#### `/v1/get-hubspot-integration` (HubSpot Integration)
**Method:** POST
**Purpose:** Get HubSpot CRM integration settings and status
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Check if HubSpot integration is enabled
- Get HubSpot connection status
- Display CRM sync settings
- Auto-create HubSpot notes from meetings

**Implementation Priority:** Low - integration management

**Related:** Part of Granola's CRM integration suite (HubSpot, Attio, Affinity)

---

#### `/v1/get-knock-user-token` (Knock Notifications Token)
**Method:** POST
**Purpose:** Get authentication token for Knock (notification service)
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Authenticate with Knock notification service
- Enable in-app notifications
- Push notification management

**Implementation Priority:** Very Low - internal infrastructure

**Note:** Knock (knock.app) is a notification infrastructure service. This token is used for in-app notifications in the Granola desktop app.

---

#### `/v1/get-deepgram-token` (Deepgram Transcription Token)
**Method:** POST
**Purpose:** Get authentication token for Deepgram speech-to-text API
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")
- `sentry-trace` - Sentry distributed tracing
- `baggage` - Sentry context propagation

**Response:** TBD (needs capture to document structure - likely returns Deepgram API key)

**Potential Use Cases:**
- Authenticate with Deepgram for real-time transcription
- Enable live meeting transcription
- Access speech-to-text services

**Implementation Priority:** Low - internal infrastructure for transcription

**Note:** Deepgram (deepgram.com) is Granola's speech-to-text provider. This token is used to authenticate with Deepgram's API for real-time meeting transcription. Granola uses Deepgram for live audio transcription during meetings.

---

#### `/v1/add-user-favourite-document-list` (Add Favorite Folder)
**Method:** POST
**Purpose:** Add a document list/folder to user's favorites
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_list_id": "f6c77f90-55cc-43c5-a721-91ab4f4e0851"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Pin important folders to favorites
- Quick access to frequently used folders
- User folder organization

**Implementation Priority:** Medium - user preference management

**IMPORTANT:** This is a write operation. Modifies user favorites list.

**Related:** Pairs with `/v1/remove-user-favourite-document-list`

---

#### `/v1/remove-user-favourite-document-list` (Remove Favorite Folder)
**Method:** POST
**Purpose:** Remove a document list/folder from user's favorites
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_list_id": "f6c77f90-55cc-43c5-a721-91ab4f4e0851"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Unpin folders from favorites
- Manage favorite folders list
- User folder organization

**Implementation Priority:** Medium - user preference management

**IMPORTANT:** This is a write operation. Modifies user favorites list.

---

#### `/v1/get-folder-zapier-integrations` (Get Zapier Webhooks)
**Method:** POST
**Purpose:** Get Zapier webhook integrations configured for a specific folder
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_list_id": "f6c77f90-55cc-43c5-a721-91ab4f4e0851"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- List Zapier webhooks for a folder
- Check if folder has automation configured
- Display webhook settings
- Manage folder-level Zapier integrations

**Implementation Priority:** Low - integration management

**Note:** Granola supports per-folder Zapier webhooks that trigger when new meetings are added to the folder.

---

#### `/v1/delete-document-list` (Delete Folder)
**Method:** POST
**Purpose:** Delete a document list/folder
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "id": "f6c77f90-55cc-43c5-a721-91ab4f4e0851"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Delete unused folders
- Clean up folder structure
- Remove meeting collections

**Implementation Priority:** High - folder management write operation

**IMPORTANT:** This is a destructive write operation. Deletes the folder permanently. Use with extreme caution.

**Related:** Opposite of `/v1/create-document-list`

---

#### `/v1/update-user-preferences` (Update User Preferences)
**Method:** POST
**Purpose:** Update user's application preferences and settings
**Discovered:** January 2025 via Proxyman

**Request Parameters:** Full preferences object with all settings:
```json
{
  "timestamp": 1762013499020,
  "calendarsSelected": {},
  "notificationsBlocked": false,
  "selectedTheme": "system",
  "summaryLanguage": "en",
  "defaultSharingLinkVisibility": "public",
  "listsSidebarPreferences": {
    "width": 192,
    "opened": false
  },
  "activeWorkspaceId": "workspace-uuid",
  ...
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Update user settings programmatically
- Sync settings across devices
- Change theme, language, notifications
- Configure sidebar, default sharing settings

**Implementation Priority:** Medium - user settings management

**IMPORTANT:** This is a write operation. Modifies all user preferences. Requires full preference object.

**Related:** Pairs with `/v1/get-user-preferences` for read operations

---

#### `/v1/get-attio-list-preference` (Get Attio Folder Settings)
**Method:** POST
**Purpose:** Get Attio CRM integration preferences for a specific folder
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_list_id": "7986df58-eed7-4129-958c-d48dd931fbf1"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Check if folder syncs to Attio CRM
- Get Attio sync settings for folder
- Manage folder-level CRM integration

**Implementation Priority:** Low - CRM integration management

**Note:** Granola supports per-folder Attio CRM integration settings.

---

#### `/v1/add-document-to-list` (Add Meeting to Folder)
**Method:** POST
**Purpose:** Add a document/meeting to a folder/list
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_id": "2db1b11e-d9e4-4410-ba05-ce3bfb707969",
  "document_list_id": "7986df58-eed7-4129-958c-d48dd931fbf1"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Organize meetings into folders
- Add meetings to collections
- Programmatically organize meetings by criteria
- Auto-add meetings to project folders

**Implementation Priority:** High - core folder management write operation

**IMPORTANT:** This is a write operation. Adds meeting to folder.

**Related:** Pairs with `/v1/remove-document-from-list`

---

#### `/v1/remove-document-from-list` (Remove Meeting from Folder)
**Method:** POST
**Purpose:** Remove a document/meeting from a folder/list
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "document_id": "2db1b11e-d9e4-4410-ba05-ce3bfb707969",
  "document_list_id": "7986df58-eed7-4129-958c-d48dd931fbf1"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Remove meetings from folders
- Clean up folder organization
- Move meetings between folders (remove + add)

**Implementation Priority:** High - core folder management write operation

**IMPORTANT:** This is a write operation. Removes meeting from folder.

**Note:** This doesn't delete the meeting, only removes it from the folder.

---

#### `/v1/get-privacy-mode` (Privacy Mode Status)
**Method:** POST
**Purpose:** Get privacy mode status for the user
**Discovered:** January 2025 via Proxyman

**Request Parameters:** None (empty POST body)

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Check if privacy mode is enabled
- Display privacy mode status
- Conditional transcription based on privacy settings

**Implementation Priority:** Low - user privacy setting

**Note:** Granola has a privacy mode feature that prevents recording/transcription when enabled.

---

#### `/v1/get-subscriptions` (Get Subscription Plans)
**Method:** POST
**Purpose:** Get available subscription plans and pricing
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "include_enterprise_plan": true
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Display available subscription plans
- Show pricing information
- Upgrade/downgrade plan selection
- Enterprise plan availability check

**Implementation Priority:** Low - billing/subscription management

**Related:** Different from `/v1/get-current-subscription` which shows the user's active plan

---

#### `/v1/create-document` (Create New Document)
**Method:** POST
**Purpose:** Create a new meeting/document
**Discovered:** January 2025 via Proxyman

**Request Parameters:** Full document object:
```json
{
  "id": "e56ed644-105b-4393-a196-c9478dffd0c2",
  "user_id": "83a06d3e-2424-474a-af11-e36ff8f273b5",
  "title": null,
  "created_at": "2025-11-01T16:15:51.796Z",
  "updated_at": "2025-11-01T16:15:51.796Z",
  "type": "meeting",
  "deleted_at": null,
  "transcribe": true,
  "workspace_id": "1858c68b-4bed-4110-a70c-c4819dab05f0",
  "sharing_link_visibility": "public",
  "creation_source": "macOS",
  ...
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure)

**Potential Use Cases:**
- Create new meetings programmatically
- Initialize blank meeting documents
- Start new transcription sessions
- Automated meeting creation

**Implementation Priority:** **HIGH** - Core write operation for creating meetings

**IMPORTANT:** This is a critical write operation. Creates new meeting documents. Use with caution.

**Related:** This is likely the "create" part of CRUD, while `/v1/upsert-document` handles both create and update.

---

#### `/v1/get-transcription-auth-token` (Transcription Auth Token)
**Method:** POST
**Purpose:** Get authentication token for transcription service (Assembly AI)
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "provider": "assembly-universal"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")
- `sentry-trace` - Sentry distributed tracing
- `baggage` - Sentry context propagation

**Response:** TBD (needs capture to document structure - likely returns Assembly AI API token)

**Providers Observed:**
- `assembly-universal` - Assembly AI (alternative to Deepgram)

**Potential Use Cases:**
- Authenticate with Assembly AI for transcription
- Enable live meeting transcription
- Alternative transcription provider to Deepgram

**Implementation Priority:** Low - internal infrastructure for transcription

**Note:** Assembly AI is an alternative speech-to-text provider. Granola may use both Deepgram and Assembly AI depending on configuration or feature flags.

**Related:** Similar to `/v1/get-deepgram-token` but for Assembly AI instead

---

#### `/v1/set-person`
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

#### `/v1/get-feature-flags`
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

#### `/v1/get-people`
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

#### `/v1/get-attio-integration`
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

#### `/v1/get-recipes`
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

#### `/v1/get-current-subscription`
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

#### `/v1/get-workspace-members`
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

#### `/v1/get-entity-batch`
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

#### Action Items Extraction
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

#### Meeting Templates
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

#### Folder Analytics
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

#### AI Chat Interface
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

#### Team & Workspace Management
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

#### Sharing & Collaboration
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

#### External Integrations
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

#### `/v1/upload-file` (File Upload)
**Method:** POST
**Purpose:** Upload files (images, attachments) to Granola's storage
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "fileJSON": {
    "mimeType": "image/jpeg",
    "fileContentBase64": "/9j/4AAQSkZJRgABAQAAAQABAAD..."
  }
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure - likely returns file URL/ID)

**Supported MIME Types:**
- `image/jpeg` (confirmed from sample)
- Likely: `image/png`, `image/gif`, `application/pdf`, etc.

**Potential Use Cases:**
- Upload meeting attachments
- Add images to meeting notes
- Attach files to documents
- Logo uploads for workspaces
- Avatar uploads for users

**Implementation Priority:** High - write operation for file management, enables richer meeting notes

**IMPORTANT:** This is a write operation. Uploads files to Granola's storage (likely S3 or similar).

**Related:** Pairs with `get-attachments` for reading attachments

---

#### `/v1/create-workspace-invite-link` (Create Workspace Invite Link)
**Method:** POST
**Purpose:** Create an invite link for users to join a workspace
**Discovered:** January 2025 via Proxyman

**Request Parameters:**
```json
{
  "workspace_id": "1858c68b-4bed-4110-a70c-c4819dab05f0"
}
```

**Additional Headers:**
- `X-Granola-Workspace-Id` - Workspace UUID
- `X-Granola-Device-Id` - Device identifier hash
- `X-Client-Version` - Client version (e.g., "6.298.0")

**Response:** TBD (needs capture to document structure - likely returns invite link URL and expiration)

**Potential Use Cases:**
- Generate shareable workspace invite links
- Onboard new team members
- Invite external collaborators
- Create time-limited invite links
- Manage workspace access

**Implementation Priority:** Medium - workspace collaboration feature

**IMPORTANT:** This is a write operation. Creates invite links that grant workspace access.

**Related:** Pairs with `get-workspace-invite-links` (read existing links), `get-workspaces`, `get-workspace-members`

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
