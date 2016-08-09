"""
 Angel Olle Blazquez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with This program. If not, see <http://www.gnu.org/licenses/>.
"""
import urllib
import sys,os
import imghdr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from optparse import OptionParser

__author__ = "Angel Olle Blazquez"

# regex_images = r'(?:http|https)://(?:distilleryimage)\d.(?:\w)*.(?:\w)*.(?:com)/(?:\w)*_(?:8|7)(?:.jpg)'

def save_image(imgurl, directory):
  url = imgurl.replace('_6','_8')
  img_name = ''.join([directory, '/', url.split('/')[-1]])
  print "saving %s to %s" % (img_name,directory)
  urllib.urlretrieve(url, img_name)
  if imghdr.what(img_name) is not 'jpeg':
    os.remove(img_name)
    url = url.replace('_8','_7')
    img_name = ''.join([directory, '/', url.split("/")[-1]])
    urllib.urlretrieve(url, img_name)
  print " ... image saved!"


def fetch(url, directory):
  print "Capturing image links from %s . Please wait until the browser is closed." % url
  try:
    ff = webdriver.Firefox()
    ff.implicitly_wait(5)
    ff.get(str(url))
    WebDriverWait(ff, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "more-photos-enabled")))
    ff.execute_script("window.scrollTo(0,Math.max(document.documentElement.scrollHeight,"+ "document.body.scrollHeight,document.documentElement.clientHeight));")
    WebDriverWait(ff, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME,"more-label"),"Load more..."))
    ff.execute_script("window.scrollTo(0,Math.max(document.documentElement.scrollHeight,"+ "document.body.scrollHeight,document.documentElement.clientHeight));")

    while True:
       try:
         ff.find_element_by_link_text("Load more...").click()
         WebDriverWait(ff, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME,"more-label"),"Load more..."))
       except:
         break

    for elem in ff.find_elements_by_css_selector("div.Image.iLoaded.iWithTransition"):
      save_image(elem.get_attribute("src"),directory)

  finally:
    ff.quit()
 
 

def main(argv):
  __doc__="""\
Usage: pynst [option] [option]
Download  images from (not own) Instagram profiles, without login and/or access_token.
Once launched, you must wait until the browser is closed.

-a, --address           Instagram address.
-d, --dir               Directory to save image files

Address required.
Default directory: /tmp \
  """

  if '-h' in argv or '--help' in argv:
    print __doc__  
    return 1
  if len(argv) < 2:
    sys.stderr.write("Invalid parameters.\nMinimum required params: <url>\n")
    return 1
  if '-a' not in argv and '--address' not in argv:
     sys.stderr.write("Error. You must specify address.\n")
     return 1

  parser = OptionParser()
  parser.add_option("-a", "--address", dest="address", help="Address of Instagram profile", metavar="ADDRESS")
  parser.add_option("-d", "--dir", dest="dir", default="/tmp", help="Directory to save image files", metavar="DIR")
  (options, args) = parser.parse_args()

  if ('-d' in argv or '--dir' in argv) and not os.path.exists(options.dir):
    sys.stderr.write("Error: The %s path to store data not found! Please, first create it\n" % argv[2])
    return 1
  print "Checking url availability..."
  if urllib.urlopen(options.address).getcode() is not 200:
    sys.stderr.write("Error. URL not available\n")
    return 1
  print " ...available!\n"

  fetch(options.address,options.dir)



if __name__ == "__main__":
  sys.exit(main(sys.argv))
