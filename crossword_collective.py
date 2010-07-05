#!/usr/bin/python

import os.path

from crossword import Crossword

data_dir = "/home/martin/crosswords/"
home_page = "http://www.guardian.co.uk/crosswords/"
css_filename = "/home/martin/cvs/src/crossword_collective/crossword.css"

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
    quick_serial = 12481

ok = True

while ok:
    print "Attempting to create Quick Crossword %d..." % quick_serial

    crossword = Crossword(home_page = home_page, cross_type="quick", data_dir = data_dir, prefix = "quick_crossword", serial_number = str(quick_serial), density = 128, border = 16, border_color = (255,255,255), css_filename = css_filename, smtp_server = smtp_server, from_email_address = from_email_address, to_email_address = to_email_address)
    ok = crossword.create()
    if ok:
        print "created" 
        quick_serial += 1

f = open(next_quick_filename, "w")
f.write(str(quick_serial))
f.close()

# cryptic crossword
# 24909 on 2010-01-16
next_cryptic_filename = os.path.join(data_dir, "next_cryptic.txt")
if os.path.exists(next_cryptic_filename):
    f = open(next_cryptic_filename, "r")
    cryptic_serial = int(f.read())
    f.close()
else:
    cryptic_serial = 25009

ok = True
    
while ok:
    print "Attempting to create Cryptic Crossword %d..." % cryptic_serial

    crossword = Crossword(home_page = home_page, cross_type="cryptic", data_dir = data_dir, prefix = "cryptic_crossword", serial_number = str(cryptic_serial), density = 147, border = 16, border_color = (255,255,255), css_filename = css_filename, smtp_server = smtp_server, from_email_address = from_email_address, to_email_address = to_email_address)
    ok = crossword.create()
    if ok:
        print "created" 
        cryptic_serial += 1
        if cryptic_serial % 6 == 3:
            cryptic_serial += 1

f = open(next_cryptic_filename, "w")
f.write(str(cryptic_serial))
f.close()

# prize crossword
# 24909 on 2010-01-16
next_prize_filename = os.path.join(data_dir, "next_prize.txt")
if os.path.exists(next_prize_filename):
    f = open(next_prize_filename, "r")
    prize_serial = int(f.read())
    f.close()
else:
    prize_serial = 25005

ok = True
    
while ok:
    print "Attempting to create Prize Crossword %d..." % prize_serial

    crossword = Crossword(home_page = home_page, cross_type="prize", data_dir = data_dir, prefix = "prize_crossword", serial_number = str(prize_serial), density = 147, border = 16, border_color = (255,255,255), css_filename = css_filename, smtp_server = smtp_server, from_email_address = from_email_address, to_email_address = to_email_address)
    ok = crossword.create()
    if ok:
        print "created" 
        prize_serial += 6

f = open(next_prize_filename, "w")
f.write(str(prize_serial))
f.close()
