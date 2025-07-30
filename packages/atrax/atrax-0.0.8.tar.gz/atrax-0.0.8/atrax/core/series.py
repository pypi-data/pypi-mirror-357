from datetime import datetime
from .rolling import RollingSeries
from .locators import _Iloc, _Loc
from .customdatetime import _DateTimeAccessor


class Series:

    @property
    def iloc(self):
        return _Iloc(self)

    @property
    def loc(self):
        return _Loc(self)
    
    @property
    def dt(self):
        return _DateTimeAccessor(self)
    


    def __init__(self, data, name=None, index=None):
        """
        One-dimensional labeled array for Atrax.

        Parameters
        ----------
        data : list
            A list of values.
        name : str, optional
            The name of the series.
            defaults to None, which means no name is assigned.

        Examples
        --------
        >>> from atrax import Atrax
        >>> s = Atrax.Series([1, 2, 3, 4], name="numbers")
        >>> print(s)
        0: 1
        1: 2
        2: 3
        3: 4
        """
        self.data = data
        self.name = name or ""
        self.index = index or list(range(len(data)))
        if len(self.data) != len(self.index):
            raise ValueError("Length of index must match length of data.")
        self.dtype = self._infer_dtype()

    def _infer_dtype(self):
        if all(isinstance(x, int) for x in self.data):
            return "int"
        elif all(isinstance(x, (int, float)) for x in self.data):
            return "float"
        elif all(isinstance(x, bool) for x in self.data):
            return "bool"
        elif all(isinstance(x, datetime) for x in self.data):
            return "datetime"
        elif all(isinstance(x, str) for x in self.data):
            return "str"
        else:
            return "object"

    def __repr__(self):
        lines = [f"{idx}   {val}" for idx, val in zip(self.index[:10], self.data[:10])]
        if len(self.data) > 10:
            lines.append(f"...({len(self.data)} total)")
        lines.append(f"Name: {self.name}, dtype: {self.dtype}")
        return "\n".join(lines)
    
    def __len__(self):
        """Get the number of elements in the Series."""
        return len(self.data)
    
    def __getitem__(self, i):
        """Get an item from the Series by index."""
        return self.data[i]
    
    def __gt__(self, other):
        result =  [x > other for x in self.data]
        return Series(result, name=f"({self.name} > {other})")
    
    
    def __lt__(self, other): 
        result =  [x < other for x in self.data]
        return Series(result, name=f"({self.name} < {other})")
    
    def __ge__(self, other):        
        result =  [x >= other for x in self.data]
        return Series(result, name=f"({self.name} >= {other})")
    
    def __le__(self, other):        
        result = [x <= other for x in self.data]
        return Series(result, name=f"({self.name} <= {other})")
    
    def __eq__(self, other):        
        result = [x == other for x in self.data]
        return Series(result, name=f"({self.name} == {other})")
    
    def __ne__(self, other):        
        result = [x != other for x in self.data]
        return Series(result, name=f"({self.name} != {other})")
    
    def _binary_op(self, other, op):
        if isinstance(other, Series):
            if len(other.data) != len(self.data):
                raise ValueError("Cannot perform operation: Series must have the same length.")
            return Series([op(a,b) for a,b in zip(self.data, other.data)], name=self.name)
        else:
            return Series([op(a, other) for a in self.data], name=self.name)

    def __add__(self, other): return self._binary_op(other, lambda a, b: a + b)
    def __sub__(self, other): return self._binary_op(other, lambda a, b: a - b)
    def __mul__(self, other): return self._binary_op(other, lambda a, b: a * b)
    def __truediv__(self, other): return self._binary_op(other, lambda a, b: a / b)
    def __floordiv__(self, other): return self._binary_op(other, lambda a, b: a // b)
    def __mod__(self, other): return self._binary_op(other, lambda a, b: a % b)
    def __pow__(self, other): return self._binary_op(other, lambda a, b: a ** b)

    def __and__(self, other):
        if not isinstance(other, Series):
            raise TypeError("Operand must be a Series.")
        if len(other.data) != len(self.data):
            raise ValueError("Cannot perform operation: Series must have the same length.")
        return Series([a and b for a,b in zip(self.data, other.data)], name=f"({self.name}) & {other.name}")
    
    def __or__(self, other):
        if not isinstance(other, Series):
            raise TypeError("Operand must be a Series.")
        if len(other.data) != len(self.data):
            raise ValueError("Cannot perform operation: Series must have the same length.")
        return Series([a or b for a, b in zip(self.data, other.data)], name=f"({self.name}) | {other.name}")

    def __invert__(self):
        return Series([not x for x in self.data], name=f"(~{self.name})")

    def head(self, n=5):
        """
        Return the first n elements of the Series.
        Parameters:
        n (int): The number of elements to return. Defaults to 5.
        Returns:
        Series: A new Series containing the first n elements.
        """
        return Series(self.data[:n], name=self.name, index=self.index[:n])
    
    def tail(self, n=5):
        """
        Return the last n elements of the Series.
        Parameters:
        n (int): The number of elements to return. Defaults to 5.
        Returns:
        Series: A new Series containing the last n elements.
        """
        return Series(self.data[-n:], name=self.name, index=self.index[-n:])
    
    def unique(self):
        """
        Return the unique values in the Series.
        Returns:
        Series: A new Series containing the unique values.
        """
        unique_data = list(set(self.data))
        return Series(unique_data, name=f"Unique({self.name})", index=list(range(len(unique_data))))
    
    def nunique(self):
        """
        Return the number of unique values in the Series.
        Returns:
        int: The number of unique values.
        """
        return len(set(self.data))
    
    def isin(self, values):
        """
        Check if each element in the Series is in the provided list of values.
        Parameters:
        values (list): A list of values to check against.
        Returns:
        Series: A new Series containing boolean values indicating membership.
        """
        return Series([x in values for x in self.data], name=f"IsIn({self.name})", index=self.index)
    
    def between(self, left, right, inclusive=True):
        """
        Check if each element in the Series is between two values.
        Parameters:
        left (int/float): The lower bound.
        right (int/float): The upper bound.
        inclusive (bool): Whether to include the bounds. Defaults to True.
        Returns:
        Series: A new Series containing boolean values indicating if each element is between the bounds.
        """
        if inclusive:
            return Series([left <= x <= right for x in self.data], name=f"Between({self.name}, {left}, {right})")
        else:
            return Series([left < x < right for x in self.data], name=f"Between({self.name}, {left}, {right}, exclusive)")

    def to_list(self):
        """
        Convert the Series to a list.
        Returns:
        list: The data in the Series as a list.
        """
        return self.data
    
    def apply(self, func):
        return Series([func(x) for x in self.data], name=self.name)
    
    
    def _repr_html_(self):
        """
        Return a string representation of the Series in HTML format.
        Returns:
        str: HTML representation of the Series.
        """
        html = "<table style='border-collapse: collapse;'>"
        for idx, val in zip(self.index[:10], self.data[:10]):
            html += f"<tr><td style=''>{idx}</td>"
            html += f"<td style=''>{val}</td></tr>"
        html += f"<tr><td colspan='2' style='font-size:16px;'><strong>Name: {self.name}, dtype: {self.dtype}<strong></td></tr>"
        if len(self.data) > 10:
            html += f"<tr><td colspan='2'><i>...{len(self.data) - 10} more</i></td></tr>"
        html += "</table>"
        return html 
    
    def to_datetime(self, format='%Y-%m-%d', errors='raise'):
        """
        Convert the Series to datetime objects.
        
        Parameters:
        format (str): The format of the date strings. Defaults to '%m/%d/%Y'.
        errors (str): 'raise' to throw errors, 'coerce' to return None on failure
        
        Returns:
        Series: A new Series with datetime objects.
        """
        converted = []

        for val in self.data:
            if isinstance(val, datetime):
                converted.append(val)
            elif isinstance(val, str):
                try:
                    converted.append(datetime.strptime(val, format))
                except Exception as e:
                    if errors == 'coerce':
                        converted.append(None)
                    else:
                        raise ValueError(f"Failed to parse '{val}' as datetime: {e}")
            else:
                if errors == 'coerce':
                    converted.append(None)
                else:
                    raise ValueError(f"Unsupported type for to_datetime: {type(val)}")
        return Series(converted, name=self.name, index=self.index)
    
    def astype(self, dtype):
        """
        Convert the Series to a specified data type.
        
        Parameters:
        dtype (type): The Python type to cast to (e.g., int, float, str)
        
        Returns:
        Series: A new Series with the converted data type.
        """
        type_map = {
            "int": int,
            "float": float,
            "str": str,
            "object": lambda x: x
        }

        if isinstance(dtype, str):
            cast_fn = type_map.get(dtype)
            if cast_fn is None:
                raise ValueError(f"Unsupported dtype: {dtype}")
        else:
            cast_fn = dtype  # assume it's already a Python type

        new_data = []
        for val in self.data:
            try:
                new_data.append(cast_fn(val))
            except:
                new_data.append(None)

        return Series(new_data, name=self.name, index=self.index)
    
    def rolling(self, window):
        """
        Create a rolling window object for the Series.
        
        Parameters:
        window (int): The size of the rolling window.
        
        Returns:
        RollingSeries: A RollingSeries object for performing rolling operations.
        """
        if not isinstance(window, int) or window <= 0:
            raise ValueError("Window size must be a positive integer.")
        return RollingSeries(self.data, window=window, name=self.name)
    
    def cut(self, bins=4, labels=None, precision=3, tie_breaker='upper'):
        """
        Bin the Series into discrete intervals.
        
        Parameters:
        bins (int): Number of bins to create. Defaults to 4.
        labels (list): Optional labels for the bins. If None, default labels will be used.
        precision (int): Number of decimal places for bin edges. Defaults to 3.
        tie_breaker (str): How to handle ties ('upper', 'lower', 'random'). Defaults to 'upper'.
        
        Returns:
        Series: A new Series with binned data.
        """
        if not self.data:
            return Series([], name=self.name, index=self.index)
        
        clean_data = [v for v in self.data if v is not None]
        min_val, max_val = min(clean_data), max(clean_data)

        if isinstance(bins, int):
            step = (max_val - min_val) / bins
            bin_edges = [round(min_val + i * step, precision) for i in range(bins + 1)]
        else:
            bin_edges = bins

        def assign_bin(val):
            if tie_breaker == 'lower' and val == bin_edges[0]:
                return labels[0] if labels else 0
            
            
            for i in range(len(bin_edges) - 1):
                left = bin_edges[i]
                right = bin_edges[i + 1]
                if tie_breaker == 'upper':
                    if left <= val < right:
                        return labels[i] if labels else i
                else:
                    if left < val <= right:
                        return labels[i] if labels else i
            if val == bin_edges[-1]:
                return labels[-1] if labels else len(bin_edges) - 2
            return None
        
        binned = [assign_bin(v) if v is not None else None for v in self.data]
        return Series(binned, name=self.name, index=self.index)
    
    def rank(self, method='average', ascending=True):
        """
        Compute numerical data ranks (1 through n) along the Series.
        
        Parameters:
        - method: {'average', 'min', 'max', 'first', 'dense'}, default 'average'
        - ascending: boolean, default True
        
        Returns:
        Series: A new Series with ranked values.
        """
        values = self.data
        indexed = list(enumerate(values))

        if not ascending:
            indexed.sort(key=lambda x: -x[1])
        else:
            indexed.sort(key=lambda x: x[1])

        ranks = [0] * len(values)
        cur_rank = 1
        dense_rank = 1
        i = 0

        while i < len(indexed):
            j = i
            # find group of tied values
            while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
                j+= 1

            group = indexed[i:j + 1]
            indices = [idx for idx, _ in group]
            group_size = len(group)

            if method == 'average':
                avg_rank = sum(range(cur_rank, cur_rank + group_size)) / group_size
                for idx in indices:
                    ranks[idx] = avg_rank
            elif method == 'min':
                for idx in indices:
                    ranks[idx] = cur_rank
            elif method == 'max':
                for idx in indices:
                    ranks[idx] = cur_rank + group_size - 1
            elif method == 'first':
                for offset, (idx, _) in enumerate(group):
                    ranks[idx] = cur_rank + offset
            elif method == 'dense':
                for idx in indices:
                    ranks[idx] = dense_rank

            i = j + 1
            cur_rank += group_size
            if method == 'dense':
                dense_rank += 1

        return Series(ranks, name=f"{self.name}_rank", index=self.index)
    
    def map(self, arg):
        """
        Map values of the Series using an input mapping or function.
        
        Parameters:
        arg (dict or function): A mapping dictionary or a function to apply to each value.
        
        Returns:
        Series: A new Series with mapped values.
        """
        if callable(arg):
            mapped = [arg(x) for x in self.data]
        elif isinstance(arg, dict):
            mapped = [arg.get(x, None) for x in self.data]
        else:
            raise TypeError("Argument must be a callable or a dictionary.")
        return Series(mapped, name=f"{self.name}_mapped", index=self.index)
    
    def quantile(self, q):
        """
        Compute the q-th quantile of the Series.
        
        Parameters:
        q (float): The quantile to compute (0 <= q <= 1).
        
        Returns:
        float: The q-th quantile value.
        """
        if not self.data:
            return None if isinstance(q, float) else [None for _ in q]
        
        sorted_data = sorted(x for x in self.data if x is not None)
        n = len(sorted_data)

        def compute_single_quantile(p):
            if not 0 <= p <= 1:
                raise ValueError("Quantile must be between 0 and 1.")
            idx = p * (n-1)
            lower = int(idx)
            upper = min(lower + 1, n-1)
            weight = idx - lower
            return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
        
        if isinstance(q, list):
            return [compute_single_quantile(p) for p in q]
        return compute_single_quantile(q)
    
    def percentile(self, p):
        """ Equivalent to quantile"""
        if isinstance(p, list):
            return self.quantile([x/100 for x in p])
        return self.quantile(p/100)

      
     
    