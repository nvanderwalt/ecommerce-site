@echo off
echo Adding all changes to git...
git add -A

echo Creating commit...
git commit -m "Fix cart button colors and improve functionality

- Fixed cart button colors (green for success, yellow for already in cart)
- Removed duplicate JavaScript handlers from templates
- Added proper CSS overrides for Bootstrap button states
- Updated Facebook Business Page links
- Enhanced README with SEO implementation section
- Fixed security settings for development
- Improved cart functionality with proper error handling"

echo Commit completed!
pause
