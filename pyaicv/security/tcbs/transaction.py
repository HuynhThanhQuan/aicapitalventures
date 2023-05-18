


class TCBSTransactionHistoryManagement:
    def __init__(self):
        self.factory = {}

    def set(self, customer_name, txn_data):
        inst = CustomerTransactionHistory(customer_name, txn_data)
        self.factory[customer_name] = inst

    def get(self, customer_name):
        return self.factory[customer_name]

    def write_from_drive(self, data):
        groups = data.groupby('Khách hàng')
        for customer_name, txn_data in groups:
            self.set(customer_name, txn_data)

class CustomerTransactionHistory:
    def __init__(self, name, txn_data=None):
        self.name = name
        self.txn_data = txn_data

    def set_transaction_data(self, data):
        self.txn_data = data

    def get_transaction_data(self):
        return self.txn_data


