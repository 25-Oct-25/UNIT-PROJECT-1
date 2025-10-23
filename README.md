# 🛒 E-Store - Smart Electronics Marketplace

## 📋 Overview
- E-Store is a comprehensive online electronics marketplace built with Python, offering a seamless shopping experience for customers and efficient management tools for administrators. The platform features high security, AI-powered recommendations, and complete inventory and sales management.

# ✨ Key Features

## 👤 For Customers:
- 🧾 Secure Account Creation with email verification and OTP
- 🛍️ Browse Products with detailed information across multiple categories
- 🔍 Advanced Search for products by name
- 🤖 Smart Recommendations using Google Gemini AI
- 🛒 Advanced Shopping Cart with quantity management
- 📧 PDF Invoices delivered to your email
- ⭐ Product Ratings and Reviews system
- 📊 Product Sorting by rating or best-selling
- 💰 Discount Coupons for special savings

## 👨‍💼 For Administrators:
- 🔐 Secure Login with encrypted passwords
- ➕ Add New Products to inventory
- ✏️ Edit Existing Products information
- 🏷️ Manage Discount Codes with customizable rates
- 📈 Sales Tracking and product analytics

# 🛠 Technologies Used

## Core Libraries:
- cryptography==46.0.2 - Password encryption
- google-generativeai==0.8.5 - AI integration (Gemini)
- reportlab==4.4.4 - PDF generation for invoices
- colorama==0.4.6 - CLI color formatting
- art==6.5 - Text art design
- python-dotenv==1.1.1 - Environment variables management
- Pillow==12.0.0 - Image processing support

# 📁 Project Structure

- UNIT-PROJECT-1/
- ├── 📁 database/           # JSON databases
- ├── 📁 auth/              # Authentication system
- ├── 📁 controller/        # Control module
- ├── 📁 Ai/               # Artificial Intelligence
- ├── 📁 EMAILS_PDF/       # Invoices and emails
- ├── 🐍 main.py           # Main file
- └── 📄 requirements.txt  # Requirements

# 🚀 Installation & Setup

## 1. Install Dependencies:
- bash
- pip install -r requirements.txt

## 2. Environment Setup:
- Create a .env file in the root directory and add:
- env
- GEMINI_API_KEY=your_gemini_api_key_here
- EMAIL_ADDRESS=your_email@gmail.com
- EMAIL_PASSWORD=your_app_password_here

## 3. Run the Application:
- bash
- python main.py

# 🎯 How to Use

## Main Menu:
- [1] 🧾 Sign Up
- [2] 🔑 Login  
- [3] 🛠️  Admin Panel
- [0] ❌ Exit

## Customer Menu:
- [1] 🛍️  Show All Products
- [2] 🔍 Search Products
- [3] ➕ Add Product to Cart
- [4] 🗑️  Delete Product from Cart
- [5] 🧺 Show My Cart
- [6] 💳 Pay & Receive Invoice
- [7] 🤖 Gemini Assistant
- [8] 💬 Add Review For Products
- [9] 🔍 Show Review For Products
- [10] 🔍 Sort Products By Rating Or Most Solds
- [0] 🚪 Logout

## Admin Menu:
- [1] ➕ Add New Product
- [2] ✏️  Edit Existing Product
- [3] 🏷️  Add/Edit Discount Coupons
- [0] 🚪 Logout

# 🔒 Security Features
- Advanced Encryption for passwords using Fernet cryptography
- Two-Factor Authentication via email OTP during signup
- Secure Session Management with encrypted JSON storage
- Input Validation and comprehensive error handling
- Separate Admin & User Authentication systems

# 🤖 Artificial Intelligence
- The system integrates Google Gemini AI to provide:
- Personalized product recommendations based on user queries
- Search assistance and contextual understanding
- Smart suggestions analyzing multiple data sources:
- Complete product catalog
- Customer reviews and ratings
- Best-selling product statistics

# 📊 Data Management

## JSON Databases:
- users.json - Customer accounts with encrypted passwords
- admins.json - Administrator credentials
- products.json - Complete product catalog with categories and prices
- carts.json - Shopping carts with quantity-based pricing
- comments_ratings.json - Customer reviews and ratings
- products_most_sold.json - Sales statistics and analytics
- discounts.json - Discount codes and rates

# 🎨 User Interface
- Colorful and attractive command-line interface using Colorama
- Expressive icons and formatting for enhanced user experience
- Professional PDF invoice design with detailed breakdowns
- Smooth navigation with clear menu structures

# 🌟 Special Features

## Automated Email System:
- OTP verification for secure signups
- PDF invoice delivery with professional templates
- Order confirmation and receipt emails

## Smart Cart System:
- Quantity-based pricing with real-time calculations
- Persistent cart storage across sessions
- Discount code application with validation

## AI-Powered Recommendations:
- Natural language queries understanding
- Multi-data source analysis (products, reviews, sales)
- Context-aware product suggestions

# 🔄 Workflow Examples

## Customer Journey:
- Sign Up → Email verification with OTP
- Browse Products → Search or view all items
- Get AI Recommendations → Ask Gemini for suggestions
- Add to Cart → Specify quantities
- Apply Discounts → Use coupon codes
- Checkout → Receive PDF invoice via email
- Leave Reviews → Rate purchased products

## Admin Operations:
- Secure Login → Encrypted authentication
- Manage Inventory → Add/edit products
- Create Discounts → Set up promotional codes
- Monitor Sales → Track product performance

# 🐛 Troubleshooting

## Common Issues:

### Email Not Sending:
- Check .env file configuration
- Verify Gmail app password setup
- Ensure internet connectivity

### Gemini API Errors:
- Verify API key in .env file
- Check internet connection
- Confirm API quota limits

### File Path Errors:
- Ensure database files exist in correct locations
- Check path configurations in controller files
- Verify read/write permissions

### JSON Decode Errors:
- Check for corrupted JSON files
- Verify file encoding (UTF-8)
- Ensure proper JSON syntax


# E-Store - Your Smart Electronics Shopping Companion 🚀
