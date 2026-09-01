from database import db


class Issue(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("book.id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    issue_date = db.Column(
        db.Date,
        nullable=False
    )

    due_date = db.Column(
        db.Date,
        nullable=False
    )

    return_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Issued"
    )

    fine = db.Column(
        db.Integer,
        default=0
    )

    book = db.relationship("Book")

    student = db.relationship("Student")