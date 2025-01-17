#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if timesheet script exists
if [ ! -f "timesheet.py" ]; then
    echo -e "${RED}Error: timesheet.py not found in current directory${NC}"
    exit 1
fi

# Make the script executable
chmod +x timesheet.py

# Move the script to bin directory
cp timesheet.py "/bin/timesheet"

# Verify installation
if [ -x "/bin/timesheet" ]; then
    echo -e "${GREEN}Installation successful!${NC}"
    echo -e "${GREEN}You can now run 'timesheet' from anywhere${NC}"
else
    echo -e "${RED}Installation failed${NC}"
    exit 1
fi
