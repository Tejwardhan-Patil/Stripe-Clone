#!/bin/bash

# Exit on any error
set -e

# Define environment (development or production)
ENVIRONMENT=${1:-production}

# Build the project
echo "Building the project..."
bash scripts/build.sh

# Run tests
echo "Running tests..."
# Frontend tests
echo "Running frontend tests..."
cd frontend
npm install
npm run test
cd ..

# Backend tests
echo "Running backend tests..."
cd backend
python3 -m unittest discover -s src/tests
cd ..

# Containerize the application (frontend and backend)
echo "Building Docker images..."
docker build -t stripe-clone-frontend:latest ./frontend
docker build -t stripe-clone-backend:latest ./backend

# Push Docker images to Docker registry 
echo "Pushing Docker images to Docker registry..."
docker tag stripe-clone-frontend:latest website.com/stripe-clone-frontend:latest
docker tag stripe-clone-backend:latest website.com/stripe-clone-backend:latest
docker push website.com/stripe-clone-frontend:latest
docker push website.com/stripe-clone-backend:latest

# Deploy Infrastructure using Terraform
echo "Deploying infrastructure with Terraform..."
cd deployment/terraform
terraform init
terraform apply -auto-approve
cd ../..

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
cd deployment/kubernetes
kubectl apply -f manifests/k8s_service.yaml
cd ../..

# Run database migrations
echo "Running database migrations..."
bash scripts/db_migrate.sh

# Post-deployment checks
echo "Running post-deployment checks..."
kubectl rollout status deployment/stripe-clone-backend
kubectl rollout status deployment/stripe-clone-frontend

echo "Deployment completed successfully for $ENVIRONMENT environment."