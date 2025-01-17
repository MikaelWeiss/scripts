#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if timesheet script exists
if [ ! -f "timesheet" ]; then
    echo -e "${RED}Error: timesheet not found in current directory${NC}"
    exit 1
fi

# Make the script executable
chmod +x timesheet

# Move the script to bin directory
ln timesheet "/bin/timesheet"

# Verify installation
if [ -x "/bin/timesheet" ]; then
    echo -e "${GREEN}Installation successful!${NC}"
    echo -e "${GREEN}You can now run 'timesheet' from anywhere${NC}"
else
    echo -e "${RED}Installation failed${NC}"
    exit 1
fi
