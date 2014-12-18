import string



NUMBERS = [0,1,2,3,4,5,6,7,8,9]
BASE_36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LETTERS = [
    'A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
]
PUNCTUATION = [c for c in string.punctuation]


def trans_table(intab="", outab=""):
    return string.maketrans(intab, outab)