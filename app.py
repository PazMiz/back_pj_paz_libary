import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date,timedelta
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library2.sqlite3'
app.config['SECRET_KEY'] = "random string"

# Define the books list outside the route handler functions
books = [
    {'id': 1, 'bookname': 'Book 1', 'writer': 'Author 1', 'year_published': 2021, 'book_loan': '1'},
    {'id': 2, 'bookname': 'Book 2', 'writer': 'Author 2', 'year_published': 2022, 'book_loan': '2'},
    {'id': 3, 'bookname': 'Book 3', 'writer': 'Author 3', 'year_published': 2023, 'book_loan': '3'}
]

db = SQLAlchemy(app)
CORS(app)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


app.json_encoder = CustomJSONEncoder
@app.route('/')
def hello():
    return "hey"


#################### Customer Start point ####################


class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    age = Column(Integer)

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', city='{self.city}', age={self.age})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'age': self.age,
        }


@app.route("/customers")
def cust_show():
    print ("start")
    customers = Customer.query.all()
    print ("customers: " + str(customers))
    cust_list = [customer.to_dict() for customer in customers]
    print ("list: " + str(cust_list))
    json_data = json.dumps(cust_list)
    print ("json: " + str(json_data))
    return json_data


@app.route('/customers/new', methods=['POST'])
def newcust():
    data = request.get_json()
    name = data['name']
    city = data['city']
    age = data['age']

    new_customer = Customer(name=name, city=city, age=age)
    db.session.add(new_customer)
    db.session.commit()
    return "A new Library Customer was created."


