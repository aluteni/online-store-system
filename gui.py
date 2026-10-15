import tkinter as tk
from tkinter import ttk, messagebox
from backend import *
from storeExceptions import *
 
PRIMARY = "#583B14"
PRIMARY_DARK = "#4E342E"
PRIMARY_HOVER = "#5D4037"
SOFT = "#D7CCC8"
BG = "#F5F5F4"
TAB_BG = "#E7E5E4"
TEXT = "#292524"
BORDER = "#D6D3D1"
 
 
class StoreApp(tk.Tk):
 
    def __init__(self):
        super().__init__()
        self.title("BrightMart")
        self.geometry("1000x650")
        self.minsize(900, 600)
        self.setupStyle()
 
        self.store = OnlineStore("BrightMart")
        try:
            self.store.loadCatalog()
            self.store.loadCustomers()
            self.store.loadOrders()
        except StoreError as e:
            messagebox.showerror("Load error", str(e))
 
        header = tk.Frame(self, bg=PRIMARY)
        header.pack(fill="x")
        tk.Label(header, text="BrightMart", bg=PRIMARY, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(header, text="Online store manager", bg=PRIMARY, fg=SOFT,
                 font=("Segoe UI", 10)).pack(side="left")
 
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
 
        self.catalog_tab = ttk.Frame(tabs)
        tabs.add(self.catalog_tab, text="Catalog")
        self.buildCatalogTab()
        self.refreshCatalog()
 
        self.customer_tab = ttk.Frame(tabs)
        tabs.add(self.customer_tab, text="Customers")
        self.buildCustomerTab()
        self.refreshCustomers()
 
        self.order_tab = ttk.Frame(tabs)
        tabs.add(self.order_tab, text="Orders")
        self.buildOrderTab()
        tabs.bind("<<NotebookTabChanged>>", lambda e: self.refreshOrderChoices())
 
        self.report_tab = ttk.Frame(tabs)
        tabs.add(self.report_tab, text="Report")
        self.buildReportTab()
        self.refreshReport()
 
        self.protocol("WM_DELETE_WINDOW", self.onClose)
 
    # ---------- styling ----------
 
    def setupStyle(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        self.configure(bg=BG)
 
        style.configure(".", font=("Segoe UI", 10), background=BG, foreground=TEXT)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TLabelframe", background=BG, bordercolor=BORDER)
        style.configure("TLabelframe.Label", background=BG, foreground=PRIMARY,
                        font=("Segoe UI", 10, "bold"))
 
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(20, 8), background=TAB_BG,
                        foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", PRIMARY)],
                  foreground=[("selected", "white")])
 
        style.configure("TButton", padding=(14, 7), background=PRIMARY,
                        foreground="white", borderwidth=0,
                        font=("Segoe UI", 10, "bold"))
        style.map("TButton",
                  background=[("pressed", PRIMARY_DARK), ("active", PRIMARY_HOVER)])
 
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=6)
 
        style.configure("Treeview", background="white", fieldbackground="white",
                        foreground=TEXT, rowheight=28, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PRIMARY_DARK, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=8, relief="flat")
        style.map("Treeview.Heading", background=[("active", PRIMARY_HOVER)])
        style.map("Treeview", background=[("selected", PRIMARY)],
                  foreground=[("selected", "white")])
 
        style.configure("Total.TLabel", font=("Segoe UI", 13, "bold"),
                        foreground=PRIMARY_DARK)
 
        self.option_add("*Label.background", BG)
 
    # ---------- catalog tab ----------
 
    def buildCatalogTab(self):
        top = ttk.Frame(self.catalog_tab)
        top.pack(fill="x", padx=10, pady=10)
 
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        ttk.Button(top, text="Search", command=self.refreshCatalog).pack(side="left", padx=5)
 
        table = ttk.Frame(self.catalog_tab)
        table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
 
        self.product_table = ttk.Treeview(
            table, columns=("id", "type", "name", "price", "stock", "details"),
            show="headings")
        for col, title, width, anchor in [
            ("id", "ID", 60, "center"),
            ("type", "Type", 90, "center"),
            ("name", "Name", 300, "w"),
            ("price", "Price (N$)", 110, "e"),
            ("stock", "Stock", 70, "center"),
            ("details", "Expiry / Warranty", 160, "center"),
        ]:
            self.product_table.heading(col, text=title)
            self.product_table.column(col, width=width, anchor=anchor)
 
        self.product_table.tag_configure("odd", background=BG)
        self.product_table.tag_configure("even", background="white")
 
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=scroll.set)
        self.product_table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
 
        form = ttk.LabelFrame(self.catalog_tab, text="Add product")
        form.pack(fill="x", padx=10, pady=(0, 10))
 
        self.type_var = tk.StringVar(value="Grocery")
        self.name_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        self.extra_var = tk.StringVar()
 
        ttk.Label(form, text="Type").grid(row=0, column=0, padx=5)
        ttk.Label(form, text="Name").grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Price").grid(row=0, column=2, padx=5)
        ttk.Label(form, text="Stock").grid(row=0, column=3, padx=5)
        self.extra_label = ttk.Label(form, text="Expiry (dd/mm/yyyy)")
        self.extra_label.grid(row=0, column=4, padx=5)
 
        type_box = ttk.Combobox(form, textvariable=self.type_var,
                                values=["Grocery", "Electronic"],
                                state="readonly", width=11)
        type_box.grid(row=1, column=0, padx=5, pady=5)
        type_box.bind("<<ComboboxSelected>>", self.updateExtraLabel)
 
        ttk.Entry(form, textvariable=self.name_var, width=18).grid(row=1, column=1, padx=5)
        ttk.Entry(form, textvariable=self.price_var, width=8).grid(row=1, column=2, padx=5)
        ttk.Entry(form, textvariable=self.stock_var, width=8).grid(row=1, column=3, padx=5)
        ttk.Entry(form, textvariable=self.extra_var, width=18).grid(row=1, column=4, padx=5)
        ttk.Button(form, text="Add", command=self.addProduct).grid(row=1, column=5, padx=5)
 
    def refreshCatalog(self):
        self.product_table.delete(*self.product_table.get_children())
        for i, product in enumerate(self.store.searchProduct(self.search_var.get())):
            if isinstance(product, Grocery):
                kind, details = "Grocery", DateHelper.format(product.expiry_date)
            else:
                kind, details = "Electronic", f"{product.warranty_months} months"
 
            self.product_table.insert(
                "", tk.END,
                values=(product.product_id, kind, product.name.title(),
                        f"{product.price:,.2f}", product.stock_quantity, details),
                tags=("odd" if i % 2 else "even",))
 
    def updateExtraLabel(self, event=None):
        if self.type_var.get() == "Grocery":
            self.extra_label.config(text="Expiry (dd/mm/yyyy)")
        else:
            self.extra_label.config(text="Warranty (months)")
 
    def addProduct(self):
        try:
            name = self.name_var.get().strip()
            if not name:
                raise ValueError("Name is required")
 
            if self.type_var.get() == "Grocery":
                product = Grocery(name, self.price_var.get(),
                                  self.stock_var.get(), self.extra_var.get())
            else:
                product = Electronic(name, self.price_var.get(),
                                     self.stock_var.get(), self.extra_var.get())
 
            self.store.addProduct(product)
 
        except (ValueError, StoreError) as e:
            messagebox.showerror("Cannot add product", str(e))
            return
 
        for var in (self.name_var, self.price_var, self.stock_var, self.extra_var):
            var.set("")
        self.refreshCatalog()
 
    # ---------- customers tab ----------
 
    def buildCustomerTab(self):
        table = ttk.Frame(self.customer_tab)
        table.pack(fill="both", expand=True, padx=10, pady=10)
 
        self.customer_table = ttk.Treeview(
            table, columns=("id", "name", "email", "orders", "status"),
            show="headings")
        for col, title, width, anchor in [
            ("id", "ID", 60, "center"),
            ("name", "Name", 220, "w"),
            ("email", "Email", 320, "w"),
            ("orders", "Orders", 80, "center"),
            ("status", "Status", 120, "center"),
        ]:
            self.customer_table.heading(col, text=title)
            self.customer_table.column(col, width=width, anchor=anchor)
 
        self.customer_table.tag_configure("odd", background=BG)
        self.customer_table.tag_configure("even", background="white")
 
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.customer_table.yview)
        self.customer_table.configure(yscrollcommand=scroll.set)
        self.customer_table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
 
        form = ttk.LabelFrame(self.customer_tab, text="Register customer")
        form.pack(fill="x", padx=10, pady=(0, 10))
 
        self.cust_name_var = tk.StringVar()
        self.cust_email_var = tk.StringVar()
 
        ttk.Label(form, text="Name").grid(row=0, column=0, padx=5)
        ttk.Label(form, text="Email").grid(row=0, column=1, padx=5)
        ttk.Entry(form, textvariable=self.cust_name_var, width=25).grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(form, textvariable=self.cust_email_var, width=30).grid(row=1, column=1, padx=5)
        ttk.Button(form, text="Register", command=self.registerCustomer).grid(row=1, column=2, padx=5)
 
    def refreshCustomers(self):
        self.customer_table.delete(*self.customer_table.get_children())
        for i, customer in enumerate(self.store.listByCustomerOrderHistory()):
            status = "Regular" if customer.isRegularCustomer() else "Standard"
            self.customer_table.insert(
                "", tk.END,
                values=(customer.customer_id, customer.name, customer.email,
                        customer.orderCount(), status),
                tags=("odd" if i % 2 else "even",))
 
    def registerCustomer(self):
        try:
            customer = Customer(self.cust_name_var.get(), self.cust_email_var.get())
            self.store.registerCustomer(customer)
        except (ValueError, StoreError) as e:
            messagebox.showerror("Cannot register", str(e))
            return
 
        self.cust_name_var.set("")
        self.cust_email_var.set("")
        self.refreshCustomers()
 
    # ---------- orders tab ----------
 
    def buildOrderTab(self):
        self.cart = []
        self.order_customers = []
        self.order_products = []
 
        self.order_customer_var = tk.StringVar()
        self.order_product_var = tk.StringVar()
        self.order_qty_var = tk.StringVar(value="1")
        self.pay_type_var = tk.StringVar(value="Credit Card")
        self.pay_ref_var = tk.StringVar()
        self.cart_total_var = tk.StringVar(value="Cart total: N$0.00")
        self.pending_var = tk.StringVar(value="Pending orders: 0")
 
        pick = ttk.LabelFrame(self.order_tab, text="New order")
        pick.pack(fill="x", padx=10, pady=10)
 
        ttk.Label(pick, text="Customer").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.order_customer_box = ttk.Combobox(pick, textvariable=self.order_customer_var,
                                               state="readonly", width=45)
        self.order_customer_box.grid(row=0, column=1, columnspan=3, sticky="w", padx=5)
 
        ttk.Label(pick, text="Product").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.order_product_box = ttk.Combobox(pick, textvariable=self.order_product_var,
                                              state="readonly", width=45)
        self.order_product_box.grid(row=1, column=1, padx=5)
        ttk.Label(pick, text="Qty").grid(row=1, column=2, padx=5)
        ttk.Entry(pick, textvariable=self.order_qty_var, width=5).grid(row=1, column=3, padx=5)
        ttk.Button(pick, text="Add to cart", command=self.addToCart).grid(row=1, column=4, padx=5)
 
        self.cart_table = ttk.Treeview(
            self.order_tab, columns=("product", "qty", "price", "subtotal"),
            show="headings", height=6)
        for col, title, width, anchor in [
            ("product", "Product", 320, "w"),
            ("qty", "Qty", 70, "center"),
            ("price", "Unit price (N$)", 140, "e"),
            ("subtotal", "Subtotal (N$)", 140, "e"),
        ]:
            self.cart_table.heading(col, text=title)
            self.cart_table.column(col, width=width, anchor=anchor)
 
        self.cart_table.tag_configure("odd", background=BG)
        self.cart_table.tag_configure("even", background="white")
        self.cart_table.pack(fill="both", expand=True, padx=10)
 
        cart_bar = ttk.Frame(self.order_tab)
        cart_bar.pack(fill="x", padx=10, pady=(5, 0))
        ttk.Button(cart_bar, text="Remove selected",
                   command=self.removeFromCart).pack(side="left")
        ttk.Button(cart_bar, text="Clear cart",
                   command=self.clearCart).pack(side="left", padx=5)
        ttk.Label(cart_bar, textvariable=self.cart_total_var,
                  style="Total.TLabel").pack(side="right", padx=5)
 
        pay = ttk.LabelFrame(self.order_tab, text="Payment")
        pay.pack(fill="x", padx=10, pady=10)
 
        ttk.Combobox(pay, textvariable=self.pay_type_var,
                     values=["Credit Card", "Mobile Money"],
                     state="readonly", width=14).grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(pay, textvariable=self.pay_ref_var, width=25).grid(row=0, column=1, padx=5)
        ttk.Button(pay, text="Submit order", command=self.submitOrder).grid(row=0, column=2, padx=5)
        ttk.Label(pay, textvariable=self.pending_var).grid(row=0, column=3, padx=15)
 
        queue = ttk.LabelFrame(self.order_tab, text="Queue")
        queue.pack(fill="x", padx=10, pady=(0, 10))
 
        ttk.Button(queue, text="Process next order",
                   command=self.processOrder).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(queue, text="Cancel last order",
                   command=self.cancelLast).grid(row=0, column=1, padx=5)
 
    def refreshOrderChoices(self):
        self.order_customers = list(self.store.registered_customers)
        self.order_products = self.store.searchProduct("")
 
        self.order_customer_var.set("")
        self.order_product_var.set("")
        self.order_customer_box["values"] = [str(c) for c in self.order_customers]
        self.order_product_box["values"] = [
            f"[{p.product_id}] {p.name} - N${p.price:.2f}" for p in self.order_products
        ]
 
    def refreshCart(self):
        self.cart_table.delete(*self.cart_table.get_children())
        for i, item in enumerate(self.cart):
            self.cart_table.insert(
                "", tk.END,
                values=(item.product.name.title(), item.quantity,
                        f"{item.product.price:,.2f}", f"{item.getTotal():,.2f}"),
                tags=("odd" if i % 2 else "even",))
        total = sum(item.getTotal() for item in self.cart)
        self.cart_total_var.set(f"Cart total: N${total:,.2f}")

    
 
    def addToCart(self):
        index = self.order_product_box.current()
        try:
            if index < 0:
                raise ValueError("Choose a product")
            self.cart.append(OrderItem(self.order_products[index], self.order_qty_var.get()))
        except (ValueError, TypeError) as e:
            messagebox.showerror("Cannot add item", str(e))
            return
        self.refreshCart()

    def removeFromCart(self):
        selected = self.cart_table.selection()
        if not selected:
            messagebox.showinfo("Remove item", "Select an item in the cart first.")
            return
        del self.cart[self.cart_table.index(selected[0])]
        self.refreshCart()

    def clearCart(self):
        self.cart.clear()
        self.refreshCart()
 
    def submitOrder(self):
        index = self.order_customer_box.current()
        try:
            if index < 0:
                raise ValueError("Choose a customer")
            if not self.cart:
                raise ValueError("The cart is empty")
 
            reference = self.pay_ref_var.get().strip()
            if self.pay_type_var.get() == "Credit Card":
                payment = CreditCard(None, reference)
            else:
                payment = MobileMoney(None, reference)
 
            order = Order(self.order_customers[index], payment, list(self.cart))
            self.store.submitOrder(order)
 
        except (ValueError, TypeError, StoreError) as e:
            messagebox.showerror("Cannot submit order", str(e))
            return
 
        self.cart.clear()
        self.pay_ref_var.set("")
        self.refreshCart()
        self.pending_var.set(f"Pending orders: {self.store.pendingCount()}")
 
    def processOrder(self):
        try:
            order = self.store.processNextOrder()
        except EmptyQueueError as e:
            messagebox.showinfo("Queue empty", str(e))
            return
        except StoreError as e:
            messagebox.showerror("Order failed",
                                 f"{e}\nThe order was removed from the queue.")
        else:
            messagebox.showinfo("Order placed",
                                f"Order #{order.order_id} placed.\n"
                                f"Total: N${order.payment.amount:,.2f}")
        self.afterOrderChange()
 
    def cancelLast(self):
        try:
            order, fee, refund = self.store.cancelLastOrder()
        except StoreError as e:
            messagebox.showinfo("Nothing to cancel", str(e))
            return
 
        messagebox.showinfo("Order cancelled",
                            f"Order #{order.order_id} cancelled.\n"
                            f"Refund fee: N${fee:,.2f}\n"
                            f"Refund: N${refund:,.2f}")
        self.afterOrderChange()
 
    def afterOrderChange(self):
        self.pending_var.set(f"Pending orders: {self.store.pendingCount()}")
        self.refreshCatalog()
        self.refreshCustomers()
        self.refreshOrderChoices()
        self.refreshReport()
 
 
    def buildReportTab(self):
        top = ttk.Frame(self.report_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Refresh report",
                   command=self.refreshReport).pack(side="left", padx=5)
        ttk.Button(top, text="Save report to file",
                   command=self.saveReport).pack(side="left", padx=5)
        ttk.Button(top, text="Save all data",
                   command=self.saveAll).pack(side="left", padx=5)

        cards = ttk.Frame(self.report_tab)
        cards.pack(fill="x", padx=10, pady=(0, 10))

        self.stat_vars = {}
        for i, (key, title) in enumerate([
            ("revenue", "Total revenue"),
            ("orders", "Orders placed"),
            ("average", "Average order"),
            ("best", "Best seller"),
        ]):
            card = tk.Frame(cards, bg="white", highlightbackground=BORDER,
                            highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            cards.columnconfigure(i, weight=1)

            tk.Label(card, text=title, bg="white", fg="#78716C",
                     font=("Segoe UI", 10)).pack(anchor="w", padx=15, pady=(12, 0))
            var = tk.StringVar(value="-")
            tk.Label(card, textvariable=var, bg="white", fg=PRIMARY_DARK,
                     font=("Segoe UI", 16, "bold"), wraplength=190,
                     justify="left").pack(anchor="w", padx=15, pady=(2, 12))
            self.stat_vars[key] = var

        table = ttk.Frame(self.report_tab)
        table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.report_table = ttk.Treeview(
            table, columns=("id", "date", "customer", "items", "total", "payment"),
            show="headings")
        for col, title, width, anchor in [
            ("id", "Order", 70, "center"),
            ("date", "Date", 100, "center"),
            ("customer", "Customer", 220, "w"),
            ("items", "Items", 70, "center"),
            ("total", "Total (N$)", 120, "e"),
            ("payment", "Payment", 120, "center"),
        ]:
            self.report_table.heading(col, text=title)
            self.report_table.column(col, width=width, anchor=anchor)

        self.report_table.tag_configure("odd", background=BG)
        self.report_table.tag_configure("even", background="white")

        scroll = ttk.Scrollbar(table, orient="vertical", command=self.report_table.yview)
        self.report_table.configure(yscrollcommand=scroll.set)
        self.report_table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def refreshReport(self):
        orders = self.store.orders
        self.report_table.delete(*self.report_table.get_children())

        if not orders:
            for var in self.stat_vars.values():
                var.set("-")
            return

        revenue = sum(order.payment.amount for order in orders)

        counts = {}
        for order in orders:
            for item in order.items:
                counts[item.product.name] = counts.get(item.product.name, 0) + item.quantity
        best = max(counts, key=counts.get)

        self.stat_vars["revenue"].set(f"N${revenue:,.2f}")
        self.stat_vars["orders"].set(str(len(orders)))
        self.stat_vars["average"].set(f"N${revenue / len(orders):,.2f}")
        self.stat_vars["best"].set(f"{best.title()} ({counts[best]} sold)")

        newest_first = sorted(orders, key=lambda o: (o.order_date, o.order_id), reverse=True)
        for n, order in enumerate(newest_first):
            self.report_table.insert(
                "", tk.END,
                values=(order.order_id, DateHelper.format(order.order_date),
                        order.customer.name,
                        sum(item.quantity for item in order.items),
                        f"{order.payment.amount:,.2f}",
                        order.payment.paymentType().title()),
                tags=("odd" if n % 2 else "even",))
 
    def saveReport(self):
        try:
            with open("sales_report.txt", "w") as f:
                f.write(self.store.generateSalesReport())
        except OSError as e:
            messagebox.showerror("Cannot save report", str(e))
            return
        messagebox.showinfo("Saved", "Report saved to sales_report.txt")
 
    def saveAll(self):
        try:
            self.store.saveCatalog()
            self.store.saveCustomers()
            self.store.saveOrders()
        except StoreError as e:
            messagebox.showerror("Cannot save", str(e))
            return
        messagebox.showinfo("Saved", "Products, customers and orders saved.")
 
    def onClose(self):
        if messagebox.askyesno("Quit", "Save all data before closing?"):
            try:
                self.store.saveCatalog()
                self.store.saveCustomers()
                self.store.saveOrders()
            except StoreError as e:
                messagebox.showerror("Cannot save", str(e))
                return
        self.destroy()
 
 
if __name__ == "__main__":
    StoreApp().mainloop()
 