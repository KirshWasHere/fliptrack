# Changelog

All notable changes to FlipTrack will be documented in this file.

## [2.0.0] - 2024-11-10

### Added
- **Search functionality**: Real-time search by item name
- **Status filtering**: Filter items by Draft/Listed/Sold status
- **Input validation**: Comprehensive validation for all form fields
  - Item names (2-200 characters)
  - Prices (non-negative, max $1M)
  - URLs (must be http/https)
- **Confirmation dialogs**: Delete confirmation to prevent accidents
- **CSV export**: Export all items to CSV (Ctrl+E)
- **Full backup system**: One-click backup of database, images, and reports (Ctrl+B)
- **JSON export/import**: Backup and restore functionality
- **Image optimization**: Automatic compression of downloaded images
- **Error handling**: Comprehensive error handling throughout the app
- **Test suite**: 12 automated tests covering core functionality
- **Export utilities CLI**: Command-line tools for export and backup

### Improved
- **Database operations**: Added error handling and search/filter support
- **Report generation**: Better error handling and validation
- **Image management**: Images are now optimized on download
- **Form validation**: Real-time validation with helpful error messages
- **Dashboard**: Shows filtered item count vs total
- **Documentation**: Consolidated from 20+ files to 3 essential docs
- **Code quality**: Added type hints and better error messages

### Fixed
- Database operations now properly handle errors
- Image paths are cleaned up if database save fails
- Reports handle missing images gracefully
- QR code generation errors don't crash report generation
- Long item names are truncated in table view

### Changed
- Deleted 20+ redundant documentation files
- Consolidated README with all essential information
- Simplified INSTALL.md with clear troubleshooting
- Updated keyboard shortcuts (added Ctrl+F, Ctrl+E, Ctrl+B)

### Technical Improvements
- Better separation of concerns
- Consistent error handling patterns
- Input sanitization and validation
- Resource cleanup on errors
- Comprehensive test coverage

## [1.0.0] - Initial Release

### Features
- Terminal-based UI with Textual
- Item management (add, edit, delete)
- Profit calculations
- Image scraping from multiple sources
- HTML report generation
- Master index generation
- SQLite database
- QR code generation
- Status tracking (Draft/Listed/Sold)

---

**Note**: Version 2.0.0 represents a major stability and usability upgrade with focus on data validation, error handling, and user experience improvements.
