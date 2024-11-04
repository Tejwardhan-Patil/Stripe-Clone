#!/bin/bash

# Set environment variables
export ENVIRONMENT=${1:-"development"}
export PYTHON_MIGRATIONS_DIR="./database/migrations/"
export PYTHON_CONFIG="./backend/src/config/database_config.py"
export JAVA_MIGRATIONS_DIR="./backend/src/main/resources/migrations/"
export JAVA_CONFIG="./backend/src/main/resources/db_config.yaml"

# Function to run Python migrations
run_python_migrations() {
  echo "Running Python migrations..."
  python3 -m flask db upgrade
  if [ $? -eq 0 ]; then
    echo "Python migrations completed successfully."
  else
    echo "Python migrations failed."
    exit 1
  fi
}

# Function to run Java migrations
run_java_migrations() {
  echo "Running Java migrations..."
  java -jar ./backend/build/libs/db-migrator.jar --config $JAVA_CONFIG migrate
  if [ $? -eq 0 ]; then
    echo "Java migrations completed successfully."
  else
    echo "Java migrations failed."
    exit 1
  fi
}

# Select the type of migrations to run based on the backend
if [ -d $PYTHON_MIGRATIONS_DIR ]; then
  run_python_migrations
else
  echo "Python migrations directory not found."
fi

if [ -d $JAVA_MIGRATIONS_DIR ]; then
  run_java_migrations
else
  echo "Java migrations directory not found."
fi

echo "Database migration process completed."