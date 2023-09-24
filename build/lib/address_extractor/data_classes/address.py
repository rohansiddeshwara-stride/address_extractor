# data_classes/address.py

class Address:
    def __init__(self, text, bbox):
        self.text = text
        self.bbox = bbox
        self.name = "address"
