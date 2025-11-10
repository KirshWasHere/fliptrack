# Test Data Guide

Your FlipTrack database now has **26 test items** with **15 items having images**.

## What You Can Test

### 1. Basic Navigation
```bash
python main.py
```
- Browse through 26 items in the table
- Use arrow keys to navigate
- See different statuses (Draft, Listed, Sold)

### 2. Search & Filter
- Press `Ctrl+F` to focus search
- Try searching: "Nike", "iPhone", "Harry Potter"
- Use status dropdown to filter by Draft/Listed/Sold
- See real-time results

### 3. Generate Single Report
- Select any item with images (15 items have them)
- Press `r` to generate report
- Press `o` to open in browser
- See dark mode styling with images

### 4. Generate ALL Reports (NEW!)
- Press `Ctrl+R` to generate reports for all 26 items
- Watch as it processes all items
- Master index opens automatically
- All reports saved to `reports/` folder

### 5. Master Index
- Press `m` to generate master index
- Opens automatically in browser
- See all 26 items in a table
- Click "View" links to see individual reports

### 6. Export Features
- Press `Ctrl+E` to export to CSV
- Press `Ctrl+B` to create full backup
- Check the generated files

### 7. Edit & Delete
- Select an item
- Press `e` to edit
- Try changing prices, status
- Press `d` to delete (with confirmation)

### 8. Add New Item
- Press `a` to add new item
- Fill in the form
- Test validation (try invalid prices, empty name)
- Save and see it in the table

### 9. Delete All Items (NEW!)
- Press `Ctrl+B` to backup first (recommended)
- Press `Ctrl+D` to delete all
- Read the warning carefully
- Confirm deletion
- All items, images, and reports are removed
- Perfect for clearing test data

## Test Scenarios

### Scenario 1: Batch Report Generation
1. Press `Ctrl+R`
2. Wait for "Generated X reports + master index!"
3. Master index opens automatically
4. Click through different item reports
5. Notice dark mode styling

### Scenario 2: Search & Report
1. Press `Ctrl+F`
2. Search "Nike"
3. Select a Nike item
4. Press `r` to generate report
5. Press `o` to view

### Scenario 3: Filter & Export
1. Use status dropdown → select "Sold"
2. See only sold items (8 items)
3. Press `Ctrl+E` to export
4. Open CSV to see filtered data

### Scenario 4: Full Workflow
1. Add a new item (`a`)
2. Generate its report (`r`)
3. Generate master index (`m`)
4. Export to CSV (`Ctrl+E`)
5. Create backup (`Ctrl+B`)

## Test Data Summary

**Total Items**: 26
- Draft: 14 items
- Listed: 4 items
- Sold: 8 items

**Categories**:
- Books: 13 items
- Electronics: 3 items
- General: 7 items
- Sneakers: 3 items

**Items with Images**: 15 items
**Total Potential Profit**: ~$1,197
**Total Actual Profit**: ~$572

## Regenerate Test Data

### Method 1: Using Delete All (Recommended)
```bash
# Run the app
python main.py

# Press Ctrl+D to delete all items
# Confirm the deletion
# Press 'q' to quit

# Generate new items
python generate_test_data.py 30

# Add images to some items
python add_test_images.py 20
```

### Method 2: Manual Database Delete
```bash
# Delete current database
del tracker.db

# Generate new items
python generate_test_data.py 30

# Add images to some items
python add_test_images.py 20
```

## Tips

1. **Test the dark mode reports** - They look great!
2. **Try Ctrl+R** - Generates all reports at once
3. **Use search** - Much faster than scrolling
4. **Test validation** - Try entering invalid data
5. **Check exports** - CSV and backup features work great

## What to Look For

✓ Dark mode reports look professional
✓ Search is instant and accurate
✓ Filters work correctly
✓ Validation prevents bad data
✓ Confirmation dialogs prevent accidents
✓ All reports generate successfully
✓ Master index links work
✓ Export features create proper files
✓ Images display correctly in reports
✓ QR codes are scannable (if URLs present)

## Known Test Data Quirks

- Some items have negative profits (intentional for testing)
- Some items don't have URLs (testing optional fields)
- Images are placeholders (colored rectangles with text)
- Some duplicate item names (testing search)

---

**Ready to test?** Run `python main.py` and start exploring!
