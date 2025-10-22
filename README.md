## 🛒 E-Store - Smart Electronics Marketplace
# 📋 Overview
- E-Store is a comprehensive online electronics marketplace built with Python, offering a seamless shopping experience for customers and efficient management tools for administrators. The platform features high security, AI-powered recommendations, and complete inventory and sales management.

## ✨ Key Features
# 👤 For Customers:
- 🧾 Secure Account Creation with email verification
- 🛍️ Browse Products with detailed information
- 🔍 Advanced Search for products by name
- 🤖 Smart Recommendations using AI (Google Gemini)
- 🛒 Advanced Shopping Cart with quantity management
- 📧 PDF Invoices delivered to your email
- ⭐ Product Ratings and reviews
- 📊 Product Sorting by rating or best-selling
- 👨‍💼 For Administrators:
- 🔐 Secure Login with encrypted passwords
- ➕ Add New Products to inventory
- ✏️ Edit Existing Products information
- 📈 Sales Tracking and product analytics


### 🛠 Technologies Used

## Core Libraries:
# python
- cryptography==41.0.7        # Password encryption
- google-generativeai==0.3.2  # AI integration
- reportlab==4.0.4            # PDF generation
- colorama==0.4.6             # CLI color formatting
- art==6.1                    # Text art design
- python-dotenv==1.0.0        # Environment variables management

# Project Structure:

- UNIT-PROJECT-1/
- ├── 📁 database/           # JSON databases
- ├── 📁 auth/              # Authentication system
- ├── 📁 controller/        # Control module
- ├── 📁 Ai/               # Artificial Intelligence
- ├── 📁 EMAILS_PDF/       # Invoices and emails
- ├── 🐍 main.py           # Main file
- └── 📄 requirements.txt  # Requirements

## 🚀 Installation & Setup

# 1. Install Dependencies:
- bash
- pip install -r requirements.txt

# 2. Environment Setup:
- Create a .env file and add:

# env :
- GEMINI_API_KEY=your_gemini_api_key
- EMAIL_ADDRESS=your_email@gmail.com
- EMAIL_PASSWORD=your_app_password

# 3. Run the Application:
- bash
- python main.py

## 🎯 How to Use :

# Main Menu:
- [1] 🧾 Sign Up
- [2] 🔑 Login
- [3] 🛠️  Admin Panel
- [0] ❌ Exit

# Customer Menu:
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

# Admin Menu:
- [1] ➕ Add New Product
- [2] ✏️  Edit Existing Product
- [0] 🚪 Logout

# 🔒 Security Features
- Advanced Encryption for passwords using Fernet
- Two-Factor Authentication via email OTP
- Secure Session management
- Input Validation and error handling

# 🤖 Artificial Intelligence
- The system uses Google Gemini to provide:
- Personalized product recommendations
- Search assistance
- Smart suggestions based on:
- Product catalog
- Reviews and ratings
- Best-selling products

## 📊 Data Management
# JSON Databases:
- users.json: Customer accounts
- products.json: Product catalog
- carts.json: Shopping carts
- comments_ratings.json: Reviews and ratings
- products_most_sold.json: Sales statistics

# 🎨 User Interface
- Colorful and attractive interface
- Expressive icons for ease of use
- Professional invoice design
- Smooth and enjoyable user experience

## 🌟 Special Features

# Automated Email System:
- OTP verification for signups
- PDF invoice delivery
- Professional email templates

# Smart Cart System:
- Quantity-based pricing
- Real-time total calculation
- Persistent cart storage

# AI-Powered Recommendations:
- Context-aware suggestions
- Multi-data source analysis (products, reviews, sales)
- Natural language queries

## 🐛 Troubleshooting
# Common Issues:
- Email not sending: Check .env file configuration
- Gemini API errors: Verify API key and internet connection
- File path errors: Ensure database files exist in correct locations 

### NOTE: before submitting the final project, please do the following command:
`pip freeze > requirements.txt` to enable use to know & use the packages used in your project.