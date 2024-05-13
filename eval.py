
def remove_ending_punctuation(text:str):
  """Removes the ending punctuation mark from a string.

  Args:
    text: The string to process.

  Returns:
    The string with the last punctuation mark removed, 
    or the original string if no punctuation is found.
  """

  punctuations = ";.,"

  # Check if the string is empty
  if not text:
    return text

  # Get the last character
  last_char = text[-1]

  # Remove last character if it's punctuation
  if last_char in punctuations:
    return text[:-1]
  else:
    return text
  

def decode(text):
    if "#" in text:
        elems = text.split("#")
        elems = [remove_ending_punctuation(e.strip().lower()) for e in elems]
        elems = [element for element in elems if element != '']

        return elems
    else:
        return []
    

