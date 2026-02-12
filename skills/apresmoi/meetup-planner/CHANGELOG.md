# Changelog

All notable changes to the Meetup Planner skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-12

### Added
- Initial release of meetup-planner skill
- Automated event discovery using Brave Search API
- Event detail extraction using Firecrawl API
- Conversational preference collection system
- Daily automated search scheduling via cron
- Local event tracking database (JSON-based)
- Smart reminder system (24h and 2h before events)
- Support for multiple event platforms (Eventbrite, Meetup.com, Luma, etc.)
- Privacy-first local data storage
- Interactive commands for managing preferences and events
- Automatic skill dependency installation (firecrawl/cli, brave-search)
- Comprehensive error handling and fallback mechanisms
- Event status tracking (new, interested, registered, past)
- Post-event cleanup and feedback collection

### Dependencies
- firecrawl/cli - For web scraping and content extraction
- brave-search - For event discovery across the web

### Requirements
- BRAVE_API_KEY environment variable
- FIRECRAWL_API_KEY environment variable
- Cron or equivalent scheduler

### Security
- No hardcoded credentials
- All sensitive data stored as environment variables
- Local-only data storage
- Explicit permission declarations for filesystem, network, and cron access

---

## Future Roadmap

### [1.1.0] - Planned
- Calendar integration (Google Calendar, iCal)
- Email notifications for reminders
- Event recommendation engine based on past attendance
- Multi-user support for teams
- Web UI for preference management
- Export events to various formats (CSV, ICS)

### [1.2.0] - Planned
- Machine learning for better event matching
- Social features (share events with friends)
- Event RSVP tracking integration
- Conflict detection for overlapping events
- Travel time estimation for in-person events

### [2.0.0] - Future
- Mobile app integration
- Real-time event updates
- Community event sharing marketplace
- Integration with more event platforms
- Advanced filtering and sorting options
