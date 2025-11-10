# FlipTrack Quick Reference

## Keyboard Shortcuts

### Dashboard
- `a` - Add new item
- `e` - Edit selected item
- `d` - Delete selected item (with confirmation)
- `r` - Generate HTML report (selected item)
- `o` - Open report in browser
- `m` - Generate master index
- `Ctrl+R` - Generate ALL reports + master index
- `Ctrl+D` - Delete ALL items (with confirmation)
- `Ctrl+F` - Focus search bar
- `Ctrl+E` - Export to CSV
- `Ctrl+B` - Create full backup
- `q` - Quit

### Item Form
- `Ctrl+S` - Save item
- `Esc` - Cancel and return to dashboard
- `Tab` - Navigate between fields

## Common Tasks

### Add an Item
1. Press `a`
2. Fill in item name (required)
3. Enter prices
4. Optionally scrape or add images
5. Press `Ctrl+S` or click Save

### Search for Items
1. Press `Ctrl+F` or click search box
2. Type item name
3. Results filter in real-time

### Generate Report
**Single Item:**
1. Select item in table
2. Press `r`
3. Press `o` to open in browser

**All Items:**
1. Press `Ctrl+R`
2. Wait for generation to complete
3. Master index opens automatically

### Export Data
- **CSV**: Press `Ctrl+E`
- **Full Backup**: Press `Ctrl+B`
- **Command line**: `python export_utils.py csv`

## Input Validation

### Item Name
- Required
- 2-200 characters
- Any characters allowed

### Prices
- Non-negative numbers
- Max: $1,000,000
- Decimals allowed (e.g., 99.99)

### URLs
- Optional
- Must start with http:// or https://
- Max 2000 characters

### Status
- Draft: Not yet listed
- Listed: Currently for sale
- Sold: Requires final sold price

## File Locations

```
fliptrack/
├── tracker.db           # Your database
├── data/images/         # Product images
│   └── item_[ID]/       # Images per item
└── reports/             # HTML reports
    ├── index.html       # Master index
    └── item_[ID]_report.html
```

## Command Line Tools

```bash
# Export to CSV
python export_utils.py csv output.csv

# Export to JSON
python export_utils.py json backup.json

# Create full backup
python export_utils.py backup my_backup

# Restore from JSON
python export_utils.py restore backup.json

# Run tests
python tests.py
```

## Profit Calculations

**Potential Profit** = Target Price - Purchase Price - Shipping Cost

**Actual Profit** = Final Sold Price - Purchase Price - Shipping Cost

## Tips

1. **Use descriptive names** - Makes searching easier
2. **Add images early** - Harder to find later
3. **Update status regularly** - Keep inventory accurate
4. **Backup before deleting all** - Press `Ctrl+B` before `Ctrl+D`
5. **Use search** - Faster than scrolling
6. **Generate reports before selling** - Professional presentation

## Dangerous Operations

⚠️ **Delete All (Ctrl+D)**
- Deletes ALL items, images, and reports
- Requires confirmation
- CANNOT be undone
- **Always backup first!** (Ctrl+B)

## Troubleshooting

### Can't find an item?
- Use search (Ctrl+F)
- Check status filter dropdown
- Clear search to see all items

### Images not showing?
- Check data/images/item_[ID]/ folder
- Re-generate report (press `r`)
- Try manual image selection

### Database locked?
- Close all instances of the app
- Check for background processes

### Export failed?
- Ensure you have items in database
- Check disk space
- Verify write permissions

## Getting Help

1. Check README.md for detailed docs
2. Check INSTALL.md for setup issues
3. Run `python tests.py` to diagnose
4. Review error messages carefully

---

**Pro Tip**: Press `Ctrl+B` regularly to backup your data!
