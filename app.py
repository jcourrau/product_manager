from tkinter import ttk
from tkinter import *
import customtkinter as ct  # For a more modern style
from datetime import datetime
from models import Product
from db import session, Base, engine
import json

Base.metadata.create_all(engine)


# Load categories from categories.json
def load_categories():
    with open("categories.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        categories = data.get("categories", [""]) # Default to ["-"] if no categories found
        print(f" Categories loaded: {categories}")
        return categories


# Replace the hardcoded list with the dynamic one
category_list = load_categories()

'''
> Implemented Improvements
1. Use Custom TKinter to enhance the interface.
2. Add ID to the table.
3. Display the product's creation date.
4. Confirmation window for deleting products.
5. Simplified editing window (only 2 fields).
6. Combine messages into one method (row, color, window...).
7. Messages that disappear after a while.
8. Add categories via ct.CTkOptionMenu.
9. Add a category column.
10. Use a single frame to create/edit products.
11. Verify if the name already exists.
12. Exception handling if the database fails.
13. Exceptions in all methods.
14. Implement SQLAlchemy.
15. Disabled add button while editing a product.

> Pending Improvements
* Add search bar.
* 
'''


class MainWindow:
    db = "database/products.db"

    def __init__(self, root, percentage=0.3):
        self.window = root
        self.window.title("Product Manager")
        self.window.resizable(False, True)  # Allow resizing
        self.window.wm_iconbitmap("resources/icon.ico")
        self.window.geometry("450x600")  # Initial size

        # Configuration to center everything in the window
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=0)  # Top frame
        self.window.grid_rowconfigure(1, weight=0)  # Space for Message
        self.window.grid_rowconfigure(2, weight=1)  # Table (main)
        self.window.grid_rowconfigure(3, weight=0)  # Space for Message
        self.window.grid_rowconfigure(4, weight=0)  # Buttons

        # Top frame
        self.create_top_frame(
            parent=self.window,
            frame_title="Add Product",
            button_text="Edit Product",
            button_command=self.add_product
        )

        # Product Table
        self.setup_table()

        # Buttons
        self.setup_buttons()

        # Retrieve products
        self.get_products()

    ''' Interface Functions '''

    def create_top_frame(self, parent, frame_title, button_text, button_command, row=0, category="", name="", price=""):
        """
        Creates a generic top frame with name, price, and category fields.
        """
        global category_list
        categories = category_list

        # Frame
        frame = ct.CTkFrame(parent, corner_radius=10)
        frame.grid(row=row, column=0, sticky="new", pady=(20, 5), padx=20)
        pady_val = 5
        padx_val = 10
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Title
        bold_font = ("Arial", 14, "bold")
        ct.CTkLabel(
            frame,
            text=frame_title,
            font=bold_font
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            pady=(pady_val, 0),
            sticky="ew"
        )

        # Name Entry
        ct.CTkLabel(
            frame,
            text="Name: "
        ).grid(
            row=1,
            column=0,
            pady=pady_val,
            padx=(padx_val, 5),
            sticky="e"
        )
        self.name_entry = ct.CTkEntry(
            frame,
            textvariable=StringVar(parent, value=name)
        )
        self.name_entry.grid(
            row=1,
            column=1,
            pady=pady_val,
            padx=(0, padx_val),
            sticky="w")

        self.name_entry.focus()

        # Price Entry
        ct.CTkLabel(
            frame,
            text="Price: "
        ).grid(
            row=2,
            column=0,
            pady=pady_val,
            padx=(padx_val, 5),
            sticky="e"
        )
        self.price_entry = ct.CTkEntry(
            frame,
            textvariable=StringVar(parent, value=price)
        )
        self.price_entry.grid(
            row=2,
            column=1,
            pady=pady_val,
            padx=(0, padx_val),
            sticky="w"
        )

        # Category Dropdown
        ct.CTkLabel(
            frame,
            text="Category: "
        ).grid(
            row=3,
            column=0,
            pady=pady_val,
            padx=(padx_val, 5),
            sticky="e"
        )
        self.category_menu = ct.CTkOptionMenu(
            frame,
            values=categories
        )
        self.category_menu.grid(
            row=3,
            column=1,
            pady=pady_val,
            padx=(0, padx_val),
            sticky="w"
        )
        self.category_menu.set(category)  # Initial empty value
        header_color = "#343638"
        text_color = "#dce4ee"
        self.category_menu.configure(
            fg_color=header_color,  # Background color of the menu
            text_color=text_color  # Text color
        )  # Change colors

        # Main Button
        self.product_button = ct.CTkButton(
            frame,
            text=button_text,
            width=200,
            command=button_command
        )
        self.product_button.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="n",
            pady=(10, 15),
            padx=padx_val
        )

    def setup_table(self, row=2):
        header_color = "#343638"
        field_color = "#2b2b2b"
        text_color = "#dce4ee"
        rounded_corners = 7

        # Container with background and rounded corners
        table_container = ct.CTkFrame(self.window, corner_radius=rounded_corners)
        table_container.grid(row=row, column=0, sticky="nsew", padx=20, pady=(10, 7))

        # Table Configuration
        style = ttk.Style()
        style.theme_use('default')

        # Row Style
        style.configure(
            "mystyle.Treeview",
            highlightthickness=0,
            bd=0,
            font=('Arial', 14),
            background=field_color,
            foreground=text_color,
            fieldbackground=field_color
        )

        style.map(
            "mystyle.Treeview",
            background=[('selected', '#1f6aa5')],
            foreground=[('selected', text_color)]
        )  # Row selection colors

        # Header Style
        style.configure(
            "mystyle.Treeview.Heading",
            font=('Arial', 16, 'bold'),
            background=header_color,
            foreground=text_color,
            padding=[5, 10, 5, 10],
            relief="none"
        )

        style.map(
            "mystyle.Treeview.Heading",
            background=[("active", header_color)],  # Keep original color on hover
            foreground=[("active", text_color)],  # Keep text white
            relief=[("active", "none")]
        )  # Header effects

        style.layout(
            "mystyle.Treeview",
            [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]
        )  # Remove borders

        # Table Structure
        self.table = ttk.Treeview(
            table_container,
            height=20,
            columns=("ID", "Name", "Price"),  # Add "ID" column
            style="mystyle.Treeview"
        )
        self.table.pack(
            fill="both",
            expand=True,
            padx=rounded_corners,
            pady=rounded_corners)

        # Headers
        self.table.heading('#0', text='  ID', anchor=W)
        self.table.heading('#1', text='Name', anchor=CENTER)
        self.table.heading('#2', text='Price', anchor=W)
        self.table.heading('#3', text='Category', anchor=W)

        # Configure column widths
        self.table.column('#0', minwidth=20, width=90, anchor=W, stretch=NO)
        self.table.column('#1', minwidth=220, anchor=W, stretch=YES)
        self.table.column('#2', minwidth=120, width=120, anchor=W, stretch=YES)
        self.table.column('#3', minwidth=200, anchor=W, stretch=YES)

    def setup_buttons(self, row=4):
        # Padding
        outer_pad = 50
        inner_pad = 6

        # Frame
        buttons_frame = ct.CTkFrame(self.window)
        buttons_frame.grid(row=row, column=0, sticky="we", padx=20, pady=(7, 20))

        # Center grid
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Delete Button
        self.button_del = ct.CTkButton(buttons_frame, text='Delete', command=self.delete_product)
        self.button_del.grid(
            row=0,
            column=0,
            sticky="we",
            padx=(outer_pad, inner_pad),
            pady=inner_pad * 2
        )

        # Edit Button
        self.button_edit = ct.CTkButton(buttons_frame, text='Edit', command=self.edit_product)
        self.button_edit.grid(
            row=0,
            column=1,
            sticky="we",
            padx=(inner_pad, outer_pad),
            pady=inner_pad * 2
        )

    def show_message(self, text, row=1, color="red", duration=3000, pady=(5, 0), padx=20, show_window=None):
        """
        Displays a message in the main window for a limited time.

        Args:
            text (str): The message text.
            row (int): The row where the message should be displayed.
            color (str): The message text color.
            duration (int): Time in milliseconds before hiding the message.
            pady: Y Padding
            padx: X Padding
            show_window: The window where the message will be displayed. Default is self.window.
        """
        if show_window is None:
            show_window = self.window

        message = ct.CTkLabel(
            show_window,
            text=text,
            text_color=color,
            height=20
        )
        message.grid(
            row=row,
            column=0,
            pady=pady,
            padx=padx,
            sticky="we"
        )

        # Automatically hide the message after `duration` ms
        def hide_message():
            if message.winfo_exists():  # Verify if the widget still exists
                message.grid_remove()

        self.window.after(duration, hide_message)

    ''' Database Functions '''

    def get_products(self):

        # Clear the interface table before displaying the products
        self.table.delete(*self.table.get_children())

        # Query all products in the database, ordered by category
        products = session.query(Product).order_by(Product.category.desc()).all()

        # Insert each product into the table
        for product in products:
            self.table.insert(
                "",
                0,
                text=product.id,  # ID Column
                values=(product.name, product.price, product.category)  # Columns Name, Price, Category
            )

    ''' Interactions '''

    def price_validation(self, price):
        try:
            float(price)
            return True
        except ValueError:
            return False

    def verifications(self, name, price, category, window=None, add_mode=True):

        # Name validation
        if not name.strip() != "":
            print("Name is required.")
            self.show_message(
                "Name is required.",
                row=1, show_window=window)
            return False

        # Check for duplicate names when adding a new product.
        if add_mode:
            for row_id in self.table.get_children():
                existing_name = self.table.item(row_id, 'values')[0]  # Name Column
                if name.lower() == existing_name.lower():  # Compare names in lowercase.
                    self.show_message(
                        f"The product with name '{name}' already exists.",
                        row=1, show_window=window)
                    return False

        # Price validation
        if not self.price_validation(price):
            print("Price is required.")
            self.show_message(
                "Price is required.",
                row=1, show_window=window)
            return False

        # Validate that the price is not 0
        if float(price) <= 0:
            print("Price must be greater than 0.")
            self.show_message(
                "Price must be greater than 0.",
                row=1, show_window=window)
            return False

        # Category validation
        if category == "":
            self.show_message(
                "Select a category.",
                row=1, show_window=window)
            return False

        return True

    def add_product(self):
        """
        Adds a product by first validating its name and price.
        """
        # Variables
        name = self.name_entry.get()
        price = self.price_entry.get()
        category = self.category_menu.get()
        current_datetime = datetime.now()

        # Validations
        if not self.verifications(name, price, category):
            return  # Exit if validations fail

        # Create a new Product object
        new_product = Product(name=name, price=price, category=category, created_date=current_datetime)
        session.add(new_product)
        session.commit()

        # Success messages
        print(f"Product added successfully: {name} - ${price} - {current_datetime}")
        self.show_message(
            f"Product '{name}' added.",
            color="#dce4ee")

        # Clear input fields
        self.name_entry.delete(0, END)
        self.price_entry.delete(0, END)

        # Update table
        self.get_products()

    def delete_product(self):
        try:
            selected_item = self.table.selection()
            if not selected_item:
                self.show_message(
                    "Please select a product to delete.",
                    row=3, pady=0)
                return

            # Get the ID of the selected product
            prod_id = self.table.item(self.table.selection())['text']
            prod_name = self.table.item(self.table.selection())['values'][0]

            # Confirmation window
            confirm = ConfirmWindow(self)
            if not confirm.result:
                print("Product not deleted.")
                return  # Do not delete if canceled

            # Delete product from the database
            session.query(Product).filter_by(id=prod_id).delete()
            session.commit()

            # Show success message
            self.show_message(
                f"Product '{prod_name}' deleted successfully.",
                row=3, color="#dce4ee", pady=0)

            # Update the table
            self.get_products()
        except Exception as e:
            # Show message if no product is selected
            self.show_message(
                f"Error deleting product: {e}",
                row=3, pady=0)

    def edit_product(self):
        try:
            selected_item = self.table.selection()
            if not selected_item:
                self.show_message(
                    "Please select a product.",
                    row=3, pady=0)
                return

            # Get selected product
            prod_id = self.table.item(self.table.selection())['text']
            product = session.query(Product).filter_by(id=prod_id).first()
            if product:
                EditWindow(self, product)  # Pass the product object to the editing window

        except Exception as e:
            # Show message if no product is selected
            self.show_message(
                f"Error editing product: {e}",
                row=3, pady=0)


