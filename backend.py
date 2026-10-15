from abc import ABC, abstractmethod
from datetime import date, datetime
from collections import deque
from storeExceptions import *
import json


class DateHelper:

    FORMAT = "%d/%m/%Y"

    @staticmethod
    def parse(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value).strip(), DateHelper.FORMAT).date()
        except ValueError:
            raise ValueError("Date must be valid and in the format dd/mm/yyyy")

    @staticmethod
    def format(dte):
        return dte.strftime(DateHelper.FORMAT)


class IdHelper:

    @staticmethod
    def assign(cls, given_id):
        if given_id is None:
            new_id = cls._id_counter
            cls._id_counter += 1
            return new_id

        given_id = int(given_id)
        cls._id_counter = max(cls._id_counter, given_id + 1)
        return given_id


class Customer:

    _id_counter = 1000

    def __init__(self, name, email, customer_id=None, previous_orders=0):

        self.customer_id = IdHelper.assign(Customer, customer_id)

        self.name = name
        self.email = email
        self.previous_orders = previous_orders
        self._order_history = []

    @property
    def previous_orders(self):
        return self._previous_orders

    @previous_orders.setter
    def previous_orders(self, count):
        try:
            count = int(count)
        except (ValueError, TypeError):
            raise ValueError("Invalid previous order count")
        if count < 0:
            raise ValueError("Previous orders must be >= 0")
        
        self._previous_orders = count

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        name = str(name).strip()
        if not name:
            raise ValueError("Name is required")
        self._name = name

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        email = str(email).strip()
        local, _, domain = email.partition("@")
        if not local or "." not in domain:
            raise ValueError("Invalid email address")
        self._email = email
    
    def toDict(self):
        return {
            "id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "orders": self.previous_orders
        }

    

    def orderCount(self):
        return self.previous_orders + len(self._order_history)

    def isRegularCustomer(self):
        return self.orderCount() > 6

    def addOrder(self, order):
        for existing_order in self._order_history:
            if existing_order.order_id == order.order_id:
                return

        self._order_history.append(order)


    def displayInfo(self):
        return f"{self.name} | {self.email}"

    def removeOrder(self, order):
        if order in self._order_history:
            self._order_history.remove(order)

    def __str__(self):
        return self.displayInfo()

    def __lt__(self, other):
        return self.orderCount() < other.orderCount()

    def __eq__(self, other):
        return isinstance(other, Customer) and self.email.lower() == other.email.lower()

    


class Payment(ABC):

    _id_counter = 2000

    def __init__(self, payment_date=None, payment_id=None):

        self.payment_id = IdHelper.assign(Payment, payment_id)

        self.amount = 0
        self.payment_date = payment_date
        self.status = "pending"

    @property
    def payment_date(self):
        return self._payment_date

    @payment_date.setter
    def payment_date(self, dte):
        self._payment_date = date.today() if dte is None else DateHelper.parse(dte)

    def toDict(self):
        return {"id": self.payment_id, "type": self.paymentType(),
                "amount": round(self.amount, 2), "status": self.status,
                "date": DateHelper.format(self.payment_date)}

    @abstractmethod
    def paymentType(self):
        pass


    @abstractmethod
    def validatePayment(self):
        pass

    @abstractmethod
    def refundFee(self):
        pass

class CreditCard(Payment):

    def __init__(self, payment_date, card_number, payment_id=None):

        super().__init__(payment_date, payment_id)
        self.card_number = card_number

    def toDict(self):
        payment = super().toDict()
        payment["reference"] = self.card_number
        return payment

    def paymentType(self):
        return "credit card"

    def validatePayment(self):
        return len(self.card_number) == 16 and self.card_number.isdigit()
    
    def refundFee(self):
        return self.amount * 0.05


class MobileMoney(Payment):

    def __init__(self, payment_date, phone_number, payment_id=None):

        super().__init__(payment_date, payment_id)
        self.phone_number = phone_number

    def toDict(self):
        payment = super().toDict()
        payment["reference"] = self.phone_number
        return payment

    def paymentType(self):
        return "mobile money"

    def validatePayment(self):
        return len(self.phone_number) == 10 and self.phone_number.isdigit()

    def refundFee(self):
        return 0

