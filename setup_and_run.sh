#!/bin/bash

# AI-Blockchain Hybrid Market Predictor Dashboard Setup and Run Script

set -e  # Exit on error

echo "🧠 AI-Blockchain Hybrid Market Predictor - Setup Script"
echo "========================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if .env exists
echo -e "${YELLOW}Step 1: Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file or copy from env.example"
    exit 1
fi

# Check if DB config exists in .env
if ! grep -q "DB_HOST" .env; then
    echo -e "${YELLOW}Adding database configuration to .env...${NC}"
    cat >> .env << 'EOF'

# Database Configuration for Dashboard
DB_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
POSTGRES_PORT=5432
EOF
    echo -e "${GREEN}✓ Added database configuration${NC}"
fi

# Step 2: Check Docker
echo ""
echo -e "${YELLOW}Step 2: Checking Docker availability...${NC}"
if command -v docker &> /dev/null && docker info &> /dev/null; then
    USE_DOCKER=true
    echo -e "${GREEN}✓ Docker is available${NC}"
else
    USE_DOCKER=false
    echo -e "${YELLOW}! Docker not available, will use local setup${NC}"
fi

# Step 3: Setup PostgreSQL
echo ""
echo -e "${YELLOW}Step 3: Setting up PostgreSQL...${NC}"

if [ "$USE_DOCKER" = true ]; then
    # Check if container exists
    if docker ps -a | grep -q sentiment_postgres; then
        echo -e "${GREEN}✓ PostgreSQL container exists${NC}"
        docker start sentiment_postgres 2>/dev/null || true
    else
        echo "Starting PostgreSQL with Docker..."
        docker run -d \
          --name sentiment_postgres \
          -e POSTGRES_USER=postgres \
          -e POSTGRES_PASSWORD=postgres \
          -e POSTGRES_DB=sentiment_market \
          -p 5432:5432 \
          postgres:15-alpine
        
        echo "Waiting for PostgreSQL to start..."
        sleep 5
    fi
    
    # Check if database is initialized
    if ! docker exec sentiment_postgres psql -U postgres -d sentiment_market -c "SELECT 1" &> /dev/null; then
        echo "Initializing database..."
        docker exec -i sentiment_postgres psql -U postgres < database/schema.sql 2>/dev/null || echo "Schema already exists"
        docker exec -i sentiment_postgres psql -U postgres < database/seed_data.sql 2>/dev/null || echo "Seed data already exists"
        echo -e "${GREEN}✓ Database initialized${NC}"
    else
        echo -e "${GREEN}✓ Database already initialized${NC}"
    fi
else
    # Check local PostgreSQL
    echo -e "${YELLOW}Checking local PostgreSQL...${NC}"
    if command -v pg_isready &> /dev/null && pg_isready &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is running locally${NC}"
        echo -e "${YELLOW}Note: Make sure database is initialized manually${NC}"
    else
        echo -e "${RED}✗ PostgreSQL not found. Please install PostgreSQL or use Docker${NC}"
        exit 1
    fi
fi

# Step 4: Check Python environment
echo ""
echo -e "${YELLOW}Step 4: Checking Python environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment found${NC}"
    source venv/bin/activate
    
    # Check if required packages are installed
    if ! python -c "import streamlit, plotly, psycopg2" &> /dev/null; then
        echo "Installing required packages..."
        pip install -q streamlit plotly psycopg2-binary pandas streamlit-autorefresh
        echo -e "${GREEN}✓ Packages installed${NC}"
    else
        echo -e "${GREEN}✓ Required packages are installed${NC}"
    fi
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment created and packages installed${NC}"
fi

# Step 5: Run dashboard
echo ""
echo -e "${GREEN}========================================================"
echo -e "🎉 Setup Complete!"
echo -e "========================================================"
echo -e "${NC}"
echo -e "${GREEN}Starting dashboard...${NC}"
echo ""
echo "Dashboard will open at: http://localhost:8501"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Change to dashboard directory and run
cd dashboard
streamlit run app.py

