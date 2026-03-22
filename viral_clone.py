
# ==============================
# CLONE VIRAL TOPIC
# ==============================

import requests
import os
import random

def generate_variations(topic):
    templates = [
        "{} - cơ hội lớn ít ai thấy",
        "{} - cảnh báo quan trọng",
        "{} - điều 90% F0 không biết",
        "{} - bạn đang làm sai điều này",
        "{} - tín hiệu trước khi tăng mạnh",
        "{} - dấu hiệu sắp sập?"
    ]

    return [topic] + [t.format(topic) for t in random.sample(templates, 3)]