class Product(ABC):

    _id_counter = 3000

    def __init__(self, name, price, stock_quantity, product_id=None):

        self.product_id = IdHelper.assign(Product, product_id)

        self.name = name.lower()
        self.price = price
        self.stock_quantity = stock_quantity

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        try:
            price = float(price)

        except (ValueError, TypeError):
            raise ValueError("Invalid price")

        if price <= 0:
            raise ValueError("Invalid price. Must be > 0")
        
        self._price = round(price, 2)


    @property
    def stock_quantity(self):
        return self._stock_quantity

    @stock_quantity.setter
    def stock_quantity(self, quantity):
        try:
            quantity = int(quantity)

        except (ValueError, TypeError):
            raise ValueError("Invalid stock quantity")

        if quantity < 0:
            raise ValueError("Invalid quantity for product. Must be >= 0")

        self._stock_quantity = quantity


    def toDict(self):
        return {"id": self.product_id, "name": self.name,
                "price": self.price, "stock": self.stock_quantity}

    @abstractmethod
    def displayInfo(self):
        pass

    def __str__(self):
        return self.displayInfo()

    def __lt__(self, other):
        return self.stock_quantity < other.stock_quantity

    def __eq__(self, other):
        return isinstance(other, Product) and self.name.lower() == other.name.lower()


class Grocery(Product):

    def __init__(self, name, price, stock_quantity, expiry_date, product_id=None):

        super().__init__(name, price, stock_quantity, product_id)
        self.expiry_date = expiry_date

    @property
    def expiry_date(self):
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, dte):
        self._expiry_date = DateHelper.parse(dte)

    def toDict(self):
        product = super().toDict()
        product["type"] = "grocery"
        product["expiry"] = DateHelper.format(self.expiry_date)
        return product

    def isExpired(self, current_date=None):
        if not current_date:
            current_date=date.today()
        return self.expiry_date < current_date

    def displayInfo(self):
        return f"[{self.product_id}] | Grocery: {self.name} - N${self.price:.2f} | Expires: {DateHelper.format(self.expiry_date)} | Stock: {self.stock_quantity}"

    def __eq__(self, other):
        return (isinstance(other, Grocery) and super().__eq__(other) and self.expiry_date == other.expiry_date)


class Electronic(Product):

    def __init__(self, name, price, stock_quantity, warranty_months, product_id=None):

        super().__init__(name, price, stock_quantity, product_id)
        self.warranty_months = warranty_months

    def displayInfo(self):
        return f"[{self.product_id}] | Electronic: {self.name} - N${self.price:.2f} | Warranty: {self.warranty_months} months | Stock: {self.stock_quantity}"

    @property
    def warranty_months(self):
        return self._warranty_months

    @warranty_months.setter
    def warranty_months(self, months):

        try:
            months = int(months)

        except (ValueError, TypeError):
            raise ValueError("Invalid warranty months")

        if months <= 0:
            raise ValueError("Invalid warranty months. Must be > 0")

        self._warranty_months = months

    def toDict(self):
        product = super().toDict()
        product["type"] = "electronic"
        product["warranty"] = self.warranty_months
        return product

class OrderItem:

    def __init__(self, product, quantity):
        
        self.product = product
        self.quantity = quantity

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, product):
        if not isinstance(product, Product):
            raise TypeError("Order cancelled: Not a product object.")

        self._product = product

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        try:
            quantity = int(quantity)

        except (ValueError, TypeError):
            raise ValueError("Invalid quantity")

        if quantity <= 0:
            raise ValueError("Invalid quantity in OrderItem. Must be > 0")

        self._quantity = quantity

    def toDict(self):
        return {"product_id": self.product.product_id, "name": self.product.name,
                "price": self.product.price, "quantity": self.quantity}

    def getTotal(self):
        return self.product.price * self.quantity



class Order:

    _id_counter = 4000

    def __init__(self, customer, payment, items, order_date=None, order_id=None):

        if payment.status != "pending":
            raise ValueError("This payment has already been used.")
        
        self.order_id = IdHelper.assign(Order, order_id)

        self.customer = customer
        self.payment = payment
        self.items = items
        self.order_date = order_date or date.today()
        self.payment.amount = self.calculateTotalCost() * 0.9 if self.customer.isRegularCustomer() else self.calculateTotalCost()

    @property
    def customer(self):
        return self._customer

    @customer.setter
    def customer(self, customer):
        if not isinstance(customer, Customer):
            raise ValueError("Order cancelled: Not a customer object.")

        self._customer = customer

    @property
    def payment(self):
        return self._payment

    @payment.setter
    def payment(self, payment):
        if not isinstance(payment, Payment):
            raise ValueError("Order cancelled: Not a payment object")

        self._payment = payment

    
    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, ordered):
        for item in ordered:
            if not isinstance(item, OrderItem):
                raise ValueError("Order cancelled: all items in being ordered must be OrderItem objects")

        self._items = ordered

    @property
    def order_date(self):
        return self._order_date
    
    @order_date.setter
    def order_date(self, dte):
            self._order_date = DateHelper.parse(dte)


   
    def toDict(self):
        return {
            "id": self.order_id,
            "date": DateHelper.format(self.order_date),

            "customer_id": self.customer.customer_id,
            "customer": {
                "id": self.customer.customer_id,
                "name": self.customer.name,
                "email": self.customer.email
            },

            "items": [item.toDict() for item in self.items],
            "payment": self.payment.toDict()
        }


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

    def __len__(self):
        return len(self.items)

    def __add__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.payment.amount + other.payment.amount


