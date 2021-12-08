import math

# defines a few helper functions
def eq(f1, f2, allowed_error = 1e-3):
  return abs(f1 - f2) <= allowed_error
def print_dict_list(list):
  print("[")
  for entry in list:
    print(" {")
    if entry == None:
      print(entry)
      continue
    for key, value in entry.items():
      if value == -1: continue
      print(f"  {key[0:2] + key[3] if (key[0] == '1') else key[0:3]}: {(value)}")
    print(" }")
  print("]")

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    from: https://kodify.net/python/math/truncate-decimals/
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor
