#!/usr/bin/python

import os
import sys
import re
import stat
import getopt
from types import MethodType

MODE = "777"

files_rwx = []
pii_info = []

#Regex to extract the PII information from the files
mobile           = re.compile("^[6-9]\d{9}$")
email            = re.compile("([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
aadhaar_number   = re.compile("^[2-9]{1}[0-9]{3}\\s[0-9]{4}\\s[0-9]{4}$")
pan_number       = re.compile("[A-Z]{5}[0-9]{4}[A-Z]{1}")
ccn              = re.compile('((?:(?:\\d{4}[- ]?){3}\\d{4}|\\d{15,16}))(?![\\d])')
btc_address      = re.compile('(?<![a-km-zA-HJ-NP-Z0-9])[13][a-km-zA-HJ-NP-Z0-9]{26,33}(?![a-km-zA-HJ-NP-Z0-9])')
street_address   = re.compile('\d{1,4} [\w\s]{1,20}(?:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|park|parkway|pkwy|circle|cir|boulevard|blvd)\W?(?=\s|$)', re.IGNORECASE)
zip_code         = re.compile(r'\b\d{6}(?:[-\s]\d{4})?\b')

regexes = {
  "Mobile Number" : mobile,
  "Email Address" : email,
  "Aadhaar Number" : aadhaar_number,
  "Pan Card Number" : pan_number,
  "Credit Card Number" : ccn,
  "Bitcoin Address" : btc_address,
  "Street Address" : street_address,
  "Zip Code" : zip_code,
}

try:
      opts, args = getopt.getopt(sys.argv[1:],"hd:",["dir="])
except getopt.GetoptError:
      print ('matrix -d <absolute_directory_path>')
      sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
     print ('matrix -d <absolute_directory_path>')
     sys.exit()
  elif opt in ("-d"):
     path = arg
         
try:
    path
except NameError:
    path = '.'

mode = int(MODE, 8)

# initializing suffix list 
suff_list = ['.txt', '.html', '.css', '.jsp', '.php', '.py', '.rss', '.xhtml', '.asp', '.aspx', '.ppt', '.pptx', '.csv', '.dat', '.db', '.sql', '.tar', '.xml', '.apk', '.ipa', '.bin', '.bat', '.rtf', '.jpeg', '.jpg', '.png', '.exe', '.jar', '.msi', '.py', '.js', '.doc', '.pdf', '.java', '.docx', '.xls', '.xlsx']

#Verify the file permission
def verify_mode(mode, file, path):
    filemode = stat.S_IMODE(os.stat(path).st_mode)
    return filemode == mode

#Traversing files line by line to extract PII information
def check_pii(file, path):
    if file.endswith(tuple(suff_list)):
        for i, line in enumerate(open(path)):
            for k, v in list(regexes.items()):
                for match in re.finditer(v, line):
                    pii = {'file': file, 'line': i+1, 'type': k, 'content' : match.group() }
                    pii_info.append(pii)
                
for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
        path = os.path.join(dirpath, file)
        if verify_mode(mode, file, path):
            files_rwx.append(file)
            
        check_pii(file, path) 
         
if files_rwx:    
    print ("\nList of files with 777 permission:%s \n"% (files_rwx))
else:
    print ("\n\033[0;31;40mNo files found with 777 permission")

if pii_info:    
    print ("\033[1;33;40mHere is the extracted PII information\n")
    print ("\033[1;33;40m{:<20} {:<20} {:<10} {:<10}".format('PII Type', 'File Name', 'Line No.', 'Info Found'))
    for row in pii_info:
        print ("\033[0;36;40m{:<20} {:<20} {:<10} {:<10}".format(row['type'], row['file'], row['line'], row['content']))

else:
    print ("\n\033[0;31;40mNo PII information found")



