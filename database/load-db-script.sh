#!/bin/bash

# default database name
DEFAULT_DB="skill_endorsement_db"

# if the first argument looks like a .sql file, user omitted the DB name
if [[ "$1" == *.sql ]]; then
    DB_NAME="$DEFAULT_DB"
    SQL_FILE="$1"
else
    # database name provided explicitly
    DB_NAME="${1:-$DEFAULT_DB}"
    SQL_FILE="$2"
fi

# validate file argument
if [ -z "$SQL_FILE" ]; then
    echo "Usage:"
    echo "  $0 [dbname] file.sql"
    echo
    echo "Examples:"
    echo "  $0 createDB.sql"
    echo "  $0 my_database createDB.sql"
    exit 1
fi

# verify SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo "Error: File '$SQL_FILE' does not exist."
    exit 1
fi

echo "Importing '$SQL_FILE' into database '$DB_NAME' using XAMPP SQL..."
sudo /opt/lampp/bin/mysql -u root "$DB_NAME" < "$SQL_FILE"

if [ $? -eq 0 ]; then
    echo "Import completed successfully!"
else
    echo "Import failed."
fi

