import unicodedata

def remove_accents(accented_string):
    return unicodedata.normalize('NFKD', accented_string).encode('ASCII', 'ignore').upper().decode("utf-8")

if __name__ == "__main__":
    print(remove_accents("ódontologíá"))
