import mysql.connector
from mysql.connector import errorcode

# --- Database Configuration ---
# !!! Update these values to match your MySQL setup !!!
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost'
}
DB_NAME = 'homelike'

def create_database(cursor):
    """Creates the database if it doesn't already exist."""
    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{DB_NAME}' created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print(f"Database '{DB_NAME}' already exists.")
        else:
            print(err)
            exit(1)

def create_tables(cursor):
    """Defines and executes the CREATE TABLE statements."""
    
    TABLES = {}

    # Parent Tables (no foreign keys, or only to other parents)
    TABLES['Hostel'] = (
        "CREATE TABLE `Hostel` ("
        "  `HId` VARCHAR(20) NOT NULL,"
        "  `HName` VARCHAR(100) NOT NULL,"
        "  `WName` VARCHAR(100),"
        "  PRIMARY KEY (`HId`)"
        ") ENGINE=InnoDB")

    TABLES['Rooms'] = (
        "CREATE TABLE `Rooms` ("
        "  `RNo` VARCHAR(20) NOT NULL,"
        "  `Occupancy` INT,"
        "  `Block` VARCHAR(20),"
        "  `Floor` INT,"
        "  PRIMARY KEY (`RNo`)"
        ") ENGINE=InnoDB")

    TABLES['Washroom'] = (
        "CREATE TABLE `Washroom` ("
        "  `WashroomID` VARCHAR(20) NOT NULL,"
        "  `Floor` INT,"
        "  `Block` VARCHAR(20),"
        "  PRIMARY KEY (`WashroomID`)"
        ") ENGINE=InnoDB")

    TABLES['Filter'] = (
        "CREATE TABLE `Filter` ("
        "  `FId` VARCHAR(20) NOT NULL,"
        "  `Floor` INT,"
        "  `Block` VARCHAR(20),"
        "  PRIMARY KEY (`FId`)"
        ") ENGINE=InnoDB")

    # Child Tables (with foreign keys)
    TABLES['Warden'] = (
        "CREATE TABLE `Warden` ("
        "  `WardenID` VARCHAR(20) NOT NULL,"
        "  `WName` VARCHAR(100) NOT NULL,"
        "  `Wmail` VARCHAR(100) UNIQUE,"
        "  `Wcontact` VARCHAR(20),"
        "  `HId` VARCHAR(20) NOT NULL,"
        "  PRIMARY KEY (`WardenID`),"
        "  FOREIGN KEY (`HId`) REFERENCES `Hostel` (`HId`)"
        "    ON DELETE CASCADE"
        ") ENGINE=InnoDB")

    # ------------------ MODIFIED TABLE ------------------
    TABLES['Student'] = (
        "CREATE TABLE `Student` ("
        "  `SId` VARCHAR(20) NOT NULL,"
        "  `SName` VARCHAR(100) NOT NULL,"
        "  `Smail` VARCHAR(100) NOT NULL UNIQUE,"
        "  `Scontact` VARCHAR(20),"
        "  `HId` VARCHAR(20) NULL,"
        "  `RNo` VARCHAR(20) NULL,"  # <-- MODIFICATION 1: Changed to NULL
        "  PRIMARY KEY (`SId`),"
        "  FOREIGN KEY (`HId`) REFERENCES `Hostel` (`HId`)"
        "    ON DELETE SET NULL,"  # <-- MODIFICATION 2: Changed to SET NULL
        "  FOREIGN KEY (`RNo`) REFERENCES `Rooms` (`RNo`)"
        "    ON DELETE SET NULL"  # <-- MODIFICATION 2: Changed to SET NULL
        ") ENGINE=InnoDB")
    # ---------------------------------------------------

    TABLES['Complaint'] = (
        "CREATE TABLE `Complaint` ("
        "  `CId` VARCHAR(20) NOT NULL,"
        "  `description` TEXT NOT NULL,"
        "  `Status` VARCHAR(30) DEFAULT 'Pending',"
        "  `date_time` DATETIME NOT NULL,"
        "  `SId` VARCHAR(20) NOT NULL,"
        "  `WardenID` VARCHAR(20) NOT NULL,"
        "  `HId` VARCHAR(20) NOT NULL,"
        "  `RNo` VARCHAR(20) NULL,"
        "  `WashroomID` VARCHAR(20) NULL,"
        "  `FId` VARCHAR(20) NULL,"
        "  PRIMARY KEY (`CId`),"
        "  FOREIGN KEY (`SId`) REFERENCES `Student` (`SId`),"
        "  FOREIGN KEY (`WardenID`) REFERENCES `Warden` (`WardenID`),"
        "  FOREIGN KEY (`HId`) REFERENCES `Hostel` (`HId`),"
        "  FOREIGN KEY (`RNo`) REFERENCES `Rooms` (`RNo`),"
        "  FOREIGN KEY (`WashroomID`) REFERENCES `Washroom` (`WashroomID`),"
        "  FOREIGN KEY (`FId`) REFERENCES `Filter` (`FId`),"
        "  CHECK (`RNo` IS NOT NULL OR `WashroomID` IS NOT NULL OR `FId` IS NOT NULL)"
        ") ENGINE=InnoDB")

    # --- Execution ---
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table '{table_name}'... ", end='')
            cursor.execute(table_description)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)

def main():
    """Main function to connect and run the setup."""
    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()

        # Create and select the database
        create_database(cursor)
        cursor.execute(f"USE {DB_NAME}")

        # Drop tables in reverse order of creation to avoid FK issues
        print("Dropping existing tables (if any)...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute("DROP TABLE IF EXISTS Complaint, Student, Warden, Filter, Washroom, Rooms, Hostel;")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        print("Tables dropped.")

        # Create new tables
        create_tables(cursor)

        # Commit changes
        cnx.commit()
        print("\nAll tables created successfully in 'homelike' database!")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        else:
            print(err)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

if __name__ == "__main__":
    main()