import os.path
import urllib
import smtplib
import StringIO

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from lxml import etree
from lxml.html.soupparser import fromstring
from lxml.cssselect import CSSSelector

from PIL import Image

from parser import MyHTMLParser 
from line import Line

class Crossword(object):
    XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"

    def __init__(self, home_page, cross_type, data_dir, prefix, serial_number, density, border, border_color, smtp_server = None, from_email_address = None, to_email_address = None):
        self.home_page = home_page
        self.cross_type = cross_type

        dir = os.path.join(data_dir,str(serial_number))
        self.dir = dir
        self.mkdir(dir)
        self.prefix = prefix
        self.serial_number = serial_number
        self.density = density
        self.border = border
        self.border_color = border_color
        self.basename = self.prefix + "_" + self.serial_number
        self.smtp_server = smtp_server
        self.from_email_address = from_email_address
        self.to_email_address = to_email_address

    def mkdir(self, dir):
        if not os.path.isdir(dir):
            os.mkdir(dir)

    def download_pdf(self):
        url = self.home_page + self.cross_type + "/" + self.serial_number
        
        content = urllib.urlopen(url).read()

        root = fromstring(content)

        selector = CSSSelector('p#stand-first a')

        pdf_url = False
        
        for element in selector(root):
            href = element.get("href")
            if href != None and href[-4:] == ".pdf":
                pdf_url = href

        if pdf_url:
            pdf_stream = urllib.urlopen(pdf_url)

            pdf_basename = pdf_url[pdf_url.rfind("/") + 1:]
            self.basename = pdf_basename[:-4]
            self.pdf_filename = os.path.join(self.dir, pdf_basename)

            self.mkdir(self.dir)
            pdf_file = open(self.pdf_filename, "w")
                            
            while True:
                buffer = pdf_stream.read(1024)

                if buffer == "":
                    break

                pdf_file.write(buffer)

            pdf_file.close()
            pdf_stream.close()

            return True

        return False

    def tag_matches(self, element, tag):
        return element.tag == tag or element.tag == "{%s}%s" % (self.XHTML_NAMESPACE, tag)
    
    def convert_to_png(self):
        # Hmmm...

        png_basename = self.basename + ".png"
        self.png_filename = os.path.join(self.dir, png_basename)

        command = "convert -alpha off -density %s %s[0] -trim +repage -format png32 -depth 3 -define png:color-type=2 %s" % (self.density, self.pdf_filename, self.png_filename)

        ok = os.system(command)

        if ok == 0:
            image = Image.open(self.png_filename)
            self.image_width = image.size[0]
            self.image_height = image.size[1]
        
        return (ok == 0)

    def find_grid(self):
        image = Image.open(self.png_filename)
        pixels = image.load()

        threshold = 300

        x_lines = []

        for y in range (0, self.image_height):
            x_count = 0
            for x in range (0, self.image_width):
                if (pixels[x, y] == (255,255,255) or x + 1 == self.image_width):
                    if x_count > threshold:
                        x_lines.append(Line(x - x_count, y, x, y))

                    x_count = 0
                else:
                    x_count += 1

        freq = {}

        for line in x_lines:
            width = line.end_x - line.start_x

            n = freq.get(width, 0)

            freq[width] = n + 1


        max_count = 0
        mode_width = None

        for k, v in freq.iteritems():
            if v > max_count:
                max_count = v
                mode_width = k

        first_y = None
        last_y = None

        num_grid_lines = 0

        previous_y = None

        for line in x_lines:
            if line.end_x - line.start_x == mode_width:

                # only count non-adjacent lines
                if previous_y == None or line.start_y - previous_y > 1:
                    num_grid_lines += 1
                    previous_y = line.start_y
                    
                if first_y == None:
                    first_y = line
                    
                last_y = line

        self.grid_x = first_y.start_x
        self.grid_y = first_y.start_y

        self.grid_width = mode_width
        self.grid_height = mode_width

        if num_grid_lines < 2:
            print "Not enough grid lines"
            return False

        self.grid_size = num_grid_lines - 1
        self.square_size = mode_width / self.grid_size

        return True

    def reformat(self):
        image_in = Image.open(self.png_filename)

        if self.image_width - self.grid_width < 50:
            # move the clues right of the grid
            width_out = self.image_width * 2 + self.border * 3
            grid_height = self.grid_y + self.grid_height
            clues_height = self.image_height - self.grid_height
            if clues_height > self.grid_height:
                height_out = clues_height
            else:
                height_out = self.grid_height + self.border * 2

            image_out = Image.new(image_in.mode,
                                  (width_out, height_out),
                                  self.border_color)
            
            grid_box = (0, 0, self.image_width, grid_height)

            grid = image_in.crop(grid_box)
            image_out.paste(grid, (self.border, self.border))

            clues = image_in.crop((0, grid_height + 1,
                                   self.image_width, self.image_height))
            image_out.paste(clues, (self.image_width + self.border * 2 + 1,
                                    self.border))

        else:
            width_out = self.image_width + self.border * 2
            height_out = self.image_height + self.border * 2
            image_out = Image.new(image_in.mode,
                                  (width_out, height_out),
                                  self.border_color)

            image_out.paste(image_in, (self.border, self.border))
            

        self.image_width = width_out
        self.image_height = height_out
        self.grid_x += self.border
        self.grid_y += self.border
        
        image_out.save(self.png_filename);
            
        return True

    def create_pdf_html(self):
        html_basename = self.basename + "_pdf.html"
        self.html_filename = os.path.join(self.dir, html_basename)
        html_file = open(self.html_filename, "w")
        image = Image.open(self.png_filename).convert("1")

        pixels = image.load()

        html_file.write("<div id=\"v6vf\" style=\"text-align: left;\">\n")
        html_file.write("\t<img src=\"\" width=\"%d\" height=\"%d\">\n" % (self.image_width, self.image_height))
        html_file.write("\t<div>\n")
        html_file.write("\t\t<table>\n")

        html_file.write("\t\t\t<tbody>\n")

        # make the array one square bigger to cope with the edge pixels
        squares = [[0 for i in range(self.grid_size + 1)] for j in range(self.grid_size + 1)]

        for y in range (0, self.grid_height):
            square_y = y / self.square_size
            for x in range (0, self.grid_width):
                square_x = x / self.square_size

                n = squares[square_x][square_y]

                if pixels[x + self.grid_x, y + self.grid_y] == 0:
                    # black
                    n = n - 1
                else:
                    # white
                    n = n + 1
                    
                squares[square_x][square_y] = n

        for square_y in range (0, self.grid_size):
            html_file.write("\t\t\t\t<tr>\n")
            for square_x in range (0, self.grid_size):
                if squares[square_x][square_y] > 0:
                    cell_class = "white"
                else:
                    cell_class = "black"

                html_file.write("\t\t\t\t\t<td class=\"%s\"><br></td>\n" % cell_class)
            html_file.write("\t\t\t\t</tr>\n")
                
        html_file.write("\t\t\t</tbody>\n")
        html_file.write("\t\t</table>\n")
        html_file.write("\t</div>\n")
        html_file.write("</div>\n")

        html_file.close()

        return True

    def create_pdf_css(self):
        css_basename = self.basename + "_pdf.css"
        self.css_filename = os.path.join(self.dir, css_basename)
        css_file = open(self.css_filename, "w")

        css_file.write("img\n")
        css_file.write("{\n")
        css_file.write("\tposition: absolute;\n")
        css_file.write("\tleft: 0;\n")
        css_file.write("\ttop: 0;\n")
        css_file.write("\tz-index: -1;\n")
        css_file.write("}\n\n")

        css_file.write("table\n")
        css_file.write("{\n")
        css_file.write("\tposition: absolute;\n")
        css_file.write("\tleft: %dpx;\n" % self.grid_x)
        css_file.write("\ttop: %dpx;\n" % self.grid_y)
        css_file.write("\twidth: %dpx;\n" % self.grid_width)
        css_file.write("\theight: %dpx;\n" % self.grid_height)
        css_file.write("\tborder: thin solid black;\n")
        css_file.write("}\n\n")

        css_file.write("td\n")
        css_file.write("{\n")
        css_file.write("\twidth:%dpx;\n" % (self.square_size -4))
        css_file.write("\theight:%dpx;\n" % (self.square_size -4))
        css_file.write("\ttext-align: center;\n")
        css_file.write("\tvertical-align: middle;\n")
        css_file.write("}\n\n")

        css_file.write(".black\n")
        css_file.write("{\n")
        css_file.write("\tbackground-color:#000;\n")
        css_file.write("}\n")

        css_file.close()
        
        return True
    
    def send_email(self):
        message = MIMEMultipart()
        message["Subject"] = "%s Crossword Number %s " % (self.cross_type.capitalize(), self.serial_number)
        message["From"] = self.from_email_address
        message["To"] = self.to_email_address
        message.preamble = message["Subject"]

        f = open(self.html_filename)
        text = MIMEText(f.read(), "html")
        f.close()
        text.add_header("Content-Disposition", "attachment", filename=self.basename + ".html")
        message.attach(text)

        f = open(self.css_filename)
        text = MIMEText(f.read(), "css")
        f.close()
        text.add_header("Content-Disposition", "attachment", filename=self.basename + ".css")
        message.attach(text)

        server = smtplib.SMTP(self.smtp_server)
#        server.set_debuglevel(1)
        server.sendmail(self.from_email_address, self.to_email_address, message.as_string())
        server.quit
        
        return True

    def create(self):
        ok = self.download_pdf()
        if not ok:
            print "Failed to download PDF"
            return False

        ok = self.convert_to_png()
        if not ok:
            print "Failed to convert PDF to PNG"
            return False

        ok = self.find_grid()
        if not ok:
            print "Failed to find grid"
            return False

        ok = self.reformat()
        if not ok:
            print "Failed to reformat"
            return False
            
        ok = self.create_pdf_html()
        if not ok:
            print "Failed to create HTML"
            return False
        
        ok = self.create_pdf_css()
        if not ok:
            print "Failed to create CSS"
            return False
        
        if not self.smtp_server is None:
            ok = self.send_email()
            if not ok:
                print "Failed to send email"
                return False
            
        return True
