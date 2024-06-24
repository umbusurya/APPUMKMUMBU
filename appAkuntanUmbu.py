import streamlit as st
import sqlite3
import hashlib
import pandas as pd

# Fungsi untuk meng-hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk membuat tabel pengguna
def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan pengguna baru ke database
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, hash_password(password)))
    conn.commit()
    conn.close()

# Fungsi untuk memeriksa apakah pengguna sudah ada
def user_exists(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    data = c.fetchall()
    conn.close()
    return len(data) > 0

# Fungsi untuk memeriksa kredensial pengguna
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    data = c.fetchall()
    conn.close()
    return data

# Fungsi untuk membuat tabel transaksi
def create_transaction_table():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY,
        username TEXT,
        type TEXT,
        amount REAL,
        description TEXT,
        date TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan transaksi
def add_transaction(username, type, amount, description, date):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute('INSERT INTO transactions(username, type, amount, description, date) VALUES (?, ?, ?, ?, ?)', 
              (username, type, amount, description, date))
    conn.commit()
    conn.close()

# Fungsi untuk mendapatkan transaksi
def get_transactions(username):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute('SELECT * FROM transactions WHERE username = ?', (username,))
    data = c.fetchall()
    conn.close()
    return data

# Halaman registrasi
def register():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Register"):
        create_user_table()
        if user_exists(username):
            st.warning("Username sudah ada. Silakan pilih username lain atau login.")
        else:
            add_user(username, password)
            st.success("Anda telah berhasil terdaftar!")
            st.info("Silakan login ke akun Anda.")
            st.session_state.page = "Login"
    if st.button("Sudah punya akun? Login di sini"):
        st.session_state.page = "Login"

# Halaman login
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        create_user_table()
        create_transaction_table()  # Pastikan tabel transaksi dibuat saat login
        result = login_user(username, password)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Main"
        else:
            st.warning("Username atau password salah")
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state.page = "Register"

# Halaman utama aplikasi akuntansi
def main_app():
    st.title("Aplikasi Akuntansi UMKM")
    st.write(f"Selamat datang, {st.session_state.username}!")
    
    menu = ["Dashboard", "Tambah Pendapatan", "Tambah Pengeluaran", "Laporan Keuangan"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Dashboard":
        st.subheader("Dashboard")
        transactions = get_transactions(st.session_state.username)
        if transactions:
            df = pd.DataFrame(transactions, columns=["ID", "Username", "Type", "Amount", "Description", "Date"])
            st.dataframe(df)
            total_income = df[df['Type'] == 'Income']['Amount'].sum()
            total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
            balance = total_income - total_expense
            st.write(f"Total Pendapatan: {total_income}")
            st.write(f"Total Pengeluaran: {total_expense}")
            st.write(f"Saldo: {balance}")
        else:
            st.write("Belum ada transaksi.")

    elif choice == "Tambah Pendapatan":
        st.subheader("Tambah Pendapatan")
        amount = st.number_input("Jumlah", min_value=0.0, format="%f")
        description = st.text_area("Deskripsi")
        date = st.date_input("Tanggal")
        if st.button("Tambah"):
            add_transaction(st.session_state.username, "Income", amount, description, date)
            st.success("Pendapatan berhasil ditambahkan")

    elif choice == "Tambah Pengeluaran":
        st.subheader("Tambah Pengeluaran")
        amount = st.number_input("Jumlah", min_value=0.0, format="%f")
        description = st.text_area("Deskripsi")
        date = st.date_input("Tanggal")
        if st.button("Tambah"):
            add_transaction(st.session_state.username, "Expense", amount, description, date)
            st.success("Pengeluaran berhasil ditambahkan")

    elif choice == "Laporan Keuangan":
        st.subheader("Laporan Keuangan")
        transactions = get_transactions(st.session_state.username)
        if transactions:
            df = pd.DataFrame(transactions, columns=["ID", "Username", "Type", "Amount", "Description", "Date"])
            st.dataframe(df)
            total_income = df[df['Type'] == 'Income']['Amount'].sum()
            total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
            balance = total_income - total_expense
            st.write(f"Total Pendapatan: {total_income}")
            st.write(f"Total Pengeluaran: {total_expense}")
            st.write(f"Saldo: {balance}")
        else:
            st.write("Belum ada transaksi.")

# Halaman logout
def logout():
    st.session_state.logged_in = False
    st.session_state.page = "Login"
    st.success("Anda telah logout.")

# Routing halaman
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "Register"

if st.session_state.logged_in:
    main_app()
    if st.button("Logout"):
        logout()
else:
    if st.session_state.page == "Register":
        register()
    elif st.session_state.page == "Login":
        login()
