#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "fastmcp>=2.12.5",
#   "httpx",
#   "pydantic>=2.0",
# ]
# ///
#
# Granola MCP Server
#
# Provides access to Granola meeting notes and data via MCP.
# Architecture: Reads auth tokens from local Granola app data.
#
# Setup:
#   claude mcp add --user --transport stdio granola -- uv run --script ~/granola-mcp/granola-mcp.py

from __future__ import annotations

import json
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, field_validator
from mcp_utils import DualLogger


# =============================================================================
# Pydantic Models - Strict Validation
# =============================================================================


class GranolaDocument(BaseModel):
    """Strict model for Granola document with fail-fast validation."""

    id: str
    title: str | None = None
    created_at: str
    updated_at: str | None = None
    notes: dict | None = None  # ProseMirror JSON
    notes_markdown: str | None = None
    type: str | None = None
    people: dict | None = None
    google_calendar_event: dict | None = None
    transcribe: bool = False

    model_config = {'extra': 'allow'}  # Allow extra fields from API


class MeetingListItem(BaseModel):
    """Simplified meeting info for list views."""

    id: str
    title: str
    created_at: str
    type: str | None = None
    has_notes: bool = False
    participant_count: int = 0


class DocumentsResponse(BaseModel):
    """Response from get-documents API."""

    docs: list[GranolaDocument]

    model_config = {'extra': 'allow'}


class ExportResult(BaseModel):
    """Result from export operation."""

    path: str
    title: str
    size_bytes: int


# =============================================================================
# Global State
# =============================================================================

_temp_dir: tempfile.TemporaryDirectory | None = None
_export_dir: Path | None = None
_http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(server):
    """Manage resources - cleanup on shutdown."""
    global _temp_dir, _export_dir, _http_client

    # Initialize temp directory for exports
    _temp_dir = tempfile.TemporaryDirectory()
    _export_dir = Path(_temp_dir.name)

    # Initialize HTTP client
    _http_client = httpx.AsyncClient(timeout=30.0)

    try:
        yield {}
    finally:
        # Cleanup
        if _http_client:
            await _http_client.aclose()
        if _temp_dir:
            _temp_dir.cleanup()


mcp = FastMCP('granola', lifespan=lifespan)


# =============================================================================
# Authentication
# =============================================================================


def get_auth_token() -> str:
    """
    Read WorkOS access token from Granola's local storage.

    Raises:
        FileNotFoundError: If Granola data directory doesn't exist
        ValueError: If token data is malformed
    """
    granola_dir = Path.home() / 'Library' / 'Application Support' / 'Granola'
    supabase_file = granola_dir / 'supabase.json'

    if not supabase_file.exists():
        raise FileNotFoundError(
            f'Granola auth file not found at {supabase_file}. '
            'Is Granola installed and authenticated?'
        )

    with open(supabase_file) as f:
        data = json.load(f)

    if 'workos_tokens' not in data:
        raise ValueError('No workos_tokens found in Granola auth file')

    tokens = json.loads(data['workos_tokens'])

    if 'access_token' not in tokens:
        raise ValueError('No access_token in workos_tokens')

    return tokens['access_token']


def get_auth_headers() -> dict[str, str]:
    """Get HTTP headers with authentication."""
    token = get_auth_token()
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


# =============================================================================
# ProseMirror to Markdown Conversion
# =============================================================================


def prosemirror_to_markdown(content: dict) -> str:
    """
    Convert ProseMirror JSON to Markdown.

    Simple recursive converter for common node types.
    Falls back to plain text extraction for unknown types.
    """
    if not isinstance(content, dict):
        return ''

    node_type = content.get('type', '')

    # Document root
    if node_type == 'doc':
        children = content.get('content', [])
        return '\n\n'.join(prosemirror_to_markdown(child) for child in children)

    # Headings
    if node_type == 'heading':
        level = content.get('attrs', {}).get('level', 1)
        text = _extract_text(content)
        return f'{"#" * level} {text}'

    # Paragraph
    if node_type == 'paragraph':
        text = _extract_text(content)
        return text if text else ''

    # Bullet list
    if node_type == 'bulletList':
        items = content.get('content', [])
        lines = []
        for item in items:
            if item.get('type') == 'listItem':
                item_text = _extract_text(item)
                lines.append(f'- {item_text}')
        return '\n'.join(lines)

    # Ordered list
    if node_type == 'orderedList':
        items = content.get('content', [])
        lines = []
        for i, item in enumerate(items, 1):
            if item.get('type') == 'listItem':
                item_text = _extract_text(item)
                lines.append(f'{i}. {item_text}')
        return '\n'.join(lines)

    # Code block
    if node_type == 'codeBlock':
        text = _extract_text(content)
        return f'```\n{text}\n```'

    # Fallback: extract text
    return _extract_text(content)


