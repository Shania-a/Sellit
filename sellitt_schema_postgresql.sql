

-- CREATE DATABASE sellitt_db;

-- Skapa tabell: programs
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL
);

-- Skapa tabell: courses
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL
);

-- Skapa tabell: program_courses (många-till-många mellan programs och courses)
CREATE TABLE program_courses (
    id SERIAL PRIMARY KEY,
    program_id INT REFERENCES programs(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE
);

-- Skapa tabell: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('student', 'alumn', 'admin')) NOT NULL,
    program_id INT REFERENCES programs(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skapa tabell: books
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100),
    publication_year INT,
    isbn VARCHAR(20)
);

-- Skapa tabell: ads
CREATE TABLE ads (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    book_id INT REFERENCES books(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id),
    price NUMERIC(8,2) NOT NULL,
    description TEXT,
    status VARCHAR(20) CHECK (status IN ('active', 'sold', 'draft')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skapa tabell: messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INT REFERENCES users(id) ON DELETE CASCADE,
    ad_id INT REFERENCES ads(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
