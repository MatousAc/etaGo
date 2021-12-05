# defines a few helper functions
def eq(f1, f2, allowed_error = 1e-2):
  return abs(f1 - f2) <= allowed_error
def print_dict_list(list):
  print("[")
  for entry in list:
    print(" {")
    if entry == None:
      print(entry)
      continue
    for key, value in entry.items():
      print(f"  {key[0:2] + key[3] if (key[0] == '1') else key[0:3]}: {(value)}")
    print(" }")
  print("]")
