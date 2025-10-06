#!/bin/bash
# Fix pkg_resources issue on EC2

echo "🔧 Fixing pkg_resources issue..."
echo "================================"

# 1. Install setuptools (which includes pkg_resources)
echo "📦 Installing setuptools..."
pip install setuptools

# 2. Upgrade pip and setuptools
echo "⬆️ Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# 3. Install pkg_resources specifically
echo "📦 Installing pkg_resources..."
pip install setuptools

# 4. Verify installation
echo "✅ Verifying pkg_resources installation..."
python -c "import pkg_resources; print('pkg_resources is available')"

# 5. Test Django
echo "🧪 Testing Django..."
python manage.py check

echo "✅ Fix completed!"
