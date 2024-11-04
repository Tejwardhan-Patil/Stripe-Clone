#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Build Frontend (Angular)
echo -e "${GREEN}Building Frontend...${NC}"
cd frontend
npm install
npm run build --prod
cd ..

# Build Backend (Python and Java)
echo -e "${GREEN}Building Backend...${NC}"

# Python backend build (virtual environment and dependencies)
echo -e "${GREEN}Setting up Python backend...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Java backend build (for performance-critical services)
echo -e "${GREEN}Building Java backend services...${NC}"
cd backend/src/services
./gradlew build
cd ../../..

# Build Go services for performance-critical components
echo -e "${GREEN}Building Go services...${NC}"
cd payment_processing/transaction_management
go mod tidy
go build -o transaction_manager
cd ../refunds_manager
go mod tidy
go build -o refunds_manager
cd ../../..

cd performance/caching
go mod tidy
go build -o redis_cache
cd ../../..

cd monitoring/metrics
go mod tidy
go build -o prometheus_exporter
cd ../../..

# Finish
echo -e "${GREEN}Build completed successfully!${NC}"