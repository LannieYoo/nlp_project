import sqlite3
conn = sqlite3.connect(r'c:\Users\40270\Desktop\workspace\nlp\data\chunks.db')
c = conn.cursor()

# Check books table
c.execute("SELECT sql FROM sqlite_master WHERE name='books'")
print(c.fetchone()[0])
print()

c.execute("SELECT * FROM books ORDER BY title")
books = c.fetchall()
print(f"Total books: {len(books)}")
for b in books:
    print(f"  {b}")

c.execute("SELECT COUNT(*) FROM chunks")
print(f"\nTotal chunks: {c.fetchone()[0]}")
conn.close()
