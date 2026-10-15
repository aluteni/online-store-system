import random
from datetime import date, timedelta
 
from backend import *
from storeExceptions import *
 
random.seed(7)
today = date.today()
 
# (name, price, stock, days until expiry)
GROCERIES = [
    ("fresh milk 2l", 32.99, 40, 12),
    ("brown bread 700g", 18.99, 35, 5),
    ("white rice 2kg", 54.99, 50, 365),
    ("maize meal 5kg", 79.99, 45, 300),
    ("cooking oil 750ml", 42.99, 30, 400),
    ("sugar 2kg", 39.99, 40, 450),
    ("eggs tray of 30", 74.99, 25, 20),
    ("cheddar cheese 500g", 89.99, 20, 45),
    ("butter 500g", 69.99, 22, 40),
    ("chicken pieces 2kg", 119.99, 18, 7),
    ("beef mince 1kg", 99.99, 15, 6),
    ("bananas 1kg", 22.99, 30, 5),
    ("apples 1.5kg", 44.99, 28, 25),
    ("oranges 2kg", 39.99, 26, 18),
    ("tomatoes 1kg", 27.99, 30, 8),
    ("potatoes 2kg", 34.99, 40, 30),
    ("onions 2kg", 29.99, 40, 40),
    ("spaghetti 500g", 19.99, 60, 500),
    ("canned beans 410g", 14.99, 70, 600),
    ("tuna in oil 170g", 24.99, 55, 700),
    ("peanut butter 400g", 39.99, 35, 300),
    ("ground coffee 200g", 84.99, 25, 365),
    ("rooibos tea 80 bags", 49.99, 30, 500),
    ("orange juice 1l", 29.99, 24, 20),
    ("frozen pizza 400g", 69.99, 14, 90),
    ("plain yoghurt 1kg", 44.99, 20, 15),
    ("corn flakes 750g", 64.99, 30, 200),
    ("biltong 200g", 109.99, 16, 60),
]
 
# (name, price, stock, warranty months)
ELECTRONICS = [
    ("samsung galaxy a16 smartphone", 3499.99, 10, 24),
    ("samsung galaxy a56 smartphone", 7499.99, 8, 24),
    ("apple iphone 16 smartphone", 14999.99, 6, 12),
    ("xiaomi redmi note 14 smartphone", 4299.99, 12, 24),
    ("huawei nova 12 smartphone", 5199.99, 9, 24),
    ("samsung galaxy tab a9 tablet", 2999.99, 9, 24),
    ("apple ipad 9th gen tablet", 8999.99, 5, 12),
    ("lenovo ideapad laptop", 9999.99, 7, 24),
    ("hp pavilion laptop", 12999.99, 6, 24),
    ("dell inspiron laptop", 11999.99, 5, 24),
    ("asus vivobook laptop", 10999.99, 6, 24),
    ("samsung 55-inch 4k television", 8999.99, 5, 24),
    ("lg 50-inch 4k television", 7999.99, 4, 24),
    ("hisense 43-inch television", 5499.99, 7, 24),
    ("playstation 5 console", 11999.99, 6, 12),
    ("xbox series s console", 6999.99, 6, 12),
    ("nintendo switch console", 5999.99, 8, 12),
    ("sony wh-ch720n headphones", 1999.99, 12, 12),
    ("jbl tune wireless headphones", 1299.99, 15, 12),
    ("apple airpods wireless earbuds", 2999.99, 10, 12),
    ("logitech g502 gaming mouse", 1199.99, 14, 12),
    ("logitech wireless keyboard", 699.99, 18, 12),
    ("anker 20000mah power bank", 899.99, 16, 12),
    ("tp-link wi-fi router", 999.99, 12, 24),
    ("canon pixma printer", 1999.99, 7, 12),
    ("samsung 25w usb-c charger", 299.99, 25, 12),
    ("sandisk 128gb flash drive", 249.99, 30, 12),
    ("hp 27-inch monitor", 3299.99, 8, 24),
]
 
# (name, previous orders). 7 or more previous orders = regular customer (10% off)
CUSTOMERS = [
    ("Adolfo Diaz", 8),
    ("Fredrick Shikongo", 2),
    ("Maria Nghipandulwa", 9),
    ("Johannes Amukoto", 0),
    ("Ndapewa Iyambo", 3),
    ("Tuyeni Hamutenya", 7),
    ("Selma Nangolo", 1),
    ("Petrus Shilongo", 0),
    ("Anna Kandjii", 4),
    ("David Uushona", 0),
    ("Rauna Haufiku", 10),
    ("Elias Mbumba", 2),
    ("Lahja Ndeshi", 0),
    ("Samuel Kuutondokwa", 5),
    ("Emilia Shaanika", 1),
    ("Thomas Ekandjo", 0),
    ("Hileni Nakale", 8),
    ("Joseph Tjivikua", 3),
    ("Martha Gawanas", 0),
    ("Isaac Hoaeb", 2),
    ("Naomi Kapofi", 0),
    ("Paulus Namupala", 6),
    ("Ruth Amadhila", 1),
    ("Simon Ndjamba", 0),
    ("Beata Mutonga", 4),
    ("Kaleb Shivute", 0),
    ("Lydia Nashilongo", 2),
    ("Frans Tjipetekera", 0),
]
 
 
def randomCard():
    return "".join(random.choice("0123456789") for _ in range(16))
 
 
def randomPhone():
    return "081" + "".join(random.choice("0123456789") for _ in range(7))
 
 
store = OnlineStore("BrightMart")
 
for name, price, stock, days in GROCERIES:
    store.addProduct(Grocery(name, price, stock, today + timedelta(days=days)))
 
for name, price, stock, months in ELECTRONICS:
    store.addProduct(Electronic(name, price, stock, months))
 
for name, previous in CUSTOMERS:
    email = name.lower().replace(" ", ".") + "@example.com"
    store.registerCustomer(Customer(name, email, previous_orders=previous))
 
placed = 0
for _ in range(60):
    customer = random.choice(store.registered_customers)
    day = today - timedelta(days=random.randint(0, 30))
 
    chosen = random.sample(store.products, random.randint(1, 4))
    items = [OrderItem(product, random.randint(1, 3)) for product in chosen]
 
    if random.random() < 0.5:
        payment = CreditCard(day, randomCard())
    else:
        payment = MobileMoney(day, randomPhone())
 
    try:
        store.submitOrder(Order(customer, payment, items, order_date=day))
        store.processNextOrder()
        placed += 1
    except StoreError:
        pass
 
store.saveCatalog()
store.saveCustomers()
store.saveOrders()
 
print(f"Saved {len(store.products)} products, "
      f"{len(store.registered_customers)} customers, {placed} orders.")
 