import sqlite3

# ---DATABASE CONNECTION-----
try:
    conn = sqlite3.connect('event_management.db')  # The database file name
    conn.execute('PRAGMA foreign_keys = ON;')
    cursor = conn.cursor()

    # Create User_Type table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_Type (
    user_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_type TEXT NOT NULL)
    ''')

    # Create Users table with the new 'location' and 'contact' fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        business_name TEXT,
        email TEXT UNIQUE NOT NULL,
        active_status INTEGER NOT NULL CHECK (active_status IN (0, 1)),
        password TEXT NOT NULL,
        location TEXT,
        contact TEXT,
        user_type_id INTEGER,
        profile_type_id INTEGER,
        isActive INTEGER NOT NULL DEFAULT 1 CHECK (isActive IN (0, 1)),  -- 'isActive' field as boolean
        FOREIGN KEY (user_type_id) REFERENCES User_Type (user_type_id),
        FOREIGN KEY (profile_type_id) REFERENCES Profile_Type (profile_type_id)
    )
     ''')
    # Create Profile_Type table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Profile_Type (
    profile_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_type TEXT NOT NULL)
    ''')

    # Create Profile table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Profile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_detail TEXT NOT NULL,
        experience TEXT NOT NULL,
        thumbnail_image TEXT NOT NULL,
        profile_type_id INTEGER,
        user_id INTEGER,
        isActive INTEGER NOT NULL DEFAULT 1 CHECK (isActive IN (0, 1)),  -- 'isActive' field as boolean
        FOREIGN KEY (profile_type_id) REFERENCES Profile_Type (profile_type_id),
        FOREIGN KEY (user_id) REFERENCES Users (user_id)
    )
''')

    # Create Packages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Packages (
    package_id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL,
    package_price REAL NOT NULL,
    price REAL NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users (user_id))
    ''')

    # Create Package_Details table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Package_Details (
    package_dtl_id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_header_image TEXT,
    package_id INTEGER, 
    FOREIGN KEY (package_id) REFERENCES Packages (package_id))
    ''')

     # Create Package_images table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Package_images (
    Package_image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id INTEGER,
    package_image TEXT,
    image_desc TEXT,             
    FOREIGN KEY (package_id) REFERENCES Packages (package_id))
    ''')

    # Add the 'image_desc' column as TEXT if it doesn't already exist
    column_name = "image_desc"
    column_type = "TEXT"

    # SQLite doesn't support an easy way to check if a column exists.
    # Use a workaround to fetch the table's schema and check manually.
    cursor.execute("PRAGMA table_info(Package_images)")
    columns = [info[1] for info in cursor.fetchall()]  # Extract column names

    if column_name not in columns:
        cursor.execute(f"ALTER TABLE Package_images ADD COLUMN {column_name} {column_type}")
        print(f"Column '{column_name}' added successfully.")
    else:
        print(f"Column '{column_name}' already exists.")


    # Create Events 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    number_of_guests INTEGER NOT NULL,
    package_id INTEGER,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    user_id INTEGER,
    profile_id INTEGER,
    location TEXT,
    payment_status TEXT NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (package_id) REFERENCES Packages (package_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id),
    FOREIGN KEY (profile_id) REFERENCES Profile (profile_id)
)
''')

    # status TEXT NOT NULL CHECK (status IN ('Pending', 'Completed', 'Failed')),
    # Create Payments table with user_id as FK
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_amount REAL NOT NULL,
    payment_type TEXT NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'payment transfered',
    event_id INTEGER,
    package_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (event_id) REFERENCES Events (event_id),
    FOREIGN KEY (package_id) REFERENCES Packages (package_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id))
    ''')

    # Create Event_Organisers table with profile_type_id as a foreign key
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Event_Organisers (
    organiser_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_name TEXT NOT NULL,
    event_location TEXT NOT NULL,
    event_description TEXT NOT NULL,
    event_date TEXT NOT NULL,
    application_deadline TEXT NOT NULL,
    service_type TEXT NOT NULL,  -- Storing array of services as comma-separated values
    profile_type_id INTEGER,  -- Foreign key from Profile_Type table
    FOREIGN KEY (profile_type_id) REFERENCES Profile_Type (profile_type_id))
    ''')
    # Add Mark_bidding table with user_id and event_id as foreign keys
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Mark_bidding (
    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    event_type TEXT NOT NULL,
    bid_amount INTEGER NOT NULL,
    currency TEXT NOT NULL,
    remarks TEXT,  -- Optional comments
    FOREIGN KEY (user_id) REFERENCES Users (user_id),
    FOREIGN KEY (event_id) REFERENCES Event_Organisers (organiser_event_id))
    ''')


     
    # Step 4: Commit the changes
    conn.commit()

    # Step 5: Close the connection
    conn.close()
    print("Tables created successfully!")
except sqlite3.Error as error:
    print("Failed to connect to the database:", error)