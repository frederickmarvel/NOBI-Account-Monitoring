#!/bin/bash

# Vercel Deployment Helper Script

echo "🚀 NOBI Account Monitoring - Vercel Deployment"
echo "=============================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed"
    echo ""
    echo "Install it with:"
    echo "  npm install -g vercel"
    echo ""
    exit 1
fi

echo "✅ Vercel CLI found"
echo ""

# Check if logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 You need to login to Vercel first"
    echo ""
    vercel login
    echo ""
fi

# Show current environment variables
echo "📋 Current Environment Check:"
echo ""

if [ -f ".env" ]; then
    echo "✅ .env file exists locally"
    if grep -q "ETHERSCAN_API_KEY" .env; then
        echo "✅ ETHERSCAN_API_KEY found in .env"
    else
        echo "⚠️  ETHERSCAN_API_KEY not found in .env"
    fi
else
    echo "⚠️  .env file not found (will use Vercel environment variables)"
fi

echo ""
echo "⚠️  Important: Make sure you've set ETHERSCAN_API_KEY in Vercel:"
echo "   vercel env add ETHERSCAN_API_KEY"
echo ""

# Deployment options
echo "Choose deployment option:"
echo ""
echo "  1) Deploy to preview (test deployment)"
echo "  2) Deploy to production"
echo "  3) Link existing project"
echo "  4) Check deployment status"
echo "  5) View environment variables"
echo "  6) Exit"
echo ""

read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "🔨 Deploying to preview environment..."
        echo ""
        vercel
        ;;
    2)
        echo ""
        echo "🚀 Deploying to production..."
        echo ""
        read -p "Are you sure? This will go live! (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            vercel --prod
        else
            echo "Cancelled"
        fi
        ;;
    3)
        echo ""
        echo "🔗 Linking to existing Vercel project..."
        echo ""
        vercel link
        ;;
    4)
        echo ""
        echo "📊 Checking deployment status..."
        echo ""
        vercel ls
        ;;
    5)
        echo ""
        echo "🔐 Environment variables:"
        echo ""
        vercel env ls
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✨ Done!"
echo ""
echo "📚 For more info, see VERCEL_DEPLOYMENT.md"
