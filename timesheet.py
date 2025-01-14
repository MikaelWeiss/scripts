#!/usr/bin/env python3
import sqlite3
import sys
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('timesheet.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS time_entries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  clock_in TEXT NOT NULL,
                  clock_out TEXT)''')
    conn.commit()
    conn.close()

def clock_in(time=None):
    conn = sqlite3.connect('timesheet.db')
    c = conn.cursor()
    
    # Check if there's an open entry
    c.execute('SELECT id FROM time_entries WHERE clock_out IS NULL')
    if c.fetchone():
        print("Error: You're already clocked in!")
        conn.close()
        return
    
    if time:
        try:
            # Parse the input time and localize it
            parsed_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("Error: Time must be in format 'YYYY-MM-DD HH:MM:SS'")
            return
    else:
        # Use current local time
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO time_entries (clock_in) VALUES (?)', (time,))
    conn.commit()
    conn.close()
    print(f"Clocked in at {time}")

def clock_out(time=None):
    conn = sqlite3.connect('timesheet.db')
    c = conn.cursor()
    
    # Find the open entry
    c.execute('SELECT id FROM time_entries WHERE clock_out IS NULL')
    row = c.fetchone()
    if not row:
        print("Error: You're not clocked in!")
        conn.close()
        return
    
    time = time or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('UPDATE time_entries SET clock_out = ? WHERE id = ?', (time, row[0]))
    conn.commit()
    conn.close()
    print(f"Clocked out at {time}")

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def get_time_today():
    conn = sqlite3.connect('timesheet.db')
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now()
    
    # Get completed sessions for today
    c.execute('''SELECT clock_in, clock_out FROM time_entries 
                 WHERE date(clock_in) = ? AND clock_out IS NOT NULL''', (today,))
    
    total_seconds = 0
    for clock_in, clock_out in c.fetchall():
        start = datetime.strptime(clock_in, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(clock_out, '%Y-%m-%d %H:%M:%S')
        total_seconds += (end - start).total_seconds()
    
    # Check for open session
    c.execute('''SELECT clock_in FROM time_entries 
                 WHERE date(clock_in) = ? AND clock_out IS NULL''', (today,))
    open_session = c.fetchone()
    
    if open_session:
        start = datetime.strptime(open_session[0], '%Y-%m-%d %H:%M:%S')
        ongoing_seconds = (current_time - start).total_seconds()
        total_seconds += ongoing_seconds
        ongoing_time = format_duration(int(ongoing_seconds))
        
        # Calculate estimated finish time (8 hour workday)
        seconds_remaining = (8 * 3600) - total_seconds
        if seconds_remaining > 0:
            finish_time = current_time + timedelta(seconds=seconds_remaining)
            finish_time_str = finish_time.strftime('%I:%M %p')
            conn.close()
            return f"{format_duration(int(total_seconds))} (including {ongoing_time} from current session) - Estimated finish time: {finish_time_str}"
        else:
            overtime = format_duration(int(-seconds_remaining))
            conn.close()
            return f"{format_duration(int(total_seconds))} (including {ongoing_time} from current session) - {overtime} over 8 hours"
    
    conn.close()
    return format_duration(int(total_seconds))

def get_time_week():
    conn = sqlite3.connect('timesheet.db')
    c = conn.cursor()
    today = datetime.now()
    current_time = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    
    # Get completed sessions for the week
    c.execute('''SELECT clock_in, clock_out FROM time_entries 
                 WHERE date(clock_in) >= ? AND clock_out IS NOT NULL''', (week_start,))
    
    total_seconds = 0
    for clock_in, clock_out in c.fetchall():
        start = datetime.strptime(clock_in, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(clock_out, '%Y-%m-%d %H:%M:%S')
        total_seconds += (end - start).total_seconds()
    
    # Check for open session
    c.execute('''SELECT clock_in FROM time_entries 
                 WHERE date(clock_in) >= ? AND clock_out IS NULL''', (week_start,))
    open_session = c.fetchone()
    
    if open_session:
        start = datetime.strptime(open_session[0], '%Y-%m-%d %H:%M:%S')
        ongoing_seconds = (current_time - start).total_seconds()
        total_seconds += ongoing_seconds
        ongoing_time = format_duration(int(ongoing_seconds))
        conn.close()
        return f"{format_duration(int(total_seconds))} (including {ongoing_time} from current session)"
    
    conn.close()
    return format_duration(int(total_seconds))

def show_help():
    help_text = """
TimeTrack - Simple Time Tracking CLI

Usage:
    ./timesheet.py <command> [datetime]

Commands:
    in      Clock in (start tracking time)
    out     Clock out (stop tracking time)
    today   Show total time worked today
    week    Show total time worked this week
    --help  Show this help message

Options:
    datetime    Optional datetime string (format: "YYYY-MM-DD HH:MM:SS")
                Times are treated as local time zone
                If not provided, current local time will be used

Examples:
    ./timesheet.py in                         # Clock in now
    ./timesheet.py out                        # Clock out now
    ./timesheet.py in "2025-01-13 08:56:00"  # Clock in at specific time
    ./timesheet.py today                      # Show today's total time
    """
    print(help_text)

def main():
    init_db()
    
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(f"Time worked today: {get_time_today()}")
        return

    command = sys.argv[1]
    time = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "in":
        clock_in(time)
    elif command == "time":
        print(f"Time worked today: {get_time_today()}")
    elif command == "out":
        clock_out(time)
    elif command == "today":
        print(f"Time worked today: {get_time_today()}")
    elif command == "week":
        print(f"Time worked this week: {get_time_week()}")
    else:
        print("Invalid command. Use: in, out, time, today, or week")

if __name__ == "__main__":
    main()
