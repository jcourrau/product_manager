from sqlalchemy import Column, Integer, String, Float, DateTime
import db  # Import the database configuration from db.py


class Product(db.Base):
    # Table Configuration
    __tablename__ = "product"

    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    created_date = Column(DateTime, nullable=False)

    # Initialize the product values
    def __init__(self, name, price, category, created_date):
        self.name = name
        self.price = price
        self.category = category
        self.created_date = created_date

    # Represent the object as a string when printed.
    def __str__(self):
        return f"  • Producto {self.id}: {self.name} Precio: ${self.price}"
