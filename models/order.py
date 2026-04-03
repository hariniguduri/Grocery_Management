class Order:
    def __init__(self, id_, buyer_id, status, total, created_at):
        self.id = id_
        self.buyer_id = buyer_id
        self.status = status
        self.total = total
        self.created_at = created_at
