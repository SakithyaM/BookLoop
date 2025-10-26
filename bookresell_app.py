import streamlit as st
import book_functions as bf

st.title("Book Loop")

if "user" not in st.session_state:
    st.session_state.user = None
if "edit_book_id" not in st.session_state:
    st.session_state.edit_book_id = None

#---------- Login / Register ----------
if st.session_state.user is None:
    st.subheader("Login / Register")
    choice = st.radio("Choose an option", ["Login", "Register"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = bf.login_user(username, password)
            if user:
                st.session_state.user = {"username": username, "role": user["role"]}
                st.success(f"Logged in as {username} ({user['role']})")
                st.rerun()
            else:
                st.error("Invalid username or password")
    else:
        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")
        role = st.selectbox("Select your role", ["buyer", "seller"])
        if st.button("Register"):
            success = bf.register_user(username, password, role)
            if success:
                st.success("Registration successful!")
            else:
                st.error("Username already exists.")

else:
    user = st.session_state.user
    st.sidebar.write(f"Logged in as: {user['username']} ({user['role']})")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.edit_book_id = None
        st.rerun()

    role = user["role"]

    # ---------- Seller Page ----------
    if role == "seller":
        st.header("Seller Page")

        st.subheader("Add a Book")
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            price = st.number_input("Price (LKR)", min_value=0.0)
            category = st.text_input("Category (e.g. Science, Business, IT, Fantasy)")
            district = st.text_input("District")
            submitted = st.form_submit_button("Add Book")

            if submitted:
                if title and author:
                    bf.add_book(title, author, price, category, district, user["username"])
                    st.success("Book added successfully!")
                    st.rerun()
                else:
                    st.warning("Please fill in at least Title and Author.")

        st.subheader("Your Books")
        books = bf.load_books()
        for b in books:
            if b["seller"] == user["username"]:
                status = "SOLD" if b.get("sold", False) else "AVAILABLE"
                st.write(f"{b['title']}  — {b['author']} — LKR {b['price']} | {b['category']} | {b['district']} | {status}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Delete {b['title']}", key=f"del_{b['id']}"):
                        bf.delete_book(b["id"])
                        st.success("Book deleted!")
                        st.rerun()
                with col2:
                    if not b.get("sold", False) and st.button(f"Edit {b['title']}", key=f"edit_{b['id']}"):
                        st.session_state.edit_book_id = b["id"]
                        st.rerun()

        if st.session_state.edit_book_id:
            st.info("Edit Book Details")
            books = bf.load_books()
            book_to_edit = next((b for b in books if b["id"] == st.session_state.edit_book_id), None)
            if book_to_edit:
                with st.form("edit_book_form", clear_on_submit=True):
                    new_title = st.text_input("New Title", book_to_edit["title"])
                    new_author = st.text_input("New Author", book_to_edit["author"])
                    new_price = st.number_input("New Price", value=float(book_to_edit["price"]))
                    new_category = st.text_input("New Category", book_to_edit["category"])
                    new_district = st.text_input("New District", book_to_edit["district"])
                    save_changes = st.form_submit_button("Save Changes")
                    cancel_edit = st.form_submit_button("Cancel Edit")
                    if save_changes:
                        bf.edit_book(book_to_edit["id"], new_title, new_author, new_price, new_category, new_district)
                        st.success("Book updated successfully!")
                        st.session_state.edit_book_id = None
                        st.rerun()
                    elif cancel_edit:
                        st.session_state.edit_book_id = None
                        st.rerun()

    # ---------- Buyer Page ----------
    elif role == "buyer":
        st.header("Browse Books")

        col1, col2, col3 = st.columns(3)
        with col1:
            keyword = st.text_input("Search by title or author")
        with col2:
            category = st.text_input("Category")
        with col3:
            district = st.text_input("District")

        results = bf.search_books(keyword, category, district)
        books = bf.load_books()

        if results:
            for b in results:
                status = "SOLD" if b.get("sold", False) else "AVAILABLE"
                st.write(f"{b['title']}  by {b['author']} — LKR {b['price']} | {b['category']} | {b['district']} (Seller: {b['seller']}) — {status}")
                if not b.get("sold", False):
                    if st.button(f"Mark as Purchased ({b['title']})", key=f"buy_{b['id']}"):
                        for book in books:
                            if book["id"] == b["id"]:
                                book["sold"] = True
                                bf.save_books(books)
                                commission = bf.add_commission(b["price"], b["title"], b["seller"])
                                st.success(f"Book purchased! Admin earned LKR {commission:.2f} commission.")
                                st.rerun()
        else:
            st.info("No books found.")

    # ---------- ADMIN PAGE ----------
    elif role == "admin":
        st.header("Admin Page")

        st.subheader("Profits")
        profit_data = bf.load_admin_profit()
        st.metric("Total Profit (LKR)", f"{profit_data['total_profit']:.2f}")

        with st.expander("View Profits Details"):
            for t in profit_data["transactions"]:
                st.write(f"{t['book']} — Seller: {t['seller']} — Commission: LKR {t['commission']:.2f}")

        st.subheader("Manage Users")
        users = bf.load_users()
        for uname, details in users.items():
            st.write(f"{uname} — {details['role']}")
            if uname != user["username"]:
                if st.button(f"Delete User: {uname}", key=f"du_{uname}"):
                    bf.delete_user(uname)
                    st.warning(f"User '{uname}' deleted!")
                    st.rerun()

        st.subheader("Manage Books")
        books = bf.load_books()
        for b in books:
            st.write(f"{b['title']} by {b['author']} — {b['category']} | {b['district']} | Seller: {b['seller']}")
            if st.button(f"Delete Book {b['title']}", key=f"db_{b['id']}"):
                bf.delete_book(b["id"])
                st.warning("Book deleted.")
                st.rerun()
