# defines a few helper functions
def eq(f1, f2, allowed_error = 1e-5):
  return abs(f1 - f2) <= allowed_error
