from datetime import datetime
from atrax import to_datetime

def test_to_datetime():

    assert to_datetime("2025-06-23") == datetime(2025, 6, 23)
    assert to_datetime(["06/23/2025", "06/24/2025"]) == [
        datetime(2025, 6, 23), datetime(2025, 6, 24)
    ]