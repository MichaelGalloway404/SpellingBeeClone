import pymysql
import os
import sys

print("Starting script...")

if not os.path.isfile('words.txt'):
    print("Error: words.txt file not found.")
    sys.exit()

conn = None

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="spellingbee"
    )
    print("Connected to database!")
    cursor = conn.cursor()

    inserted = 0

    with open('words.txt', 'r') as file:
        for line in file:
            word = line.strip().lower()
            print(f"Read word: '{word}'")
            if word:
                try:
                    cursor.execute("INSERT IGNORE INTO valid_words (word) VALUES (%s)", (word,))
                    if cursor.rowcount == 1:
                        inserted += 1
                        print(f"Inserted: '{word}'")
                    else:
                        print(f"Skipped duplicate or failed insert: '{word}'")
                except pymysql.MySQLError as e:
                    print(f"Error inserting {word}: {e}")

    conn.commit()
    print(f"Words loaded successfully. {inserted} words inserted.")

except pymysql.MySQLError as err:
    print(f"Error connecting to MySQL: {err}")

finally:
    if conn:
        try:
            cursor.close()
            conn.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error during cleanup: {e}")





#444444444444444444444444444444444444444444444

# import mysql.connector
# import os
# import sys

# print("Starting script...")

# if not os.path.isfile('words.txt'):
#     print("Error: words.txt file not found.")
#     sys.exit()

# conn = None

# try:
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="root",
#         database="spellingbee"
#     )
#     print("Connected to database!")
#     cursor = conn.cursor()

#     inserted = 0

#     with open('words.txt', 'r') as file:
#         for line in file:
#             word = line.strip().lower()
#             print(f"Read word: '{word}'")
#             if word:  # only skip completely blank lines
#                 try:
#                     cursor.execute("INSERT IGNORE INTO valid_words (word) VALUES (%s)", (word,))
#                     if cursor.rowcount == 1:
#                         inserted += 1
#                         print(f"Inserted: '{word}'")
#                     else:
#                         print(f"Skipped duplicate or failed insert: '{word}'")
#                 except mysql.connector.Error as e:
#                     print(f"Error inserting {word}: {e}")

#     conn.commit()
#     print(f"Words loaded successfully. {inserted} words inserted.")

# except mysql.connector.Error as err:
#     print(f"Error connecting to MySQL: {err}")

# finally:
#     if conn and conn.is_connected():
#         cursor.close()
#         conn.close()
#         print("Connection closed.")


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4

# import pymysql

# print("start")

# # Connect to MySQL
# conn = pymysql.connect(
#     host="localhost",
#     user="root",
#     password="root"
# )

# try:
#     with conn.cursor() as cursor:
#         # Create database
#         cursor.execute("CREATE DATABASE IF NOT EXISTS testdb")
#         cursor.execute("USE testdb")

#         # Create table
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(100),
#             email VARCHAR(100)
#         )
#         """)

#         # Insert test data
#         cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("Alice", "alice@example.com"))
#         cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("Bob", "bob@example.com"))
#         cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("Charlie", "charlie@example.com"))

#         # Commit changes
#         conn.commit()

#         # Retrieve and print data
#         cursor.execute("SELECT * FROM users")
#         results = cursor.fetchall()
#         print("Users in database:")
#         for row in results:
#             print(row)

# finally:
#     conn.close()

# print("end")
