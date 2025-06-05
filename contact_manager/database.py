import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / 'contacts.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
);
'''

def init_db(db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()


def add_contact(first_name, last_name, email, phone, address, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO contacts (first_name, last_name, email, phone, address) VALUES (?, ?, ?, ?, ?)',
        (first_name, last_name, email, phone, address)
    )
    conn.commit()
    conn.close()


def update_contact(contact_id, first_name, last_name, email, phone, address, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        'UPDATE contacts SET first_name=?, last_name=?, email=?, phone=?, address=? WHERE id=?',
        (first_name, last_name, email, phone, address, contact_id)
    )
    conn.commit()
    conn.close()


def delete_contact(contact_id, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('DELETE FROM contacts WHERE id=?', (contact_id,))
    conn.commit()
    conn.close()


def get_contacts(order_by='first_name', search=None, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    query = 'SELECT id, first_name, last_name, email, phone, address FROM contacts'
    params = []
    if search:
        query += ' WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?'
        s = f'%{search}%'
        params.extend([s, s, s])
    if order_by:
        query += f' ORDER BY {order_by}'
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def import_from_csv(csv_file, db_file=DB_FILE):
    import csv
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = row.get('First Name') or row.get('Given Name') or ''
            last = row.get('Last Name') or row.get('Family Name') or ''
            email = row.get('E-mail Address') or row.get('E-mail 1 - Value') or ''
            phone = row.get('Phone 1 - Value') or row.get('Business Phone') or ''
            address = row.get('Address 1 - Formatted') or row.get('Business Street') or ''
            cur.execute(
                'INSERT INTO contacts (first_name, last_name, email, phone, address) VALUES (?, ?, ?, ?, ?)',
                (first, last, email, phone, address)
            )
    conn.commit()
    conn.close()
