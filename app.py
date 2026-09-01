import re

from flask import Flask, render_template, request
from database import db
from models.book import Book
from models.student import Student
from models.issue import Issue
from datetime import date


app = Flask(__name__)

# ---------------- DATABASE CONFIGURATION ----------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ========================================================
# HOME
# ========================================================

@app.route("/")
def home():
    return render_template("home.html")


# ========================================================
# ADD BOOK
# ========================================================

@app.route("/admin/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        title = request.form["title"].strip()
        author = request.form["author"].strip()
        category = request.form["category"].strip()
        isbn = request.form["isbn"].strip()
        quantity = int(request.form["quantity"])

        book = Book(
            title=title,
            author=author,
            category=category,
            isbn=isbn,
            quantity=quantity,
            available_quantity=quantity
        )

        db.session.add(book)
        db.session.commit()

        return "Book added successfully!"

    return render_template("admin/add_book.html")


# ========================================================
# MANAGE BOOKS
# ========================================================

@app.route("/admin/books")
def manage_books():

    books = Book.query.all()

    return render_template(
        "admin/manage_book.html",
        books=books
    )


# ========================================================
# EDIT BOOK
# ========================================================

@app.route("/admin/book/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):

    book = Book.query.get_or_404(id)

    if request.method == "POST":

        book.title = request.form["title"].strip()
        book.author = request.form["author"].strip()
        book.category = request.form["category"].strip()
        book.isbn = request.form["isbn"].strip()

        new_quantity = int(request.form["quantity"])

        # Calculate how many books are currently issued
        issued_quantity = book.quantity - book.available_quantity

        # Prevent quantity from becoming smaller than issued books
        if new_quantity < issued_quantity:
            return (
                f"Quantity cannot be less than {issued_quantity} "
                "because some books are currently issued."
            )

        book.quantity = new_quantity

        # Update available books
        book.available_quantity = new_quantity - issued_quantity

        db.session.commit()

        return "Book updated successfully!"

    return render_template(
        "admin/edit_book.html",
        book=book
    )


# ========================================================
# DELETE BOOK
# ========================================================

@app.route("/admin/book/delete/<int:id>", methods=["POST"])
def delete_book(id):

    book = Book.query.get_or_404(id)

    # Check whether this book has issue records
    existing_issue = Issue.query.filter_by(
        book_id=book.id
    ).first()

    if existing_issue:
        return "Cannot delete this book because it has issue records."

    db.session.delete(book)
    db.session.commit()

    return "Book deleted successfully!"


# ========================================================
# ADD STUDENT
# ========================================================

@app.route("/admin/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        course = request.form["course"].strip()

        # ---------------- PHONE VALIDATION ----------------

        if not re.fullmatch(r"[0-9]{10}", phone):
            return "Phone number must contain exactly 10 digits."

        # ---------------- GMAIL VALIDATION ----------------

        if not re.fullmatch(
            r"[a-zA-Z0-9._%+-]+@gmail\.com",
            email
        ):
            return "Please enter a valid Gmail address."

        # ---------------- DUPLICATE EMAIL ----------------

        existing_email = Student.query.filter_by(
            email=email
        ).first()

        if existing_email:
            return "This Gmail is already registered."

        # ---------------- DUPLICATE PHONE ----------------

        existing_phone = Student.query.filter_by(
            phone=phone
        ).first()

        if existing_phone:
            return "This phone number is already registered."

        # ---------------- CREATE STUDENT ----------------

        student = Student(
            name=name,
            email=email,
            phone=phone,
            course=course
        )

        db.session.add(student)
        db.session.commit()

        return "Student added successfully!"

    return render_template("admin/add_student.html")


# ========================================================
# MANAGE STUDENTS
# ========================================================

@app.route("/admin/students")
def manage_students():

    students = Student.query.all()

    return render_template(
        "admin/manage_student.html",
        students=students
    )


# ========================================================
# ISSUE BOOK
# ========================================================

@app.route("/admin/issue-book", methods=["GET", "POST"])
def issue_book():

    students = Student.query.all()

    books = Book.query.filter(
        Book.available_quantity > 0
    ).all()

    if request.method == "POST":

        student_id = int(request.form["student_id"])
        book_id = int(request.form["book_id"])

        issue_date = date.fromisoformat(
            request.form["issue_date"]
        )

        due_date = date.fromisoformat(
            request.form["due_date"]
        )

        # ---------------- DATE VALIDATION ----------------

        if due_date < issue_date:
            return "Due date cannot be before issue date."

        # ---------------- GET BOOK ----------------

        book = Book.query.get_or_404(book_id)

        if book.available_quantity <= 0:
            return "Book is not available."

        # ---------------- CHECK STUDENT ----------------

        student = Student.query.get_or_404(student_id)

        # ---------------- CREATE ISSUE ----------------

        issue = Issue(
            book_id=book_id,
            student_id=student_id,
            issue_date=issue_date,
            due_date=due_date,
            status="Issued",
            fine=0
        )

        # Reduce available quantity
        book.available_quantity -= 1

        db.session.add(issue)
        db.session.commit()

        return "Book issued successfully!"

    return render_template(
        "admin/issue_book.html",
        students=students,
        books=books
    )


# ========================================================
# MANAGE ISSUES
# ========================================================

@app.route("/admin/issues")
def manage_issues():

    issues = Issue.query.all()

    return render_template(
        "admin/manage_issue.html",
        issues=issues
    )


# ========================================================
# RETURN BOOK + FINE
# ========================================================

@app.route("/admin/return-book/<int:id>", methods=["POST"])
def return_book(id):

    issue = Issue.query.get_or_404(id)

    # Already returned
    if issue.status == "Returned":
        return "Book already returned."

    today = date.today()

    issue.return_date = today
    issue.status = "Returned"

    # ---------------- CALCULATE FINE ----------------

    if today > issue.due_date:

        late_days = (today - issue.due_date).days

        # ₹5 per late day
        issue.fine = late_days * 5

    else:

        issue.fine = 0

    # ---------------- UPDATE BOOK ----------------

    book = Book.query.get_or_404(issue.book_id)

    book.available_quantity += 1

    db.session.commit()

    return "Book returned successfully!"


# ========================================================
# CHATBOT
# ========================================================

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    question = ""
    answer = ""

    if request.method == "POST":

        question = request.form["question"].strip().lower()

        # ==================================================
        # AVAILABLE BOOKS
        # ==================================================

        if "available" in question and "book" in question:

            books = Book.query.filter(
                Book.available_quantity > 0
            ).all()

            if books:

                answer = "Available books:\n\n"

                for book in books:

                    answer += (
                        f"{book.title} - "
                        f"Available: {book.available_quantity}\n"
                    )

            else:

                answer = (
                    "Sorry, no books are currently available."
                )


        # ==================================================
        # ALL BOOKS
        # ==================================================

        elif "all books" in question or "list books" in question:

            books = Book.query.all()

            if books:

                answer = "All books:\n\n"

                for book in books:

                    answer += (
                        f"{book.title} - "
                        f"Quantity: {book.quantity}, "
                        f"Available: {book.available_quantity}\n"
                    )

            else:

                answer = (
                    "There are no books in the library."
                )


        # ==================================================
        # ISSUED BOOKS
        # ==================================================

        elif "issued" in question:

            issues = Issue.query.filter_by(
                status="Issued"
            ).all()

            if issues:

                answer = "Currently issued books:\n\n"

                for issue in issues:

                    answer += (
                        f"{issue.book.title} → "
                        f"{issue.student.name}\n"
                    )

            else:

                answer = (
                    "No books are currently issued."
                )


        # ==================================================
        # FINE
        # ==================================================

        elif "fine" in question:

            issues = Issue.query.filter(
                Issue.fine > 0
            ).all()

            if issues:

                answer = "Fine details:\n\n"

                for issue in issues:

                    answer += (
                        f"{issue.student.name} - "
                        f"{issue.book.title} - "
                        f"Fine: ₹{issue.fine}\n"
                    )

            else:

                answer = (
                    "There are currently no fines."
                )


        # ==================================================
        # DUE DATE
        # ==================================================

        elif "due" in question:

            issues = Issue.query.filter_by(
                status="Issued"
            ).all()

            if issues:

                answer = "Current due dates:\n\n"

                for issue in issues:

                    answer += (
                        f"{issue.student.name} - "
                        f"{issue.book.title} - "
                        f"Due: {issue.due_date}\n"
                    )

            else:

                answer = (
                    "There are no currently issued books."
                )


        # ==================================================
        # HELP
        # ==================================================

        elif "help" in question:

            answer = """I can help you with:

📚 Show available books
📚 Show all books
📖 Show issued books
📅 Show due dates
💰 Show fines
"""


        # ==================================================
        # UNKNOWN QUESTION
        # ==================================================

        else:

            answer = """Sorry, I don't understand that question.

Try asking:

• Show available books
• Show all books
• Show issued books
• Show due dates
• Show my fine
• Help
"""

    return render_template(
        "chatbot.html",
        question=question,
        answer=answer
    )


# ========================================================
# SHOW ALL ROUTES
# ========================================================

print(app.url_map)


# ========================================================
# RUN APPLICATION
# ========================================================

if __name__ == "__main__":
    app.run(debug=True)