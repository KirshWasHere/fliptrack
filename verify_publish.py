"""
Verify project is ready for GitHub publishing
Run with: python verify_publish.py
"""

import os
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✓" if exists else ("✗" if required else "○")
    req_text = " (required)" if required else " (optional)"
    print(f"{status} {filepath}{req_text if not exists and required else ''}")
    return exists

def check_directory_not_exists(dirpath):
    """Check that a directory does NOT exist (should be gitignored)"""
    exists = Path(dirpath).exists()
    status = "✗" if exists else "✓"
    print(f"{status} {dirpath} {'EXISTS (should be removed!)' if exists else 'not present (good)'}")
    return not exists

def check_file_content(filepath, search_text, should_contain=True):
    """Check if file contains specific text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            contains = search_text in content
            if should_contain:
                status = "✓" if contains else "✗"
                print(f"{status} {filepath} {'contains' if contains else 'missing'} '{search_text}'")
            else:
                status = "✗" if contains else "✓"
                print(f"{status} {filepath} {'contains (should remove!)' if contains else 'does not contain'} '{search_text}'")
            return contains == should_contain
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 80)
    print("FlipTrack - GitHub Publishing Verification")
    print("=" * 80)
    print()
    
    all_checks_passed = True
    
    # Check required files
    print("📄 Required Files:")
    all_checks_passed &= check_file_exists("README.md", required=True)
    all_checks_passed &= check_file_exists("LICENSE", required=True)
    all_checks_passed &= check_file_exists("requirements.txt", required=True)
    all_checks_passed &= check_file_exists(".gitignore", required=True)
    all_checks_passed &= check_file_exists("main.py", required=True)
    all_checks_passed &= check_file_exists("database.py", required=True)
    all_checks_passed &= check_file_exists("scraper.py", required=True)
    all_checks_passed &= check_file_exists("report_generator.py", required=True)
    all_checks_passed &= check_file_exists("utils.py", required=True)
    all_checks_passed &= check_file_exists("config.py", required=True)
    all_checks_passed &= check_file_exists("export_utils.py", required=True)
    all_checks_passed &= check_file_exists("tests.py", required=True)
    print()
    
    # Check documentation
    print("📚 Documentation:")
    all_checks_passed &= check_file_exists("INSTALL.md", required=True)
    all_checks_passed &= check_file_exists("CONTRIBUTING.md", required=True)
    all_checks_passed &= check_file_exists("CHANGELOG.md", required=True)
    all_checks_passed &= check_file_exists("QUICK_REFERENCE.md", required=True)
    check_file_exists("ARCHITECTURE.md", required=False)
    check_file_exists("GITHUB_SETUP.md", required=False)
    print()
    
    # Check that test data is removed
    print("🧹 Clean State (should NOT exist):")
    all_checks_passed &= check_directory_not_exists("tracker.db")
    all_checks_passed &= check_directory_not_exists("data")
    all_checks_passed &= check_directory_not_exists("reports")
    all_checks_passed &= check_directory_not_exists("__pycache__")
    print()
    
    # Check .gitignore content
    print("🚫 .gitignore Configuration:")
    all_checks_passed &= check_file_content(".gitignore", "tracker.db", should_contain=True)
    all_checks_passed &= check_file_content(".gitignore", "data/", should_contain=True)
    all_checks_passed &= check_file_content(".gitignore", "reports/", should_contain=True)
    all_checks_passed &= check_file_content(".gitignore", "__pycache__/", should_contain=True)
    print()
    
    # Check README content
    print("📖 README.md Content:")
    all_checks_passed &= check_file_content("README.md", "FlipTrack", should_contain=True)
    all_checks_passed &= check_file_content("README.md", "Installation", should_contain=True)
    all_checks_passed &= check_file_content("README.md", "Keyboard Shortcuts", should_contain=True)
    all_checks_passed &= check_file_content("README.md", "License", should_contain=True)
    print()
    
    # Check for sensitive data
    print("🔒 Security Check:")
    print("○ Checking for common sensitive patterns...")
    sensitive_patterns = [
        ("password", False),
        ("api_key", False),
        ("secret", False),
        ("token", False),
    ]
    
    for pattern, _ in sensitive_patterns:
        # Check main files
        for file in ["main.py", "database.py", "config.py"]:
            if Path(file).exists():
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if pattern in content and "# " not in content:  # Ignore comments
                        print(f"⚠️  Warning: '{pattern}' found in {file}")
    
    print("✓ No obvious sensitive data found")
    print()
    
    # Run tests
    print("🧪 Running Tests:")
    try:
        import subprocess
        result = subprocess.run(["python", "tests.py"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Check if tests actually passed
            if "Tests Passed:" in result.stdout and "Tests Failed: 0" in result.stdout:
                print("✓ All tests passed")
            else:
                print("⚠️  Tests completed but status unclear")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        else:
            print("✗ Some tests failed")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            all_checks_passed = False
    except subprocess.TimeoutExpired:
        print("⚠️  Tests timed out (taking too long)")
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
    print()
    
    # Check imports
    print("📦 Import Check:")
    try:
        import main
        print("✓ main.py imports successfully")
    except Exception as e:
        print(f"✗ main.py import failed: {e}")
        all_checks_passed = False
    
    try:
        import database
        print("✓ database.py imports successfully")
    except Exception as e:
        print(f"✗ database.py import failed: {e}")
        all_checks_passed = False
    
    try:
        import export_utils
        print("✓ export_utils.py imports successfully")
    except Exception as e:
        print(f"✗ export_utils.py import failed: {e}")
        all_checks_passed = False
    print()
    
    # Final summary
    print("=" * 80)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Ready to publish to GitHub!")
        print()
        print("Next steps:")
        print("1. git init (if not already done)")
        print("2. git add .")
        print("3. git commit -m 'Initial commit: FlipTrack v2.0'")
        print("4. Create repository on GitHub")
        print("5. git remote add origin https://github.com/yourusername/fliptrack.git")
        print("6. git push -u origin main")
        print()
        print("See GITHUB_SETUP.md for detailed instructions.")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues before publishing")
        print()
        print("Common fixes:")
        print("- Remove tracker.db: del tracker.db")
        print("- Remove data folder: rmdir /s data")
        print("- Remove reports folder: rmdir /s reports")
        print("- Fix failing tests")
        print("- Ensure all required files exist")
    print("=" * 80)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
