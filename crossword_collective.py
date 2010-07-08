#!/usr/bin/python

import os.path

from crossword import Crossword

data_dir = "/home/martin/crosswords"
home_page = "http://www.guardian.co.uk/crosswords/"

smtp_server = None
to_email_address = None
from_email_address = None

# quick crossword

next_quick_filename = os.path.join(data_dir, "next_quick.txt")
if os.path.exists(next_quick_filename):
    f = open(next_quick_filename, "r")
    quick_serial = int(f.read())
    f.close()
else:
    quick_serial = 12527

ok = True

while ok:
    print "Attempting to create Quick Crossword %d..." % quick_serial

    crossword = Crossword(home_page = home_page, cross_type="quick", data_dir = data_dir, prefix = "quick_crossword", serial_number = str(quick_serial), density = 128, border = 16, border_color = "#fff", smtp_server = smtp_server, from_email_address = from_email_address, to_email_address = to_email_address)
    ok = crossword.create()
    if ok:
        print "created" 
        quick_serial += 1

f = open(next_quick_filename, "w")
f.write(str(quick_serial))
f.close()

# cryptic crossword
next_cryptic_filename = os.path.join(data_dir, "next_cryptic.txt")
if os.path.exists(next_cryptic_filename):
    f = open(next_cryptic_filename, "r")
    cryptic_serial = int(f.read())
    f.close()
else:
    cryptic_serial = 25054

ok = True
    
while ok:
    print "Attempting to create Cryptic Crossword %d..." % cryptic_serial

    crossword = Crossword(home_page = home_page, cross_type="cryptic", data_dir = data_dir, prefix = "cryptic_crossword", serial_number = str(cryptic_serial), density = 147, border = 16, border_color = "#fff", smtp_server = smtp_server, from_email_address = from_email_address, to_email_address = to_email_address)
    ok = crossword.create()
    if not ok:
        print "Attempting to create Prize Crossword %d..." % cryptic_serial
        
        crossword = Crossword(home_page = home_page, cross_type="prize", data_dir = data_dir, prefix = "prize_crossword", serial_number = str(cryptic_serial), density = 147, border = 16, border_color = "#fff", smtp_server = smtp_server, from_email_address = from_email_address, to_email_address = to_email_address)
        ok = crossword.create()

    if ok:
        print "created" 
        cryptic_serial += 1

f = open(next_cryptic_filename, "w")
f.write(str(cryptic_serial))
f.close()
