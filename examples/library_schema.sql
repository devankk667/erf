CREATE TABLE Book (
    book_id INT,
    title VARCHAR(255),
    isbn VARCHAR(20),
    PRIMARY KEY (book_id)
);

CREATE TABLE Author (
    author_id INT,
    name VARCHAR(255),
    PRIMARY KEY (author_id)
);

CREATE TABLE Member (
    member_id INT,
    name VARCHAR(255),
    join_date DATE,
    PRIMARY KEY (member_id)
);

CREATE TABLE Borrows (
    member_id INT,
    book_id INT,
    borrow_date DATE,
    PRIMARY KEY (member_id, book_id),
    FOREIGN KEY (member_id) REFERENCES Member(member_id),
    FOREIGN KEY (book_id) REFERENCES Book(book_id)
);