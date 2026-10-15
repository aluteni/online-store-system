class StoreError(Exception):
    """Base class for all OnlineStore errors."""
    pass

class OutOfStockError(StoreError):
    def __init__(self, product_name, available):
        super().__init__(f"Not enough stock for {product_name}. Only {available} left.")
        self.product_name = product_name
        self.available = available

class ProductNotFoundError(StoreError):
    pass

class InvalidPaymentError(StoreError):
    pass

class ExpiredProductError(StoreError):
    pass

class DuplicateCustomerError(StoreError):
    pass

class EmptyQueueError(StoreError):
    pass

class EmptyStackError(StoreError):
    pass

class StoreFileError(StoreError):
    pass