class EditWindow:

    def __init__(self, main_window, product):
        self.main_window = main_window
        self.product = product

        # Disable Edit Product button in MainWindow while editing
        self.main_window.product_button.configure(state="disabled")

        # Window configuration
        self.edit_window = ct.CTkToplevel()
        self.edit_window.title("Edit Product")
        self.edit_window.resizable(False, False)  # Allow resizing
        self.edit_window.wm_iconbitmap("resources/icon.ico")
        self.edit_window.geometry("400x260")  # Initial size

        # Configuration to center everything in the window
        self.edit_window.grid_columnconfigure(0, weight=1)
        self.edit_window.grid_rowconfigure(0, weight=0)  # Top frame
        self.edit_window.grid_rowconfigure(1, weight=0)  # Message
        self.edit_window.grid_rowconfigure(2, weight=1)  # Main table

        # Frame
        self.main_window.create_top_frame(
            parent=self.edit_window,
            frame_title="Edit Product",
            button_text="Update Product",
            button_command=self.update_product,
            name=self.product.name,
            price=self.product.price,
            category=self.product.category
        )

    def update_product(self):
        new_name = self.main_window.name_entry.get()
        new_price = self.main_window.price_entry.get()
        new_category = self.main_window.category_menu.get()

        # Validations
        if not self.main_window.verifications(
                name=new_name, price=new_price, category=new_category, window=self.edit_window, add_mode=False
        ):
            return  # Exit if validations fail

        # Update the object's values
        self.product.name = new_name
        self.product.price = new_price
        self.product.category = new_category
        session.commit()

        # Success message
        self.main_window.show_message(
            f'The product {self.product.name} has been successfully updated.',
            row=3, color="#dce4ee", pady=0)

        self.edit_window.destroy()
        self.main_window.get_products()

        # Recreate main window to be able to add new products again.
        self.main_window.create_top_frame(
            parent=self.main_window.window,
            frame_title="Add Product",
            button_text="Edit Product",
            button_command=self.main_window.add_product
        )

        # Re-enable Edit Product button in MainWindow
        self.main_window.product_button.configure(state="normal")


