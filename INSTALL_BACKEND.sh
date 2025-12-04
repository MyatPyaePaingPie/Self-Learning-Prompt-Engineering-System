#!/bin/bash
# Install backend dependencies

echo "📦 Installing backend dependencies..."

cd "$(dirname "$0")"

# Install with SSL cert verification disabled (workaround for macOS cert issues)
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    fastapi \
    'uvicorn[standard]' \
    'python-jose[cryptography]' \
    'passlib[argon2]' \
    argon2-cffi \
    cryptography \
    python-dotenv \
    slowapi \
    sqlalchemy \
    pydantic

echo "✅ Backend dependencies installed!"
echo ""
echo "Now run:"
echo "  python3 -m uvicorn backend.main:app --reload --port 8001"

