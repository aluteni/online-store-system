from abc import ABC, abstractmethod
from datetime import date

class Customer:

    _id_counter = 1000

    def __init__(self, name, email):

        self.customer_id = Customer._id_counter
        Customer._id_counter += 1

        self.name = name
        self.email = email
        self.order_history = []

    def addOrder(self, order):
        self.order_history.append(order)

    def isRegularCustomer(self):
        return len(self.order_history) > 6

    def displayInfo(self):
        print(f"Name: {self.name}\nemail: {self.email}")


class Payment(ABC):

    _id_counter = 2000

    def __init__(self, amount, payment_date):

        self.payment_id = Payment._id_counter
        Payment._id_counter += 1

        self.amount = amount
        self.payment_date = payment_date
        self.status = "pending"


    @abstractmethod
    def paymentType(self) -> str:
        pass


    @abstractmethod
    def validatePayment(self) -> bool:
        pass


class CreditCard(Payment):

    def __init__(self, amount, payment_date, card_number):

        super().__init__(amount, payment_date)
        self.card_number = card_number

    def paymentType(self):
        return "credit card"

    def validatePayment(self):
        return len(self.card_number) == 16 and self.card_number.isdigit()




class MobileMoney(Payment):

    def __init__(self, amount, payment_date, phone_number):

        super().__init__(amount, payment_date)
        self.phone_number = phone_number

    def paymentType(self):
        return "mobile money"

    def validatePayment(self):
        return len(self.phone_number) == 10 and self.phone_number.isdigit()


class Product(ABC):

    _id_counter = 3000

    def __init__(self, name, price, stock_quantity):

        self.product_id = Product._id_counter
        Product._id_counter += 1

        self.name = name
        self.price = price
        self.stock_quantity = stock_quantity

    @abstractmethod
    def displayInfo(self):
        pass


class Grocery(Product):

    def __init__(self, name, price, stock_quantity, expiry_date):

        super().__init__(name, price, stock_quantity)
        self.expiry_date = expiry_date

    def isExpired(self, current_date):
        return self.expiry_date < current_date

    def displayInfo(self):
        print(f"[{self.product_id}] | Grocery: {self.name} - N${self.price:.2f} | Expires: {self.expiry_date} | Stock: {self.stock_quantity}")


class Electronic(Product):

    def __init__(self, name, price, stock_quantity, warranty_months):

        super().__init__(name, price, stock_quantity)
        self.warranty_months = warranty_months

    def displayInfo(self):
        print(f"[{self.product_id}] | Electronic: {self.name} - N${self.price:.2f} | Warranty: {self.warranty_months} months | Stock: {self.stock_quantity}")


class OrderItem:

    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def getTotal(self):
        return self.product.price * self.quantity



class Order:

    _id_counter = 4000

    def __init__(self, customer, payment, items, order_date):

        self.order_id = Order._id_counter
        Order._id_counter += 1

        self.customer = customer
        self.payment = payment
        self.items = items
        self.order_date = order_date

        if self.customer.isRegularCustomer():
            self.payment.amount = self.calculateTotalCost() * 0.9
        else:
            self.payment.amount = self.calculateTotalCost()

    def calculateTotalCost(self):
        return sum(item.getTotal() for item in self.items)

    def processPayment(self):

        payment_type = self.payment.paymentType()
        print(f"Processing {payment_type} payment of N${self.payment.amount:.2f}...")

        if self.payment.validatePayment():
            self.payment.status = "approved"
            self.customer.addOrder(self)

        else:
            self.payment.status = "failed"

        return self.payment.status == "approved"
            


class OnlineStore:

    def __init__(self, name):

        self.name = name
        self.products = []
        self.orders = []
        self.registeredCustomers = []

    def registerCustomer(self, customer):

        if isinstance(customer, Customer):
            self.registeredCustomers.append(customer)

    def addProduct(self, product):

        if isinstance(product, Product):
            self.products.append(product)

    def placeOrder(self, order):
        if isinstance(order, Order):
            for item in order.items:
                if item.product.stock_quantity < item.quantity:
                    print(f"Order cancelled: Not enough stock for {item.product.name}")
                    return

            if order.processPayment():
                for item in order.items:
                    item.product.stock_quantity -= item.quantity

                self.orders.append(order)
                print(f"Order #{order.order_id} was placed succesfully.")

            else:
                print("Order rejected. Invalid payment details.")


    def calculateRefundFee(self, order):

        if isinstance(order.payment, CreditCard):
            return order.payment.amount * 0.05
        elif isinstance(order.payment, MobileMoney):
            return 0
        else:
            return 0


    def displayCatalog(self):
        for product in self.products:
            product.displayInfo()


    def searchProduct(self, keyword):

        for product in self.products:
            if keyword.lower() in product.name.lower():
                return product
        return None



    def generateSalesReport(self):

        if not self.orders:
            return "No sales yet."

        total_revenue = sum(order.calculateTotalCost() for order in self.orders)
        order_count = len(self.orders)
        average_order_value = total_revenue / order_count

        product_counts = {}
        for order in self.orders:
            for item in order.items:
                product_counts[item.product.name] = product_counts.get(item.product.name, 0) + item.quantity

        best_seller = max(product_counts, key=product_counts.get)

        return (
            f"Total revenue: N${total_revenue:.2f}\n"
            f"Orders placed: {order_count}\n"
            f"Average order value: N${average_order_value:.2f}\n"
            f"Best-selling product: {best_seller} ({product_counts[best_seller]} sold)"
        )


def seedData(store):
    store.addProduct(Electronic("Phone", 4500.00, 10, 12))
    store.addProduct(Electronic("Laptop", 12000.00, 5, 24))
    store.addProduct(Grocery("Bread", 25.50, 30, date(2026, 9, 15)))
    store.addProduct(Grocery("Milk", 18.00, 20, date(2026, 9, 13)))


def showCatalog(store):
    print("\n--- BrightMart Catalog ---")
    for product in store.products:
        product.displayInfo()


def registerCustomerFlow(store):
    name = input("Customer name: ")
    email = input("Customer email: ")
    customer = Customer(name, email)
    store.registerCustomer(customer)
    print(f"Registered {name} as customer #{customer.customer_id}")


def selectCustomer(store):
    if not store.registeredCustomers:
        print("No customers registered yet.")
        return None

    for c in store.registeredCustomers:
        print(f"{c.customer_id}: {c.name}")

    chosen_id = int(input("Enter customer ID: "))

    for c in store.registeredCustomers:
        if c.customer_id == chosen_id:
            return c

    print("No customer with that ID.")
    return None


def selectPayment():
    method = input("Payment method (card/mobile): ").strip().lower()
    if method == "card":
        card_number = input("Card number (16 digits): ")
        return CreditCard(0.0, date.today(), card_number)
    elif method == "mobile":
        phone_number = input("Phone number (10 digits): ")
        return MobileMoney(0.0, date.today())