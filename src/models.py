"""Pydantic models for Granola API responses with strict validation.

Generated from actual API response analysis of 40 documents.
"""

import pydantic


class BaseModel(pydantic.BaseModel):
    """Base model with strict validation - no extra fields, all fields required unless Optional."""

    model_config = pydantic.ConfigDict(extra='forbid', strict=True)


# Nested models for structured data


class PersonName(BaseModel):
    fullName: str


class PersonDetails(BaseModel):
    name: PersonName
    avatar: str


class CompanyDetails(BaseModel):
    name: str | None = None  # Can have name field


class PersonInfo(BaseModel):
    person: PersonDetails
    company: CompanyDetails


class Creator(BaseModel):
    name: str
    email: str
    details: PersonInfo


class Conferencing(BaseModel):
    url: str | None
    type: str | None
    title: str


class People(BaseModel):
    title: str
    creator: Creator
    attendees: list
    created_at: str
    sharing_link_visibility: str | None = None
    url: str | None = None
    conferencing: Conferencing | None = None


class GoogleCalendarTime(BaseModel):
    dateTime: str
    timeZone: str


class GoogleCalendarCreator(BaseModel):
    self: bool | None = None
    email: str
    displayName: str | None = None


class GoogleCalendarOrganizer(BaseModel):
    self: bool | None = None
    email: str
    displayName: str | None = None


class GoogleCalendarReminders(BaseModel):
    useDefault: bool


class GoogleCalendarEvent(BaseModel):
    id: str
    end: GoogleCalendarTime
    etag: str
    kind: str
    start: GoogleCalendarTime
    status: str
    created: str
    creator: GoogleCalendarCreator | None = None
    iCalUID: str
    summary: str
    updated: str
    htmlLink: str
    sequence: int | None = None
    eventType: str
    organizer: GoogleCalendarOrganizer
    reminders: GoogleCalendarReminders | None = None
    calendarId: str
    # Optional fields
    primaryCalendar: bool | None = None
    location: str | None = None
    description: str | None = None
    guestsCanInviteOthers: bool | None = None
    attendees: list | None = None
    privateCopy: bool | None = None
    hangoutLink: str | None = None
    conferenceData: dict | None = None
    guestsCanModify: bool | None = None
    visibility: str | None = None
    attachments: list | None = None
    recurringEventId: str | None = None
    originalStartTime: dict | None = None
    guestsCanSeeOtherGuests: bool | None = None
    extendedProperties: dict | None = None


class ProseMirrorAttrs(BaseModel):
    """Attrs for ProseMirror nodes. Only id, timestamp, and timestamp-to appear in actual data."""

    id: str
    timestamp: str | None = None
    timestamp_to: str | None = pydantic.Field(default=None, alias='timestamp-to')


class ProseMirrorNode(BaseModel):
    type: str
    attrs: ProseMirrorAttrs | None = None
    content: list | None = None  # Can be list[ProseMirrorNode] but keeping flexible


class Notes(BaseModel):
    type: str
    content: list[ProseMirrorNode]


class LastViewedPanel(BaseModel):
    """Panel data returned when include_last_viewed_panel=True."""

    document_id: str
    id: str
    created_at: str
    title: str
    content: dict | str  # Can be dict (ProseMirror) or str (HTML)
    deleted_at: None = None
    template_slug: str
    last_viewed_at: str
    updated_at: str
    content_updated_at: str
    affinity_note_id: None = None
    original_content: str | None = None
    suggested_questions: None = None
    generated_lines: list | None = None


# Main document model


