from datetime import datetime

class Application:
    def __init__(self, id, partner_id, status, created_at=None):
        self.id = id
        self.partner_id = partner_id
        self.status = status
        self.created_at = created_at or datetime.now()
        self.items = []

    def calculate_total(self):
        return sum(item['product'].price * item['quantity'] for item in self.items)

    def add_item(self, product, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.items.append({'product': product, 'quantity': quantity})

    def validate(self):
        if not self.items:
            raise ValueError("Application must have at least one item")
        if self.calculate_total() <= 0:
            raise ValueError("Total amount must be positive")
