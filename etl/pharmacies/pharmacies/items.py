from dataclasses import dataclass


@dataclass
class PharmacyItem:
    header: str
    description: str
    price: float
    currency: str
    is_prescription: bool
    img_src: str
    site_name: str
    link: str
