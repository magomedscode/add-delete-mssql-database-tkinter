import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from contextlib import closing
from functools import partial
import pyodbc

SERVER_NAME = 'DESKTOP-FC3VM4U\SQLEXPRESS'
DATABASE_NAME = 'MANAGEMENT'
CONNECTION_PARAMETERS = f'Driver={{SQL Server}};Server={SERVER_NAME};Database={DATABASE_NAME};Trusted_Connection=yes;'

SQL_CREATE_STUDENT_TABLE = """ 
IF OBJECT_ID(N'Student', N'U') IS NULL
    CREATE TABLE Student (
        student_id INT PRIMARY KEY,
        firstname VARCHAR(50) NOT NULL,
        lastname VARCHAR(50) NOT NULL,
        address VARCHAR(50) NOT NULL
    )
"""

SQL_INSERT_STUDENT = """ INSERT INTO Student (student_id, firstname, lastname, address) VALUES (?, ? , ? , ? )"""
SQL_DELETE_STUDENT = """ DELETE FROM Student where student_id = ? """
SQL_SELECT_STUDENT = """ SELECT student_id, firstname, lastname, address from Student """


def create_student_table(db_connection):
    with closing(db_connection.cursor()) as cursor:
         cursor.execute(SQL_CREATE_STUDENT_TABLE)
    print("Table 'student' created successfully.")


def add_student(db_connection, student_tree, student_id_textbox, firstname_textbox, lastname_textbox, address_textbox):
    student_id = student_id_textbox.get().strip()
    firstname = firstname_textbox.get().strip()
    lastname = lastname_textbox.get().strip()
    address = address_textbox.get().strip()

    if not student_id or not firstname or not lastname or not address:
        messagebox.showinfo("Error", "Please fill up all the fields")
    else:
        try:
            with closing(db_connection.cursor()) as cursor:
                cursor.execute(SQL_INSERT_STUDENT, (int(student_id), firstname, lastname, address))
            db_connection.commit()
        except Exception as e:
            messagebox.showinfo("Error", f"Failed to add data: {e}")
        messagebox.showinfo("Data added succesfully!")
        student_tree.insert("", "end", values=(student_id, firstname, lastname, address))

def del_student(db_connection, student_tree):
    selected_item = student_tree.focus()
    if selected_item:
        student_id = student_tree.item(selected_item, 'values')[0]

        try:
            with closing (db_connection.cursor()) as cursor:
                cursor.execute(SQL_DELETE_STUDENT, (int(student_id),))
            db_connection.commit()
            messagebox.showinfo(("Data deleted succesfully"))

            #remove selected item from treeview
            student_tree.delete(selected_item)
        except Exception as e:
            messagebox.showinfo("Error", f"Failed to delete data: {e}")

    else:
        messagebox.showinfo(("Error", "No student selected"))



# def load_students(db_connection, student_tree):
#     with closing(db_connection.cursor()) as cursor:
#         cursor.execute(SQL_SELECT_STUDENT)
#         for student_id, firstname, lastname, address in cursor:
#             print(student_id, firstname, lastname, address)
#             student_tree.insert("", "end", values=(student_id, firstname, lastname, address))


def load_students(db_connection, student_tree):
    with closing(db_connection.cursor()) as cursor:
        cursor.execute(SQL_SELECT_STUDENT)
        for student_id, firstname, lastname, address in cursor:
            student_tree.insert("", "end", values=(student_id, firstname, lastname, address))


def main():
    db_connection = pyodbc.connect(CONNECTION_PARAMETERS)

    root = tk.Tk()
    root.title("Student Registration System")
    student_tree = ttk.Treeview(root)

    textbox_frame = tk.Frame(root)
    textbox_frame.grid(row=0, column=0, padx=1, pady=1)
    tk.Label(textbox_frame, text="Student ID").grid(row=0, column=0, padx=1, pady=1, sticky=tk.E)
    student_id_textbox = tk.Entry(textbox_frame)
    student_id_textbox.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(textbox_frame, text="Firstname").grid(row=1, column=0, padx=1, pady=1, sticky=tk.E)
    firstname_textbox = tk.Entry(textbox_frame)
    firstname_textbox.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(textbox_frame, text="Lastname").grid(row=2, column=0, padx=1, pady=1, sticky=tk.E)
    lastname_textbox = tk.Entry(textbox_frame)
    lastname_textbox.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(textbox_frame, text="Address").grid(row=3, column=0, padx=1, pady=1, sticky=tk.E)
    address_textbox = tk.Entry(textbox_frame)
    address_textbox.grid(row=3, column=1, padx=5, pady=5)

    button_frame = tk.Frame(root)
    button_frame.grid(row=0, column=1, padx=1, pady=1)

    tk.Button(button_frame, text="Add",
              command=partial(add_student, db_connection, student_tree, student_id_textbox, firstname_textbox,
                              lastname_textbox, address_textbox),
              ).pack(padx=1, pady=5, fill=tk.X)

    tk.Button(button_frame, text="Delete", command=partial(del_student, db_connection , student_tree)).pack(padx=1, pady=5, fill=tk.X)

    student_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # define our columns
    student_tree['columns'] = ("Student ID", "Firstname", "Lastname", "Address")

    # format our columns
    student_tree.column("#0", width=0, stretch=0)
    student_tree.column("Student ID", width=100)
    student_tree.column("Firstname", width=150)
    student_tree.column("Lastname", width=150)
    student_tree.column("Address", width=200)

    # create heading
    student_tree.heading("Student ID", text="Student ID")
    student_tree.heading("Firstname", text="Firstname")
    student_tree.heading("Lastname", text="Lastname")
    student_tree.heading("Address", text="Address")

    create_student_table(db_connection)
    load_students(db_connection, student_tree)
    root.mainloop()


if __name__ == "__main__":
    main()