# Contributing to FlipTrack

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/fliptrack.git
   cd fliptrack
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests to verify setup**
   ```bash
   python tests.py
   ```

## Project Structure

```
fliptrack/
├── main.py              # TUI application (Textual)
├── database.py          # Database operations (SQLite)
├── scraper.py           # Image scraping (BeautifulSoup + httpx)
├── report_generator.py  # HTML report generation (Jinja2)
├── utils.py             # Utility functions
├── config.py            # Configuration settings
├── export_utils.py      # Export and backup utilities
├── tests.py             # Test suite
└── requirements.txt     # Dependencies
```

## Code Style

- Follow PEP 8 style guide
- Use type hints where applicable
- Add docstrings to all functions
- Keep functions focused and small
- Use descriptive variable names

### Example

```python
def calculate_profit(purchase: float, shipping: float, selling: float) -> float:
    """Calculate profit from a sale
    
    Args:
        purchase: Purchase price
        shipping: Shipping cost
        selling: Selling price
        
    Returns:
        Profit amount (can be negative)
    """
    return selling - purchase - shipping
```

## Testing

### Running Tests

```bash
python tests.py
```

### Writing Tests

Add tests to `tests.py` using the `@test` decorator:

```python
@test("Your test name")
def test_your_feature():
    """Test description"""
    # Your test code
    assert result == expected, "Error message"
```

### Test Coverage

Tests should cover:
- Happy path (normal usage)
- Edge cases (empty inputs, max values)
- Error cases (invalid inputs)
- Database operations
- Validation logic

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, documented code
- Follow existing patterns
- Add tests for new features
- Update documentation

### 3. Test Your Changes

```bash
# Run test suite
python tests.py

# Test the app manually
python main.py
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add feature: description of your changes"
```

Use clear commit messages:
- `Add feature: CSV export with custom columns`
- `Fix bug: Database lock on concurrent access`
- `Improve: Image optimization performance`
- `Update docs: Add troubleshooting section`

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Why the change is needed
- How to test it
- Screenshots (if UI changes)

## Areas for Contribution

### High Priority

1. **Performance Optimization**
   - Async image downloads
   - Database query optimization
   - Image caching

2. **UI Enhancements**
   - Bulk operations (select multiple items)
   - Keyboard shortcuts customization
   - Color themes

3. **Export Features**
   - PDF report generation
   - Excel export with formatting
   - Email reports

### Medium Priority

4. **Analytics**
   - Profit charts and graphs
   - Sales trends
   - Category performance

5. **Integration**
   - eBay API integration
   - StockX price checking
   - Barcode scanning

6. **Mobile**
   - Mobile-friendly HTML reports
   - Companion mobile app
   - QR code scanning

### Low Priority

7. **Advanced Features**
   - Multi-user support
   - Cloud sync
   - Automated listing
   - Price alerts

## Bug Reports

When reporting bugs, include:

1. **Description**: What happened?
2. **Expected behavior**: What should happen?
3. **Steps to reproduce**: How to trigger the bug?
4. **Environment**: OS, Python version
5. **Error messages**: Full error output
6. **Screenshots**: If applicable

### Example Bug Report

```
**Bug**: CSV export fails with special characters in item name

**Expected**: Export should handle all characters

**Steps to reproduce**:
1. Add item with name "Test™ Item®"
2. Press Ctrl+E to export
3. Error appears

**Environment**: Windows 11, Python 3.11

**Error**:
UnicodeEncodeError: 'charmap' codec can't encode character...
```

## Feature Requests

When requesting features, include:

1. **Use case**: Why is this needed?
2. **Description**: What should it do?
3. **Examples**: How would it work?
4. **Alternatives**: Other solutions you've considered

## Code Review Process

Pull requests will be reviewed for:

1. **Functionality**: Does it work as intended?
2. **Tests**: Are there tests? Do they pass?
3. **Code quality**: Is it clean and maintainable?
4. **Documentation**: Is it documented?
5. **Compatibility**: Does it break existing features?

## Development Tips

### Database Changes

If you modify the database schema:

1. Update `database.py`
2. Add migration logic for existing databases
3. Update tests
4. Document the change

### UI Changes

If you modify the TUI:

1. Test on different terminal sizes
2. Ensure keyboard navigation works
3. Update keyboard shortcuts documentation
4. Test on Windows, macOS, and Linux if possible

### Adding Dependencies

If you need a new package:

1. Add to `requirements.txt`
2. Justify why it's needed
3. Check license compatibility (MIT preferred)
4. Update INSTALL.md if needed

## Questions?

- Check existing issues and pull requests
- Review the README.md and documentation
- Ask in pull request comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to FlipTrack!** 🎉