def _extract_text(node: dict) -> str:
    """Recursively extract all text from a ProseMirror node."""
    if isinstance(node, str):
        return node

    if not isinstance(node, dict):
        return ''

    # Direct text node
    if node.get('type') == 'text':
        text = node.get('text', '')
        # Handle marks (bold, italic, etc.)
        marks = node.get('marks', [])
        for mark in marks:
            mark_type = mark.get('type')
            if mark_type == 'bold':
                text = f'**{text}**'
            elif mark_type == 'italic':
                text = f'*{text}*'
            elif mark_type == 'code':
                text = f'`{text}`'
        return text

    # Recurse through children
    content = node.get('content', [])
    texts = [_extract_text(child) for child in content]

    # Join with space for inline, newline for block
    node_type = node.get('type', '')
    if node_type in ['paragraph', 'listItem']:
        return ' '.join(text for text in texts if text)
    else:
        return ''.join(texts)


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool(annotations=ToolAnnotations(title='List Meetings', readOnlyHint=True))
async def list_meetings(
    limit: int = 20, offset: int = 0, search: str | None = None
) -> list[MeetingListItem]:
    """
    List Granola meetings with pagination and optional search.

    Args:
        limit: Maximum number of meetings to return (default 20, max 100)
        offset: Pagination offset (default 0)
        search: Optional search term to filter by title (case-insensitive)

    Returns:
        List of meetings with id, title, date, and metadata
    """
    if limit > 100:
        limit = 100

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v2/get-documents'

    payload = {'limit': limit, 'offset': offset, 'include_last_viewed_panel': False}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = DocumentsResponse(**response.json())

    # Convert to list items
    meetings = []
    for doc in data.docs:
        # Apply search filter
        if search:
            title = doc.title or ''
            if search.lower() not in title.lower():
                continue

        # Count participants
        participant_count = 0
        if doc.people and isinstance(doc.people, dict):
            attendees = doc.people.get('attendees', [])
            participant_count = len(attendees) if isinstance(attendees, list) else 0

        meetings.append(
            MeetingListItem(
                id=doc.id,
                title=doc.title or '(Untitled)',
                created_at=doc.created_at,
                type=doc.type,
                has_notes=bool(doc.notes or doc.notes_markdown),
                participant_count=participant_count,
            )
        )

    return meetings


@mcp.tool(annotations=ToolAnnotations(title='Get Meeting Notes', readOnlyHint=True))
async def get_notes(document_id: str) -> str:
    """
    Get AI-generated notes for a specific meeting in Markdown format.

    Args:
        document_id: Granola document ID

    Returns:
        Markdown-formatted meeting notes
    """
    headers = get_auth_headers()
    url = 'https://api.granola.ai/v2/get-documents'

    # Get document with notes panel
    payload = {'limit': 100, 'offset': 0, 'include_last_viewed_panel': True}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = DocumentsResponse(**response.json())

    # Find the requested document
    doc = None
    for d in data.docs:
        if d.id == document_id:
            doc = d
            break

    if not doc:
        raise ValueError(f'Document {document_id} not found')

    # Try notes_markdown first
    if doc.notes_markdown:
        return doc.notes_markdown

    # Fall back to converting ProseMirror JSON
    if doc.notes:
        return prosemirror_to_markdown(doc.notes)

    return '(No notes available for this meeting)'


@mcp.tool(annotations=ToolAnnotations(title='Search Meetings', readOnlyHint=True))
async def search_meetings(query: str, limit: int = 20) -> list[MeetingListItem]:
    """
    Search meetings by keyword in title.

    Args:
        query: Search keyword (case-insensitive)
        limit: Maximum results to return (default 20)

    Returns:
        List of matching meetings
    """
    # Use list_meetings with search parameter
    return await list_meetings(limit=limit, offset=0, search=query)


@mcp.tool(
    annotations=ToolAnnotations(
        title='Export Meeting Notes', readOnlyHint=False, idempotentHint=False
    )
)
async def export_note(document_id: str, ctx: Context) -> ExportResult:
    """
    Export meeting notes to a temporary Markdown file.

    Files are saved to a temp directory that is cleaned up when the MCP server shuts down.

    Args:
        document_id: Granola document ID
        ctx: MCP context

    Returns:
        ExportResult with file path, title, and size
    """
    logger = DualLogger(ctx)
    await logger.info(f'Exporting notes for document {document_id}')

    # Get the notes
    notes = await get_notes(document_id)

    # Get document title
    headers = get_auth_headers()
    url = 'https://api.granola.ai/v2/get-documents'

    payload = {'limit': 100, 'offset': 0, 'include_last_viewed_panel': False}
    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = DocumentsResponse(**response.json())
    doc = next((d for d in data.docs if d.id == document_id), None)

    if not doc:
        raise ValueError(f'Document {document_id} not found')

    title = doc.title or 'untitled'

    # Create safe filename
    safe_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in title)
    safe_title = safe_title.strip()[:100]  # Limit length
    filename = f'{safe_title}.md'

    # Write to temp directory
    file_path = _export_dir / filename
    file_path.write_text(notes, encoding='utf-8')

    await logger.info(f'Exported to {file_path}')

    return ExportResult(
        path=str(file_path), title=title, size_bytes=len(notes.encode('utf-8'))
    )


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    print('Starting Granola MCP server')
    mcp.run()