@app.route('/customers/delete/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)

    Loan.query.filter_by(cust_id=id).delete()

    db.session.delete(customer)
    db.session.commit()

    return {"message": "Customer deleted successfully."}


@app.route('/customers/search/<string:name>', methods=['GET'])
def search_customer(name):
    customers = Customer.query.filter(Customer.name.ilike(f'%{name}%')).all()
    if not customers:
        return {'message': 'No customers found.'}, 404

    customer_list = [customer.to_dict() for customer in customers]
    json_data = json.dumps(customer_list)
    return json_data

##################### Customer End point ####################




######################### Book Start Point ####################
class Book(db.Model):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    bookname = Column(String)
    writer = Column(String)
    year_published = Column(Integer)
    book_loan = Column(String(1), nullable=False)

    def __repr__(self):
        return f"<Book(id={self.id}, name='{self.bookname}', author='{self.writer}', year_published={self.year_published}, type={self.book_loan})>"

    def to_dict(self):
        return {
            'id': self.id,
            'bookname': self.bookname,
            'writer': self.writer,
            'year_published': self.year_published,
            'book_loan': self.book_loan,
        }


@app.route("/books")
def book_show():
    book_list = []
    books = Book.query.all()
    for book in books:
        book_dict = {
            'id': book.id,
            'bookname': book.bookname,  # Replace 'title' with the appropriate column name from your Book table
            'writer': book.writer,  # Replace 'writer' with the appropriate column name from your Book table
            'year_published': book.year_published,  # Replace 'year_published' with the appropriate column name from your Book table
            'book_loan': book.book_loan,  # Replace 'book_loan' with the appropriate column name from your Book table
        }
        book_list.append(book_dict)
    return jsonify(book_list)


@app.route('/books/new', methods=['POST'])
def newbook():
    data = request.get_json()
    bookname = data['bookname']
    writer = data['writer']
    year_published = data['year_published']
    book_loan = data['book_loan']

    new_book = Book(bookname=bookname, writer=writer,
                    year_published=year_published, book_loan=book_loan)
    db.session.add(new_book)
    db.session.commit()
    return "A new book record was created."


@app.route('/books/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return {"message": "Book deleted successfully."}


@app.route('/books/search/<name>', methods=['GET'])
def search_books(name):
    books = Book.query.filter(Book.bookname.ilike(f'%{name}%')).all()

    if not books:
        return {'message': 'No books found.'}, 404

    book_list = [book.to_dict() for book in books]
    return jsonify(book_list)


@app.route('/books/update/<int:book_id>', methods=['PUT'])
def handle_update_book(book_id):
    book_update = Book.query.get(book_id)
    if book_update:
        data = request.get_json()
        book_update.bookname = data.get('bookname', book_update.bookname)
        book_update.writer = data.get('writer', book_update.writer)
        book_update.year_published = data.get('year_published', book_update.year_published)
        book_update.book_loan = data.get('book_loan', book_update.book_loan)
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    else:
        return jsonify({'error': 'Book not found'}), 404
    

    ########################## Book End Point ####################


    

    ################# Loan Start Point ####################


class Loan(db.Model):
    __tablename__ = 'loans'
    id = Column(Integer, primary_key=True)
    cust_id = Column(Integer, ForeignKey('customers.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    loan_date = Column(Date)
    return_date = Column(Date)
    book_loan = Column(String(1), nullable=False)

    # Add a relationship to the Customer table
    customer = relationship("Customer", backref="loans", lazy="joined")
    book = relationship("Book", backref="loans")

    def __repr__(self):
        return f"<Loan id={self.id}, cust_id={self.cust_id}, book_id={self.book_id}, loan_date='{self.loan_date}', return_date='{self.return_date}', book_loan='{self.book_loan}'>"

    def to_dict(self):
        customer_name = self.customer.name if self.customer else "Unknown Customer"
        today = date.today()
        is_late = self.return_date < today
        return {
            'id': self.id,
            'cust_id': self.cust_id,
            'cust_name': customer_name,
            'book_id': self.book_id,
            'loan_date': str(self.loan_date),
            'return_date': str(self.return_date),
            'book_loan': self.book_loan,
            'is_late': is_late
        }

@app.route("/loans")
def loans_show():
    loan_list = []
    loans = db.session.query(Loan, Customer, Book).join(Customer).join(Book).all()

    for loan, customer, book in loans:
        loan_data = loan.to_dict()
        loan_data['customer_name'] = customer.name
        loan_data['book_name'] = book.bookname
        loan_data['is_late'] = check_return_date(loan.return_date)
        loan_list.append(loan_data)

    json_data = json.dumps(loan_list, default=str)
    return json_data


def check_return_date(return_date):
    current_date = date.today()
    late_threshold = current_date - timedelta(days=10)

    if return_date < late_threshold:
        return True
    else:
        return False


@app.route('/loans/new', methods=['POST'])
def new_loan():
    data = request.get_json()
    cust_id = int(data['cust_id'])
    book_id = int(data['book_id'])
    loan_date = datetime.strptime(data['loan_date'], '%Y-%m-%d').date()
    return_date = datetime.strptime(data['return_date'], '%Y-%m-%d').date()
    book_loan = data['book_loan']

    # Check if a loan with the same book_id already exists
    existing_loan = Loan.query.filter_by(book_id=book_id).first()
    if existing_loan:
        return "A loan with the same book ID already exists."

    new_loan = Loan(cust_id=cust_id, book_id=book_id,loan_date=loan_date, return_date=return_date, book_loan=book_loan)
    db.session.add(new_loan)
    db.session.commit()
    return "A new loan record was created."

@app.route('/loans/book/<int:book_id>')
def get_loans_by_book(book_id):
    loans = Loan.query.filter_by(book_id=book_id).all()
    loan_list = [loan.to_dict() for loan in loans]
    json_data = json.dumps(loan_list, default=str)
    return json_data


@app.route('/loans/delete/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    db.session.delete(loan)
    db.session.commit()
    return {'message': 'Loan deleted successfully.'}


@app.route('/returnbook', methods=['POST'])
def return_book():
    data = request.get_json()
    cust_name = data['cust_name']
    bookname = data['bookname']

    loan = Loan.query.join(Customer).join(Book).filter(Customer.name == cust_name, Book.bookname == bookname).first()

    if not loan:
        return "No loan record found for the given customer and book."

    if not loan.book.loan_active:
        return "Book is already marked as returned."

    loan.book.loan_active = False
    loan.return_date = date.today()
    db.session.commit()

    return "Book returned successfully."


############# Loan end point ####################

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