class OrderQueue:

    def __init__(self):
        self._orders = deque()

    def _enqueue(self, order):
        self._orders.append(order)

    def dequeue(self):
        if self.isEmpty():
            raise EmptyQueueError("There are no pending orders.")
        return self._orders.popleft()

    def peek(self):
        if self.isEmpty():
            raise EmptyQueueError("There are no pending orders.")
        return self._orders[0]

    def isEmpty(self):
        return len(self) == 0

    def __len__(self):
        return len(self._orders)


class OrderStack:

    def __init__(self):
        self._orders = []

    def push(self, order):
        if not isinstance(order, Order):
            raise TypeError("Only Order objects can be stacked.")
        self._orders.append(order)

    def pop(self):
        if self.isEmpty():
            raise EmptyStackError("There are no orders to cancel.")
        return self._orders.pop()

    def peek(self):
        if self.isEmpty():
            raise EmptyStackError("There are no orders to cancel.")
        return self._orders[-1]

    def isEmpty(self):
        return len(self) == 0

    def __len__(self):
        return len(self._orders)
            


class OnlineStore:

    def __init__(self, name):

        self.name = name
        self.products = []
        self.orders = []
        self.__pending_orders = OrderQueue()
        self.completed_orders = OrderStack()
        self.registered_customers = []

    def registerCustomer(self, customer):

        if customer in self.registered_customers:
            raise DuplicateCustomerError("Customer with that email already exists")
            
        self.registered_customers.append(customer)

    def addProduct(self, product):

        if not isinstance(product, Product):
            raise TypeError("Not added: not a product object.")

        if isinstance(product, Grocery) and product.isExpired():
            raise ExpiredProductError(f"{product.name} was not added because it is already expired!")

        for existing in self.products:
            if existing == product:
                existing.stock_quantity += product.stock_quantity
                return
            
        self.products.append(product)


    def findProduct(self, product):
        for p in self.products:
            if p == product:
                return p
        return None


    def removeExpired(self):
        self.products = [
        p for p in self.products
        if not (isinstance(p, Grocery) and p.isExpired())
    ]

    def submitOrder(self, order):

        if not isinstance(order, Order):
            raise TypeError("Only Order objects can be queued.")
        
        if order.payment.status != "pending":
            raise ValueError("Order cancelled: This order was already processed.")
        self.__pending_orders._enqueue(order)

    def processNextOrder(self):
        order = self.__pending_orders.dequeue()
        self.__placeOrder(order)
        return order

    def pendingCount(self):
        return len(self.__pending_orders)

    def __placeOrder(self, order):

        self.removeExpired()

        needed = {}
        for item in order.items:
            stored = self.findProduct(item.product)
            if stored is None:
                raise ProductNotFoundError(f"Order cancelled: {item.product.name} is not available.")
                
            entry = needed.setdefault(stored.product_id, [stored, 0])
            entry[1] += item.quantity

        for stored, qty in needed.values():
            if stored.stock_quantity < qty:
                raise OutOfStockError(stored.name, stored.stock_quantity)

        if not order.processPayment():
            raise InvalidPaymentError("Invalid payment details.")

        for stored, qty in needed.values():
            stored.stock_quantity -= qty

        self.orders.append(order)
        self.completed_orders.push(order)
        print(f"Order #{order.order_id} was placed successfully.")


    def cancelLastOrder(self):
        order = self.completed_orders.peek()

        fee = self.calculateRefundFee(order)
        refund = order.payment.amount - fee

        for item in order.items:
            stored = self.findProduct(item.product)
            if stored is not None:
                stored.stock_quantity += item.quantity

        self.orders.remove(order)
        order.customer.removeOrder(order)
        order.payment.status = "refunded"
        self.completed_orders.pop()

        return order, round(fee, 2), round(refund, 2)
    

    def listByCustomerOrderHistory(self):
        return sorted(self.registered_customers)

    def sortByStockQuantity(self):
        return sorted(self.products)

    def calculateRefundFee(self, order):
        return order.payment.refundFee()

    def displayCatalog(self):

        self.removeExpired()

        for product in self.products:
            print(product)


    def searchProduct(self, keyword):
        self.removeExpired()
        return [p for p in self.products if keyword.lower() in p.name.lower()]


    def generateSalesReport(self):

        if not self.orders:
            return "No sales yet."

        total_revenue = sum(order.payment.amount for order in self.orders)
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

    def _writeJson(self, filename, data):

        try:
            text = json.dumps(data, indent=4)
        except TypeError as e:
            raise StoreFileError(f"Could not convert data to JSON: {e}")

        try:
            with open(filename, "w") as f:
                f.write(text)
        except PermissionError:
            raise StoreFileError(f"No permission to write to {filename}. Is it open in another program?")
        except OSError as e:
            raise StoreFileError(f"Could not save {filename}: {e}")
        return filename

    def _readJson(self, filename):

        try:
            with open(filename) as f:
                data = json.load(f)
        except FileNotFoundError:
            return []
        except PermissionError:
            raise StoreFileError(f"No permission to read {filename}.")
        except json.JSONDecodeError as e:
            raise StoreFileError(f"{filename} is not valid JSON: {e}")
        except OSError as e:
            raise StoreFileError(f"Could not read {filename}: {e}")

        if not isinstance(data, list):
            raise StoreFileError(f"{filename} should contain a list.")
        return data

    def saveCustomers(self, filename="customers.json"):
        return self._writeJson(filename, [c.toDict() for c in self.registered_customers])

    def saveCatalog(self, filename="products.json"):
        return self._writeJson(filename, [p.toDict() for p in self.products])

    def saveOrders(self, filename="orders.json"):
        return self._writeJson(filename, [o.toDict() for o in self.orders])
        


    def loadCustomers(self, filename="customers.json"):
        loaded = []
        for number, data in enumerate(self._readJson(filename), start=1):
            try:
                loaded.append(Customer(data["name"], data["email"],
                                    customer_id=data["id"],
                                    previous_orders=data["orders"]))
            except (KeyError, TypeError, ValueError) as e:
                raise StoreFileError(f"{filename}: entry {number} is invalid ({e!r})")

        for customer in loaded:
            self.registerCustomer(customer)
        return len(loaded)


    def loadCatalog(self, filename="products.json"):

        loaded = []

        for number, data in enumerate(self._readJson(filename), start=1):
            try:
                product_type = data["type"]

                if product_type.lower() == "grocery":
                    product = Grocery(
                        name=data["name"],
                        price=data["price"],
                        stock_quantity=data["stock"],
                        expiry_date=data["expiry"],
                        product_id=data["id"]
                    )

                elif product_type.lower() == "electronic":
                    product = Electronic(
                        name=data["name"],
                        price=data["price"],
                        stock_quantity=data["stock"],
                        warranty_months=data["warranty"],
                        product_id=data["id"]
                    )

                else:
                    raise ValueError(f"Unknown product type: {product_type}")

                loaded.append(product)

            except (KeyError, TypeError, ValueError) as e:
                raise StoreFileError(f"{filename}: entry {number} is invalid ({e!r})")

        added = 0
        for product in loaded:
            try:
                self.addProduct(product)
                added += 1
            except ExpiredProductError:
                continue

        return added


   
    def loadOrders(self, filename="orders.json"):
        loaded = []
        existing_order_ids = {order.order_id for order in self.orders}

        customers = {
            c.customer_id: c
            for c in self.registered_customers
        }

        products = {
            p.product_id: p
            for p in self.products
        }

        for number, data in enumerate(self._readJson(filename), start=1):
            try:
                customer_id = data["customer_id"]

                if customer_id in customers:
                    customer = customers[customer_id]

                else:
                    customer_data = data["customer"]

                    customer = Customer(
                        name=customer_data["name"],
                        email=customer_data["email"],
                        customer_id=customer_data["id"]
                    )

                    customers[customer_id] = customer
                items = []
                missing_product = False

                for item_data in data["items"]:
                    product = products.get(item_data["product_id"])

                    if product is None:
                        missing_product = True
                        break

                    items.append(OrderItem(product, item_data["quantity"]))

                if missing_product:
                    continue

                payment_data = data["payment"]
                payment_type = payment_data["type"]

                if payment_type.lower() == "credit card":
                    payment = CreditCard(
                        payment_date=payment_data["date"],
                        card_number=payment_data["reference"],
                        payment_id=payment_data["id"]
                    )

                elif payment_type.lower() == "mobile money":
                    payment = MobileMoney(
                        payment_date=payment_data["date"],
                        phone_number=payment_data["reference"],
                        payment_id=payment_data["id"]
                    )

                else:
                    raise ValueError(f"Unknown payment type: {payment_type}")
                
                order = Order(
                    customer=customer,
                    payment=payment,
                    items=items,
                    order_date=data["date"],
                    order_id=data["id"]
                )

                if order.order_id in existing_order_ids:
                    continue

                existing_order_ids.add(order.order_id)

                payment.amount = float(payment_data["amount"])
                payment.status = payment_data["status"]

                loaded.append(order)

            except (KeyError, TypeError, ValueError) as e:
                raise StoreFileError(f"{filename}: entry {number} is invalid ({e!r})")

        for order in loaded:
            self.orders.append(order)

            if order.payment.status.lower() == "approved":
                order.customer.addOrder(order)
                self.completed_orders.push(order)

        return len(loaded)
    
    def __len__(self):
        return len(self.products)

