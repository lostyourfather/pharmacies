from dataclasses import dataclass


@dataclass
class AptechestvoItem:
    header: str
    description: str
    price: float
    currency: str
    is_prescription: bool
    img_src: str
    site_name: str


@dataclass
class FarmaniItem:
    header: str
    description: str
    price: float
    currency: str
    is_prescription: bool
    img_src: str
    site_name: str