class GranolaDocument(BaseModel):
    """Strict model for Granola document with fail-fast validation."""

    # Required fields (always present and not null)
    id: str
    created_at: str
    notes: Notes  # Often empty ProseMirror JSON for newer meetings
    user_id: str
    notes_plain: str
    transcribe: bool
    updated_at: str
    public: bool
    meeting_end_count: int
    has_shareable_link: bool
    creation_source: str
    subscription_plan_id: str
    privacy_mode_enabled: bool
    workspace_id: str | None
    sharing_link_visibility: str

    # Nullable fields (can be None)
    people: People | None  # Can be None for some meetings
    title: str | None
    cloned_from: str | None = None
    google_calendar_event: GoogleCalendarEvent | None
    deleted_at: str | None = None
    type: str | None
    overview: str | None = None
    chapters: None = None  # Always null
    notes_markdown: (
        str | None
    )  # Often empty/None for newer meetings - use panels endpoint instead
    selected_template: None = None  # Always null
    valid_meeting: bool | None
    summary: None = None  # Always null
    affinity_note_id: None = None  # Always null
    show_private_notes: bool | None
    attachments: list | None
    hubspot_note_url: None = None  # Always null
    status: str | None = None
    external_transcription_id: str | None = None
    audio_file_handle: str | None = None
    visibility: None = None  # Always null
    notification_config: None = None  # Always null
    transcript_deleted_at: None = None  # Always null
    metadata: None = None  # Always null
    attio_shared_at: None = None  # Always null
    last_viewed_panel: LastViewedPanel | None = (
        None  # Only present when include_last_viewed_panel=True
    )


class DocumentsResponse(BaseModel):
    """Response from get-documents API."""

    docs: list[GranolaDocument]
    deleted: list[str]


class BatchDocumentsResponse(BaseModel):
    """Response from get-documents-batch API (no deleted array)."""

    docs: list[GranolaDocument]


# Simplified models for tool responses


class MeetingListItem(BaseModel):
    """Simplified meeting info for list views."""

    id: str
    title: str
    created_at: str
    type: str | None
    has_notes: bool
    participant_count: int


class DownloadResult(BaseModel):
    """Result from download operation."""

    path: str
    size_bytes: int


class TranscriptSegment(BaseModel):
    """Single segment of meeting transcript."""

    document_id: str
    id: str
    start_timestamp: str  # ISO 8601
    end_timestamp: str  # ISO 8601
    text: str
    source: str  # "microphone" or "system"
    is_final: bool


class TranscriptDownloadResult(BaseModel):
    """Result from transcript download operation with metadata."""

    path: str
    size_bytes: int
    segment_count: int
    duration_seconds: int
    microphone_segments: int
    system_segments: int


class DocumentPanel(BaseModel):
    """Panel from get-document-panels endpoint."""

    id: str
    created_at: str
    title: str
    document_id: str
    content: dict  # ProseMirror JSON
    template_slug: str | None = None
    deleted_at: str | None = None
    last_viewed_at: str | None = None
    updated_at: str
    content_updated_at: str | None = None
    affinity_note_id: str | None = None
    original_content: dict | str | None = None  # Can be dict or HTML string
    suggested_questions: list | None = None
    generated_lines: list | None = None
    user_feedback: dict | None = None


class NoteDownloadResult(BaseModel):
    """Result from note download with structural metadata."""

    path: str
    size_bytes: int
    # Structural metrics
    section_count: int  # Number of H3 headings
    bullet_count: int  # Total bullet points
    heading_breakdown: dict  # {"h1": 1, "h2": 0, "h3": 5}
    # Content metrics
    word_count: int
    # Panel metadata
    panel_title: str
    template_slug: str | None


class PrivateNoteDownloadResult(BaseModel):
    """Result from private note download with metadata."""

    path: str
    size_bytes: int
    word_count: int
    line_count: int


class MeetingList(BaseModel):
    """Meeting list/collection with document IDs."""

    id: str
    title: str
    description: str | None
    visibility: str
    document_ids: list[str]  # API uses 'document' terminology
    document_count: int
    created_at: str
    updated_at: str


class MeetingListsResult(BaseModel):
    """Result from getting meeting lists."""

    lists: list[MeetingList]
    total_count: int


class DeleteMeetingResult(BaseModel):
    """Result from delete/undelete meeting operation."""

    success: bool
    document_id: str
