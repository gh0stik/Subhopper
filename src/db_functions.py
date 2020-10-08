import sqlite3
from sqlite3 import Error
from logger import log_debug

def create_connection():
    try:
        conn = sqlite3.connect("links.db")
        return conn
    except Error as e:
        log_debug("Error connecting to DB: " + str(e))


def create_emails_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE emails(
        id INTEGER,
        address TEXT NOT NULL,
        domain TEXT NOT NULL
        );""")
    except Error as e:
        pass


def create_subhopper_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE sub_domains(
        id INTEGER,
        subs TEXT NOT NULL,
        domain TEXT NOT NULL
        );""")
    except Exception:
        pass


def create_whois_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE whois(
        id INTEGER,
        description TEXT NOT NULL,
        domain TEXT NOT NULL,
        as_number INTEGER,
        as_country TEXT NOT NULL,
        cidr TEXT NOT NULL
        );""")
    except Error as e:
        pass


def create_historic_ips_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE historic_ips(
        id INTEGER,
        ip TEXT NOT NULL,
        domain TEXT NOT NULL
        );""")
    except Error as e:
        pass


def drop_emails_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""drop table emails""")
    except Error as e:
        print(e)


def drop_whois_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""drop table whois""")
    except Error as e:
        print(e)


def drop_historic_ips_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""drop table historic_ips""")
    except Error as e:
        print(e)


def drop_subhopper_table():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("""drop table sub_domains""")
    except Error as e:
        print(e)


def reset_emails_table():
    drop_emails_table()
    create_emails_table()


def reset_whois_table():
    drop_whois_table()
    create_whois_table()


def reset_historic_ips_table():
    drop_historic_ips_table()
    create_historic_ips_table()


def reset_subhopper_table():
    drop_subhopper_table()
    create_subhopper_table()


def all_db_reset():
    reset_emails_table()
    reset_whois_table()
    reset_historic_ips_table()
    reset_subhopper_table()


def check_if_email_exist(email, target):
    try:
        conn = create_connection()
        c = conn.cursor()
        check_existance = c.execute("""SELECT address FROM emails WHERE address like '{}' AND domain like '{}' """.format(email, target)).fetchall()
        if not check_existance:
            return False
        else:
            return True
    except Exception as e:
        log_debug("Error checking email table: " + str(e))


def check_if_historical_ip_exist(ip, target):
    try:
        conn = create_connection()
        c = conn.cursor()
        check_existance = c.execute("""SELECT ip FROM historic_ips WHERE ip like '{}' AND domain like '{}' """.format(ip, target)).fetchall()
        if not check_existance:
            return False
        else:
            return True
    except Exception as e:
        log_debug("Error checking historic_ips table: " + str(e))

def check_if_subdomain_exist(subdomain, target):
    conn = create_connection()
    c = conn.cursor()
    check_existance = c.execute("""SELECT subs FROM sub_domains WHERE subs like '{}' AND domain like '{}' """.format(subdomain, target)).fetchall()
    if not check_existance:
        return False
    else:
        return True


def check_if_whois_exist(cidr, target):
    conn = create_connection()
    c = conn.cursor()
    check_existance = c.execute("""SELECT cidr FROM whois WHERE cidr like '{}' AND domain like '{}' """.format(cidr, target)).fetchall()
    if not check_existance:
        return False
    else:
        return True


def get_emails_table_id():
    conn = create_connection()
    c = conn.cursor()
    id = c.execute("""SELECT id FROM emails WHERE 1 ORDER BY id DESC LIMIT 1""").fetchone()
    if id is None:
        return(1)
    else:
        return(id[0] + 1)


def get_whois_table_id():
    conn = create_connection()
    c = conn.cursor()
    id = c.execute("""SELECT id FROM whois WHERE 1 ORDER BY id DESC LIMIT 1""").fetchone()
    if not id:
        return(1)
    else:
        return(id[0] + 1)


def get_historic_ips_table_id():
    conn = create_connection()
    c = conn.cursor()
    id = c.execute("""SELECT id FROM historic_ips WHERE 1 ORDER BY id DESC LIMIT 1""").fetchone()
    if not id:
        return(1)
    else:
        return(id[0] + 1)


def get_subhopper_table_id():
    conn = create_connection()
    c = conn.cursor()
    id = c.execute("""SELECT id FROM sub_domains WHERE 1 ORDER BY id DESC LIMIT 1""").fetchone()
    if not id:
        return(1)
    else:
        return(id[0]+1)


def update_emails_table(email, targetdomain):
    id = get_emails_table_id()
    conn = create_connection()
    c = conn.cursor()
    if not check_if_email_exist(email, targetdomain):
        try:
            c.execute("""INSERT INTO emails VALUES(?, ?, ?)""", (id, email, targetdomain))
            conn.commit()
        except Error as e:
            print(e)


def update_sub_domains_table(subdomain, targetdomain):
    id = get_subhopper_table_id()
    conn = create_connection()
    c = conn.cursor()
    if not check_if_subdomain_exist(subdomain, targetdomain):
        try:
            c.execute("""INSERT INTO sub_domains VALUES(?, ?, ?)""", (id, subdomain, targetdomain))
            conn.commit()
        except Error as e:
            print(e)


def update_historical_ips_table(ip, targetdomain):
    id = get_historic_ips_table_id()
    conn = create_connection()
    c = conn.cursor()
    if not check_if_historical_ip_exist(ip, targetdomain):
        try:
            c.execute("""INSERT INTO historic_ips VALUES(?, ?, ?)""", (id, ip, targetdomain))
            conn.commit()
        except Error as e:
            print(e)


def update_whois_table(description, targetdomain, as_number, as_country, cidr):
    id = get_whois_table_id()
    conn = create_connection()
    c = conn.cursor()
    if not check_if_whois_exist(cidr, targetdomain):
        try:
            c.execute("""INSERT INTO whois VALUES(?, ?, ?, ?, ?, ?)""", (id, description, targetdomain, as_number, as_country, cidr))
            conn.commit()
        except Error as e:
            print(e)


def validate_existing_records_in_sub_domains_table(target):
    conn = create_connection()
    c = conn.cursor()
    check_existing_record = c.execute("""SELECT domain FROM sub_domains WHERE domain like '{}' LIMIT 1""".format(target)).fetchall()
    if check_existing_record:
        return True
    else:
        return False

def validate_existing_records_in_emails_table(target):
    conn = create_connection()
    c = conn.cursor()
    check_existing_record = c.execute("""SELECT domain FROM emails WHERE domain like '{}' LIMIT 1""".format(target)).fetchall()
    if check_existing_record:
        return True
    else:
        return False


def check_subdomain(domain):
    conn = create_connection()
    c = conn.cursor()
    check_existance = c.execute("""SELECT subs FROM sub_domains WHERE domain like '{}' """.format(domain)).fetchall()
    conn.close()
    return check_existance


def check_historical_ips(domain):
    conn = create_connection()
    c = conn.cursor()
    check_existance = c.execute("""SELECT ip FROM historic_ips WHERE domain like '{}' """.format(domain)).fetchall()
    conn.close()
    return check_existance


def check_emails(domain):
    conn = create_connection()
    c = conn.cursor()
    check_existance = c.execute("""SELECT address FROM emails WHERE domain like '{}' """.format(domain)).fetchall()
    conn.close()
    return check_existance


def check_asns(domain):
    conn = create_connection()
    c = conn.cursor()
    check_existance = c.execute("""SELECT * FROM whois WHERE domain like '{}' """.format(domain)).fetchall()
    conn.close()
    return check_existance

def remove_rows(domain):
    conn = create_connection()
    c = conn.cursor()
    if validate_existing_records_in_sub_domains_table(domain):
        c.execute("""DELETE FROM sub_domains WHERE domain = '{}' """.format(domain))
        c.execute("""DELETE FROM emails WHERE domain = '{}' """.format(domain))
        c.execute("""DELETE FROM historic_ips WHERE domain = '{}' """.format(domain))
        conn.commit()
        return True
    else:
        return False


def get_stats():
    conn = create_connection()
    c = conn.cursor()
    try:
        distinct_domains = c.execute(""" SELECT count(DISTINCT domain) FROM sub_domains """).fetchone()[0]
        total_subdomains = c.execute(""" SELECT count(subs) FROM sub_domains """).fetchone()[0]
        total_historic_ips = c.execute(""" SELECT count(ip) FROM historic_ips """).fetchone()[0]
        total_emails = c.execute(""" SELECT count(address) FROM emails """).fetchone()[0]
        return {"total_subdomains":total_subdomains, "distinct_domains":distinct_domains, "total_historic_ips":total_historic_ips, "total_emails":total_emails}
    except Error as e:
        print(e)

