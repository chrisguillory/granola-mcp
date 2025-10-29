#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = [
#   "fastmcp>=2.12.5",
#   "httpx",
#   "pydantic>=2.0",
#   "pydevd-pycharm~=241.18034.82",
# ]
# ///
#
# Granola MCP Server
#
# Provides access to Granola meeting notes and data via MCP.
# Architecture: Reads auth tokens from local Granola app data.

from __future__ import annotations

import argparse
import json
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from src.helpers import (
    analyze_markdown_metadata,
    convert_utc_to_local,
    get_auth_headers,
    prosemirror_to_markdown,
)
from src.logging import DualLogger
from src.models import (
    BatchDocumentsResponse,
    DeleteMeetingResult,
    DocumentPanel,
    DocumentsResponse,
    MeetingList,
    MeetingListItem,
    MeetingListsResult,
    NoteDownloadResult,
    PrivateNoteDownloadResult,
    TranscriptDownloadResult,
    TranscriptSegment,
)

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
# MCP Tools
# =============================================================================


@mcp.tool(annotations=ToolAnnotations(title='Search Meetings', readOnlyHint=True))
async def search_meetings(
    query: str | None = None,
    list_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[MeetingListItem]:
    """
    Search Granola meetings with optional query, list filter, and pagination.

    When query is None, returns all meetings (equivalent to listing all meetings).
    When query is provided, filters meetings by title (case-insensitive).
    When list_id is provided, filters to only meetings in that list (server-side).

    Note: list_id uses API terminology ('document' internally) but refers to meeting lists.

    Args:
        query: Optional search term to filter by title (case-insensitive). None returns all meetings.
        list_id: Optional list ID to filter meetings by list (server-side filtering)
        limit: Maximum number of meetings to return (default 20, max 100)
        offset: Pagination offset for retrieving additional results (default 0)

    Returns:
        List of meetings with id, title, date, and metadata

    Possible Improvements (undocumented Granola API parameters):
        The following parameters may be supported by the Granola API but are not yet implemented:
        - filters: Filter by date ranges, meeting status, or custom metadata
        - sort: Specify sorting order (e.g., by date, title, or last modified)
        - types: Filter by document/meeting type
        - tag_ids: Filter meetings by attached tags or labels
        - archived: Include or exclude archived meetings
        - user_id: Restrict results to meetings for specific user(s)
    """
    if limit > 100:
        limit = 100

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v2/get-documents'

    payload = {'limit': limit, 'offset': offset, 'include_last_viewed_panel': False}

    # Add list filter if provided (server-side filtering)
    if list_id:
        payload['list_id'] = list_id

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = DocumentsResponse.model_validate(response.json())

    # Convert to list items
    meetings = []
    for doc in data.docs:
        # Apply search filter if query provided
        if query:
            title = doc.title or ''
            if query.lower() not in title.lower():
                continue

        # Count participants
        participant_count = 0
        if doc.people:
            participant_count = len(doc.people.attendees)

        meetings.append(
            MeetingListItem(
                id=doc.id,
                title=doc.title or '(Untitled)',
                created_at=convert_utc_to_local(doc.created_at),
                type=doc.type,
                has_notes=bool(doc.notes or doc.notes_markdown),
                participant_count=participant_count,
            )
        )

    return meetings


@mcp.tool(
    annotations=ToolAnnotations(
        title='Download Meeting Notes', readOnlyHint=False, idempotentHint=False
    )
)
async def download_note(
    document_id: str, filename: str, ctx: Context
) -> NoteDownloadResult:
    """
    Download meeting notes to a temporary Markdown file with metadata.

    Uses /v1/get-document-panels endpoint to fetch AI-generated notes.
    Returns structural and content metadata in the result.

    Files are saved to a temp directory that is cleaned up when the MCP server shuts down.

    Args:
        document_id: Granola document ID
        filename: Name for file (e.g., "prestel-notes.md")
        ctx: MCP context

    Returns:
        NoteDownloadResult with file path, size, and note metadata
    """
    logger = DualLogger(ctx)
    await logger.info(f'Downloading notes for document {document_id}')

    headers = get_auth_headers()

    # Get document metadata for title and date
    doc_url = 'https://api.granola.ai/v2/get-documents'
    doc_payload = {'id': document_id}
    doc_response = await _http_client.post(doc_url, json=doc_payload, headers=headers)
    doc_response.raise_for_status()
    doc_data = DocumentsResponse.model_validate(doc_response.json())

    # Should return exactly 1 document
    if not doc_data.docs:
        raise ValueError(f'Document {document_id} not found')

    document = doc_data.docs[0]

    # Get panels from API
    panels_url = 'https://api.granola.ai/v1/get-document-panels'
    panels_payload = {'document_id': document_id}

    panels_response = await _http_client.post(
        panels_url, json=panels_payload, headers=headers
    )
    panels_response.raise_for_status()

    # Validate panels
    panels_data = panels_response.json()
    if not panels_data:
        raise ValueError(f'No panels found for document {document_id}')

    panels = [DocumentPanel.model_validate(p) for p in panels_data]

    # Find the summary panel
    summary_panel = None
    for panel in panels:
        if panel.template_slug == 'v2:meeting-summary-consolidated':
            summary_panel = panel
            break

    if not summary_panel:
        # Fall back to first panel
        summary_panel = panels[0]

    # Convert ProseMirror to Markdown
    notes_markdown = prosemirror_to_markdown(summary_panel.content)

    # Format date from created_at
    from datetime import datetime

    # Convert UTC to local time before formatting
    created = datetime.fromisoformat(document.created_at.replace('Z', '+00:00'))
    created_local = created.astimezone()  # Convert to local timezone
    date_str = created_local.strftime('%a, %d %b %y')

    # Build full markdown with title and date header
    title = document.title or '(Untitled)'
    markdown = f'# {title}\n\n{date_str}\n\n{notes_markdown}'

    # Analyze markdown for metadata
    metadata = analyze_markdown_metadata(markdown)

    # Write to temp directory
    file_path = _export_dir / filename
    file_path.write_text(markdown, encoding='utf-8')

    await logger.info(f'Downloaded to {file_path}')

    return NoteDownloadResult(
        path=str(file_path),
        size_bytes=len(markdown.encode('utf-8')),
        section_count=metadata['section_count'],
        bullet_count=metadata['bullet_count'],
        heading_breakdown=metadata['heading_breakdown'],
        word_count=metadata['word_count'],
        panel_title=summary_panel.title,
        template_slug=summary_panel.template_slug,
    )


@mcp.tool(
    annotations=ToolAnnotations(
        title='Download Meeting Transcript', readOnlyHint=False, idempotentHint=False
    )
)
async def download_transcript(
    document_id: str, filename: str, ctx: Context
) -> TranscriptDownloadResult:
    """
    Download meeting transcript to a temporary Markdown file.

    Returns transcript metadata (segment count, duration, speaker breakdown)
    in the result object. The file contains timestamped conversation.

    Files are saved to a temp directory that is cleaned up when the MCP server shuts down.

    Args:
        document_id: Granola document ID
        filename: Name for file (e.g., "prestel-transcript.md")
        ctx: MCP context

    Returns:
        TranscriptDownloadResult with file path, size, and transcript metadata
    """
    logger = DualLogger(ctx)
    await logger.info(f'Downloading transcript for document {document_id}')

    headers = get_auth_headers()

    # Get document metadata for title and date
    doc_url = 'https://api.granola.ai/v2/get-documents'
    doc_payload = {'id': document_id}
    doc_response = await _http_client.post(doc_url, json=doc_payload, headers=headers)
    doc_response.raise_for_status()
    doc_data = DocumentsResponse.model_validate(doc_response.json())

    # Should return exactly 1 document
    if not doc_data.docs:
        raise ValueError(f'Document {document_id} not found')

    document = doc_data.docs[0]

    # Get the transcript
    url = 'https://api.granola.ai/v1/get-document-transcript'
    payload = {'document_id': document_id}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    # Validate with strict Pydantic
    segments = [TranscriptSegment.model_validate(seg) for seg in response.json()]

    if not segments:
        raise ValueError(f'No transcript available for document {document_id}')

    # Calculate metadata
    from datetime import datetime

    total_segments = len(segments)
    microphone_count = sum(1 for s in segments if s.source == 'microphone')
    system_count = sum(1 for s in segments if s.source == 'system')

    # Calculate duration
    start = datetime.fromisoformat(segments[0].start_timestamp.replace('Z', '+00:00'))
    end = datetime.fromisoformat(segments[-1].end_timestamp.replace('Z', '+00:00'))
    duration = end - start

    # Format date (abbreviated month + day)
    # Convert UTC to local time before formatting
    created = datetime.fromisoformat(document.created_at.replace('Z', '+00:00'))
    created_local = created.astimezone()  # Convert to local timezone
    date_str = created_local.strftime('%b %-d').lstrip(
        '0'
    )  # Remove leading zero from day if needed

    # Build markdown header
    title = document.title or '(Untitled)'
    lines = []
    lines.append(f'Meeting Title: {title}')
    lines.append(f'Date: {date_str}')
    lines.append('')
    lines.append('Transcript:')
    lines.append(' ')

    # Build transcript content (no timestamps, simple labels)
    # Combine consecutive segments from the same speaker
    combined_segments = []
    current_label = None
    current_texts = []

    for segment in segments:
        # Map source to Granola's labels
        label = 'Me' if segment.source == 'microphone' else 'Them'

        if label == current_label:
            # Same speaker - accumulate text
            current_texts.append(segment.text)
        else:
            # Different speaker - save previous and start new
            if current_label is not None:
                combined_text = ' '.join(current_texts)
                combined_segments.append(f'{current_label}: {combined_text}')
            current_label = label
            current_texts = [segment.text]

    # Don't forget the last segment
    if current_label is not None:
        combined_text = ' '.join(current_texts)
        combined_segments.append(f'{current_label}: {combined_text}')

    # Add two trailing spaces to all lines except the last
    for i in range(len(combined_segments) - 1):
        combined_segments[i] += '  '
    # Last line gets only one trailing space
    if combined_segments:
        combined_segments[-1] += ' '

    lines.extend(combined_segments)
    transcript_md = '\n'.join(lines)

    # Write to temp directory
    file_path = _export_dir / filename
    file_path.write_text(transcript_md, encoding='utf-8')

    await logger.info(f'Downloaded to {file_path}')

    return TranscriptDownloadResult(
        path=str(file_path),
        size_bytes=len(transcript_md.encode('utf-8')),
        segment_count=total_segments,
        duration_seconds=int(duration.total_seconds()),
        microphone_segments=microphone_count,
        system_segments=system_count,
    )


@mcp.tool(
    annotations=ToolAnnotations(
        title='Download Private Notes', readOnlyHint=False, idempotentHint=False
    )
)
async def download_private_notes(
    document_id: str, filename: str, ctx: Context
) -> PrivateNoteDownloadResult:
    """
    Download user's private notes to a temporary Markdown file.

    Returns private notes written by the user (not AI-generated notes).
    Uses /v2/get-documents endpoint to fetch the notes_markdown field.

    Files are saved to a temp directory that is cleaned up when the MCP server shuts down.

    Args:
        document_id: Granola document ID
        filename: Name for file (e.g., "electrical-private-notes.md")
        ctx: MCP context

    Returns:
        PrivateNoteDownloadResult with file path and metadata
    """
    logger = DualLogger(ctx)
    await logger.info(f'Downloading private notes for document {document_id}')

    headers = get_auth_headers()

    # Get document data
    doc_url = 'https://api.granola.ai/v2/get-documents'
    doc_payload = {'id': document_id}
    doc_response = await _http_client.post(doc_url, json=doc_payload, headers=headers)
    doc_response.raise_for_status()
    doc_data = DocumentsResponse.model_validate(doc_response.json())

    # Should return exactly 1 document
    if not doc_data.docs:
        raise ValueError(f'Document {document_id} not found')

    document = doc_data.docs[0]

    # Check if private notes exist
    if not document.notes_markdown:
        raise ValueError(f'No private notes available for document {document_id}')

    # Format date from created_at
    from datetime import datetime

    # Convert UTC to local time before formatting
    created = datetime.fromisoformat(document.created_at.replace('Z', '+00:00'))
    created_local = created.astimezone()  # Convert to local timezone
    date_str = created_local.strftime('%a, %d %b %y')

    # Build full markdown with title and date header
    title = document.title or '(Untitled)'
    markdown = f'# {title}\n\n{date_str}\n\n{document.notes_markdown}'

    # Calculate metadata
    lines = markdown.split('\n')
    line_count = len(lines)
    words = markdown.split()
    word_count = len([w for w in words if w.strip()])

    # Write to temp directory
    file_path = _export_dir / filename
    file_path.write_text(markdown, encoding='utf-8')

    await logger.info(f'Downloaded to {file_path}')

    return PrivateNoteDownloadResult(
        path=str(file_path),
        size_bytes=len(markdown.encode('utf-8')),
        word_count=word_count,
        line_count=line_count,
    )


@mcp.tool(annotations=ToolAnnotations(title='Get Meeting Lists', readOnlyHint=True))
async def get_meeting_lists(ctx: Context) -> MeetingListsResult:
    """
    Get all meeting lists/collections with their document IDs.

    Returns user's meeting lists (collections) with metadata including
    which meetings belong to each list.

    Args:
        ctx: MCP context

    Returns:
        MeetingListsResult with lists and total count
    """
    logger = DualLogger(ctx)
    await logger.info('Fetching meeting lists')

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v1/get-document-lists-metadata'
    payload = {'include_document_ids': True, 'include_only_joined_lists': False}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    lists_data = data.get('lists', {})

    # Convert dictionary of lists to list of MeetingList objects
    meeting_lists = []
    for list_id, list_info in lists_data.items():
        doc_ids = list_info.get('document_ids', [])
        meeting_list = MeetingList(
            id=list_id,
            title=list_info.get('title', ''),
            description=list_info.get('description'),
            visibility=list_info.get('visibility', ''),
            document_ids=doc_ids,
            document_count=len(doc_ids),
            created_at=convert_utc_to_local(list_info.get('created_at', '')),
            updated_at=convert_utc_to_local(list_info.get('updated_at', '')),
        )
        meeting_lists.append(meeting_list)

    await logger.info(f'Found {len(meeting_lists)} meeting lists')

    return MeetingListsResult(lists=meeting_lists, total_count=len(meeting_lists))


@mcp.tool(annotations=ToolAnnotations(title='Get Meetings', readOnlyHint=True))
async def get_meetings(document_ids: list[str], ctx: Context) -> list[MeetingListItem]:
    """
    Fetch multiple meetings by their document IDs (batch retrieval).

    Use this to efficiently fetch multiple specific meetings at once,
    such as all meetings in a list or a set of related meetings.

    Note: Parameter is 'document_ids' (API terminology) even though
    the tool is named 'get_meetings' (user-friendly terminology).

    Args:
        document_ids: List of Granola document IDs to fetch
        ctx: MCP context

    Returns:
        List of meetings with metadata
    """
    logger = DualLogger(ctx)
    await logger.info(f'Fetching {len(document_ids)} meetings')

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v1/get-documents-batch'
    payload = {'document_ids': document_ids}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = BatchDocumentsResponse.model_validate(response.json())

    # Convert to list items
    meetings = []
    for doc in data.docs:
        # Count participants
        participant_count = 0
        if doc.people:
            participant_count = len(doc.people.attendees)

        meetings.append(
            MeetingListItem(
                id=doc.id,
                title=doc.title or '(Untitled)',
                created_at=convert_utc_to_local(doc.created_at),
                type=doc.type,
                has_notes=bool(doc.notes or doc.notes_markdown),
                participant_count=participant_count,
            )
        )

    await logger.info(f'Fetched {len(meetings)} meetings')

    return meetings


@mcp.tool(
    annotations=ToolAnnotations(
        title='Delete Meeting', readOnlyHint=False, idempotentHint=True
    )
)
async def delete_meeting(document_id: str, ctx: Context) -> DeleteMeetingResult:
    """
    Delete a meeting by setting its deleted_at timestamp.

    Deleted meetings:
    - Don't appear in search results
    - Appear in the 'deleted' array of API responses
    - Can be fully restored using undelete_meeting()

    Args:
        document_id: Granola document ID to delete
        ctx: MCP context

    Returns:
        DeleteMeetingResult with success status and document ID
    """
    logger = DualLogger(ctx)
    await logger.info(f'Deleting meeting {document_id}')

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v1/update-document'

    # Generate current ISO timestamp
    from datetime import datetime, timezone

    deleted_at = datetime.now(timezone.utc).isoformat()

    payload = {'id': document_id, 'deleted_at': deleted_at}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    await logger.info(f'Successfully deleted meeting {document_id}')

    return DeleteMeetingResult(success=True, document_id=document_id)


@mcp.tool(
    annotations=ToolAnnotations(
        title='Undelete Meeting', readOnlyHint=False, idempotentHint=True
    )
)
async def undelete_meeting(document_id: str, ctx: Context) -> DeleteMeetingResult:
    """
    Restore a deleted meeting by clearing its deleted_at timestamp.

    Undeleted meetings are fully restored and will:
    - Appear in search results again
    - Be accessible through all normal endpoints
    - Retain all their original data (notes, transcripts, etc.)

    Args:
        document_id: Granola document ID to restore
        ctx: MCP context

    Returns:
        DeleteMeetingResult with success status and document ID
    """
    logger = DualLogger(ctx)
    await logger.info(f'Undeleting meeting {document_id}')

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v1/update-document'

    payload = {'id': document_id, 'deleted_at': None}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    await logger.info(f'Successfully undeleted meeting {document_id}')

    return DeleteMeetingResult(success=True, document_id=document_id)


@mcp.tool(annotations=ToolAnnotations(title='List Deleted Meetings', readOnlyHint=True))
async def list_deleted_meetings(ctx: Context) -> list[str]:
    """
    List all deleted meeting document IDs.

    Returns the IDs of meetings that have been deleted. These IDs can be used
    with undelete_meeting() to restore meetings.

    Deleted meetings:
    - Don't appear in normal search results
    - Are tracked in the 'deleted' array of the API response
    - Can be fully restored using their document ID

    Args:
        ctx: MCP context

    Returns:
        List of deleted document IDs
    """
    logger = DualLogger(ctx)
    await logger.info('Fetching deleted meeting IDs')

    headers = get_auth_headers()
    url = 'https://api.granola.ai/v2/get-documents'

    # Fetch with high limit to get all deleted IDs
    payload = {'limit': 100, 'offset': 0, 'include_last_viewed_panel': False}

    response = await _http_client.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = DocumentsResponse.model_validate(response.json())

    await logger.info(f'Found {len(data.deleted)} deleted meetings')

    return data.deleted


# =============================================================================
# Main Entry Point
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Granola MCP Server')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable PyCharm remote debugging',
    )
    parser.add_argument(
        '--debug-host',
        default=os.environ.get('DEBUG_HOST', 'host.docker.internal'),
        help='Debug host (default: host.docker.internal or $DEBUG_HOST)',
    )
    parser.add_argument(
        '--debug-port',
        type=int,
        default=int(os.environ.get('DEBUG_PORT', '5678')),
        help='Debug port (default: 5678 or $DEBUG_PORT)',
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the Granola MCP server."""
    args = parse_args()

    if args.debug:
        print(f'Enabling PyCharm remote debugging: {args.debug_host}:{args.debug_port}')
        import pydevd_pycharm

        pydevd_pycharm.settrace(
            args.debug_host,
            port=args.debug_port,
            stdoutToServer=True,
            stderrToServer=True,
            suspend=False,
        )
        print('Connected to PyCharm debugger')

    print('Starting Granola MCP server')
    mcp.run()


if __name__ == '__main__':
    main()