class ConfirmWindow:

    def __init__(self, main_window):
        self.main_window = main_window
        self.result = None  # Variable to store the user's selection

        # Window configuration
        self.confirm_window = ct.CTkToplevel()
        self.confirm_window.title("Confirm Deletion")
        self.confirm_window.resizable(False, False)
        self.confirm_window.geometry("300x150")
        self.confirm_window.grid_columnconfigure(0, weight=1)
        self.confirm_window.grid_rowconfigure(0, weight=1)

        # Message
        ct.CTkLabel(
            self.confirm_window,
            text="Are you sure you want to delete this product?",
            font=("Arial", 14),
            wraplength=250,
            justify="center"
        ).grid(row=0, column=0, pady=(20, 10), padx=20)

        # Frame for buttons
        button_frame = ct.CTkFrame(self.confirm_window)
        button_frame.grid(row=1, column=0, pady=10)

        # Configure columns to center buttons
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Confirm Button
        ct.CTkButton(
            button_frame,
            text="Confirm",
            command=self.confirm
        ).grid(row=0, column=0, padx=(10, 5), pady=5, sticky="e")

        # Cancel Button
        ct.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).grid(row=0, column=1, padx=(5, 10), pady=5, sticky="w")

        # Block execution until the window is closed
        self.confirm_window.wait_window()

    def confirm(self):
        self.result = True
        self.confirm_window.destroy()

    def cancel(self):
        self.result = False
        self.confirm_window.destroy()


if __name__ == "__main__":
    root = ct.CTk()  # Crear la ventana principal con customtkinter
    app = MainWindow(root)
    root.mainloop()
