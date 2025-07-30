from datetime import datetime, timedelta
from typing import List, Union, Optional, Literal

def to_datetime(values: Union[str, List[str]], fmt: str = None) -> Union[datetime, List[datetime]]:
    """Convert a string or list of strings to datetime objects.

    Parameters:
        value (str | list[str]): The string or list of strings to convert.
        fmt (str): Optional format string for parsing.

    Returns:
        datetime | list[datetime]: A single datetime object if a string is provided,
                                    or a list of datetime objects if a list is provided.
    """
    def parse_single(val: str) -> datetime:
        if fmt:
            return datetime.strptime(val, fmt)
        else:
            # automatic fallback using fromisoformat or common formats
            try: 
                return datetime.fromisoformat(val)
            except ValueError:
                for trial_fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%M-%Y", "%Y/%m/%d"):
                    try:
                        return datetime.strptime(val, trial_fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Cannot parse date: {val}")
    
    if isinstance(values, str):
        return parse_single(values)
    elif isinstance(values, list):
        return [parse_single(val) for val in values]
    else:
        raise TypeError("Input must be a string or a list of strings.")
    
def date_range(
        start: Union[str, datetime],
        end: Optional[Union[str, datetime]] = None,
        periods: Optional[int] = None,
        freq: Literal['D', 'H' 'T', 'min', 'S'] = 'D',
        fmt: Optional[str] = None
)-> List[datetime]:
    """Generate a list of datetime values.

    Parameters:
        start (str | datetime): Start date.
        end (str | datetime): End date Required is 'periods' is not specified.
        periods (int): Number of periods to generate. Required if 'end is not specified
        freq (str): Frequency string ('D'/day, 'H'/hour, 'T'/min, 'min'/min, 'S'/second).
        fmt (str): Optional format string for parsing.

    Returns:
        list[datetime]: List of datetime objects.
    """
    def parse_date(val):
        if isinstance(val, datetime):
            return val
        elif isinstance(val, str):
            if fmt:
                return datetime.strptime(val, fmt)
            else:
                return datetime.fromisoformat(val)
        else:
            raise TypeError("Start and end must be strings or datetime objects.")
        
    start_dt = parse_date(start)

    delta_map = {
        'D': timedelta(days=1),
        'H': timedelta(hours=1),
        'T': timedelta(minutes=1),
        'min': timedelta(minutes=1),
        'S': timedelta(seconds=1)
    }

    if freq not in delta_map:
        raise ValueError(f"Unsupported frequency: {freq}. Supported frequencies are: {list(delta_map.keys())}")
    
    delta = delta_map[freq]

    if end is not None:
        end_dt = parse_date(end)
        result = []
        current = start_dt
        while current <= end_dt:
            result.append(current)
            current += delta
        return result
    elif periods is not None:
        return [start_dt + i * delta for i in range(periods)]
    else:
        raise ValueError("Either 'end' or 'periods' must be specified.")