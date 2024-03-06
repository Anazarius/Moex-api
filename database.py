import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
)

mycursor = mydb.cursor()

def setup_database():
    mycursor.execute("CREATE DATABASE IF NOT EXISTS Share2024")
    mycursor.execute("USE Share2024")

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Statuses (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            description VARCHAR(80) NOT NULL,
            reward INT UNSIGNED
        )
    """)

    mycursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_value_statuses
        BEFORE INSERT ON Statuses
        FOR EACH ROW
        BEGIN
            IF NEW.id > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: id value exceeds maximum allowed value(max=999999)';
            END IF;
            IF NEW.reward > 9999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: reward value exceeds maximum allowed value(max=9999)';
            END IF;
        END;
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(15) NOT NULL,
            last_name VARCHAR(20) NOT NULL,
            password VARCHAR(16) NOT NULL,
            balance FLOAT(8,2),
            status_id INT UNSIGNED NOT NULL,
            FOREIGN KEY (status_id) REFERENCES Statuses(id)
        )
    """)

    mycursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_value_users
        BEFORE INSERT ON Users
        FOR EACH ROW
        BEGIN
            IF NEW.id > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: id value exceeds maximum allowed value(max=999999)';
            END IF;
        END;
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Shares (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            tag VARCHAR(10) NOT NULL,
            type VARCHAR(30) NOT NULL
        )
    """)

    mycursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_value_shares
        BEFORE INSERT ON Shares
        FOR EACH ROW
        BEGIN
            IF NEW.id > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: id value exceeds maximum allowed value(max=999999)';
            END IF;
        END;
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS User_share (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNSIGNED NOT NULL,
            share_id INT UNSIGNED NOT NULL,
            count INT UNSIGNED NOT NULL,
            data_purchase DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (share_id) REFERENCES Shares(id)
        )
    """)

    mycursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_value_user_share
        BEFORE INSERT ON User_share
        FOR EACH ROW
        BEGIN
            IF NEW.id > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: id value exceeds maximum allowed value(max=999999)';
            END IF;
            IF NEW.count > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: count value exceeds maximum allowed value(max=999999)';
            END IF;
        END;
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Favorites (
            user_id INT UNSIGNED NOT NULL,
            share_id INT UNSIGNED NOT NULL,
            PRIMARY KEY (user_id, share_id),
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (share_id) REFERENCES Shares(id)
        )
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Data (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            tag VARCHAR(10) NOT NULL,
            tradedate DATE NOT NULL,
            volume BIGINT UNSIGNED NOT NULL,
            numtrades INT UNSIGNED NOT NULL,
            low FLOAT(8,2) NOT NULL,
            high FLOAT(8,2) NOT NULL,
            open FLOAT(8,2) NOT NULL,
            close FLOAT(8,2) NOT NULL
        )
    """)

    mycursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_value_data
        BEFORE INSERT ON Data
        FOR EACH ROW
        BEGIN
            IF NEW.id > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: id value exceeds maximum allowed value(max=999999)';
            END IF;
            IF NEW.volume > 999999999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: volume value exceeds maximum allowed value(max=999999999999)';
            END IF;
            IF NEW.numtrades > 999999 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: numtrades value exceeds maximum allowed value(max=999999)';
            END IF;
        END;
    """)

    mydb.commit()

if __name__ == "__main__":
    setup_database()
