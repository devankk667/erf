CREATE TABLE Guest (
    guest_id INT,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    PRIMARY KEY (guest_id)
);

CREATE TABLE Room (
    room_id INT,
    room_number VARCHAR(10),
    room_type VARCHAR(50),
    price_per_night DECIMAL(10,2),
    PRIMARY KEY (room_id)
);

CREATE TABLE Booking (
    booking_id INT,
    check_in_date DATE,
    check_out_date DATE,
    total_amount DECIMAL(10,2),
    PRIMARY KEY (booking_id)
);