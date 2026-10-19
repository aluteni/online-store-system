# BrightMart Online Store System

A desktop application for managing a single online store, written in Python with a Tkinter graphical interface. It was built for the Object-Oriented Programming course at UNAM.

BrightMart tracks products, customers and orders. It prevents overselling, validates payments, rewards loyal customers with a discount, and keeps expiry and warranty information for products.

## Features

- **Catalog:** browse and search products, and add new groceries (with an expiry date) and electronics (with a warranty). Expired groceries are rejected and removed automatically.
- **Customers:** register customers with name and email validation. Duplicate emails are not allowed.
- **Orders:** build a cart, choose a payment method and submit the order to a queue. Orders are processed one at a time in the order they arrive (first in, first out).
- **Stock control:** an order is refused if there is not enough stock, so products are never oversold.
- **Loyalty discount:** a customer with more than 6 orders gets 10% off every new order.
- **Cancel last order:** the most recent completed order can be cancelled. Stock is restored and a refund is calculated: a 5% fee for credit cards, no fee for mobile money.
- **Sales report:** total revenue, number of orders, average order value, best-selling product, and a table of all orders. The report can be saved to `sales_report.json`.
- **Saving:** products, customers and orders are saved to JSON files, either with the "Save all data" button or when you close the window.

## Payment rules

| Method | Valid reference | Refund fee |
|---|---|---|
| Credit card | exactly 16 digits | 5% of the order total |
| Mobile money | exactly 10 digits | none |

## Project structure

| File | Purpose |
|---|---|
| `backend.py` | All classes: `OnlineStore`, `Product`, `Grocery`, `Electronic`, `Customer`, `Order`, `OrderItem`, `Payment`, `CreditCard`, `MobileMoney`, `OrderQueue`, `OrderStack` and helpers |
| `storeExceptions.py` | Custom exceptions such as `OutOfStockError` and `ExpiredProductError` |
| `gui.py` | The Tkinter interface (Catalog, Customers, Orders and Report tabs) |
| `demo_data.py` | Generates sample products, customers and orders |
| `products.json`, `customers.json`, `orders.json` | Saved store data |
| `problem statement.pdf` | The problem statement for the project |

## Object-oriented concepts used

- **Inheritance and abstract classes:** `Product` is the parent of `Grocery` and `Electronic`. `Payment` is the parent of `CreditCard` and `MobileMoney`.
- **Polymorphism:** `displayInfo`, `paymentType`, `validatePayment` and `refundFee` behave differently in each subclass.
- **Encapsulation:** property setters validate price, stock, dates, names and emails.
- **Operator overloading:** `__lt__`, `__eq__`, `__add__`, `__len__` and `__str__`.
- **Composition and aggregation:** an `Order` is made of `OrderItem` objects and has one `Payment`. The store holds products, customers and orders.
- **Data structures:** `OrderQueue` (a queue of pending orders) and `OrderStack` (a stack of completed orders used for cancelling the last one).
- **Exception handling:** custom exceptions for stock, payment, file and empty-queue errors.
- **File handling:** JSON saving and loading with error handling.

## How to run

Requirements: Python 3.9 or newer. Tkinter comes with the standard Python installer on Windows, and no other packages are needed.

1. Download or clone the repository.
2. Open a terminal in the project folder.
3. (Optional) Generate sample data. This overwrites the three JSON files:

```
   python demo_data.py
```

4. Start the application:

```
   python gui.py
```

Run both commands from the project folder, because the program reads and writes the JSON files in the folder it is started from.

## Using the application

1. **Catalog tab:** search for products or add a new one.
2. **Customers tab:** register a customer.
3. **Orders tab:** pick a customer, add products to the cart, enter the payment details and press **Submit order**. Then press **Process next order** to complete it.
4. **Report tab:** view sales figures and save the data.

Prices are in Namibian dollars (N$).
