import psycopg2


def create_connection():
    conn = psycopg2.connect(
        database='clients_and_numbers',
        user='postgres',
        password=''
    )
    return conn


def create_database_struct(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clients(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(30),
                last_name VARCHAR(30),
                email VARCHAR(50)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS phones(
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                phone VARCHAR(20)
            );
        ''')

        conn.commit()


def add_new_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO clients(first_name, last_name, email)
            VALUES (%s, %s, %s) RETURNING id;
        ''', (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        conn.commit()
        return client_id


def add_ph_numb(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO phones (client_id, phone)
            VALUES (%s, %s);
        ''', (client_id, phone))
        conn.commit()


def change_client_info(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute('''UPDATE clients SET first_name = %s
                WHERE id = %s''', (first_name, client_id))
        if last_name:
            cur.execute('''UPDATE clients SET last_name = %s
                WHERE id = %s''', (last_name, client_id))
        if email:
            cur.execute('''UPDATE clients SET email = %s
                WHERE id = %s''', (email, client_id))
        conn.commit()


def del_phone(conn, phone_id):
    with conn.cursor() as cur:
        cur.execute('''DELETE FROM phones
                WHERE id = %s''', (phone_id,))
        conn.commit()


def del_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''DELETE FROM clients
                WHERE id = %s''', (client_id,))
        conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = '''SELECT clients.id, first_name, last_name, email, phones.phone 
                   FROM clients 
                   LEFT JOIN phones ON clients.id = phones.client_id '''

        if phone:
            query += 'WHERE phones.phone = %s'
            cur.execute(query, (phone,))
        elif first_name or last_name or email:
            query += "WHERE "
            params = []
            if first_name:
                query += 'first_name = %s AND '
                params.append(first_name)
            if last_name:
                query += 'last_name = %s AND '
                params.append(last_name)
            if email:
                query += 'email = %s AND '
                params.append(email)
            query = query.rstrip(" AND ")
            cur.execute(query, tuple(params))

        return cur.fetchall()


if __name__ == '__main__':
    conn = create_connection()

    create_database_struct(conn)

    # Добавляем клиента
    client_id = add_new_client(conn, "John", "Doe", "john.doe@example.com")

    # Добавляем телефон клиенту
    add_ph_numb(conn, client_id, "+1234567890")

    # Ищем клиента по имени
    clients = find_client(conn, first_name="John")
    print(clients)

    # Изменяем email клиента
    change_client_info(conn, client_id, email="new.email@example.com")

    # Удаляем телефон
    del_phone(conn, 1)

    # Удаляем клиента
    del_client(conn, client_id)

    conn.close()