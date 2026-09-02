# 📚 Library Management System

A web-based Library Management System built using Python Flask, SQLite,
SQLAlchemy, HTML, CSS.

## 🚀 Features

- Add, edit and delete books
- Manage students
- Validate Gmail and 10-digit phone numbers
- Issue and return books
- Track issue and due dates
- Automatically calculate late fines
- Track available book quantity
- Rule-based library chatbot

## 🛠️ Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- SQLAlchemy
- HTML5
- CSS3
  

## 📂 Project Structure

library-management-project/
│
├── app.py
├── database.py
│
├── models/
│   ├── book.py
│   ├── student.py
│   └── issue.py
│
├── templates/
│   ├── home.html
│   ├── chatbot.html
│   └── admin/
│       ├── add_book.html
│       ├── manage_book.html
│       ├── edit_book.html
│       ├── add_student.html
│       ├── manage_student.html
│       ├── issue_book.html
│       └── manage_issue.html
│
├── static/
├── .gitignore
└── README.md

# ⚙️ Installation & Setup

Follow these steps to run the project on your computer.

## 1. Install Python

Install Python 3.10 or newer.

Check Python installation:

```bash
python --version

## 2. Install Dependencies
pip install flask flask-sqlalchemy
