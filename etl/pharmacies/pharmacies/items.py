from dataclasses import dataclass


@dataclass
class AptechestvoItem:
    header: str
    price: float
    is_prescription: bool
    img_src: str


@dataclass
class FarmaniItem:
    header: str
    description: str
    price: float
    currency: str
    is_prescription: bool
    img_src: str
