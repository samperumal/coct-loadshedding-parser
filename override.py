import os
from parse import hash_file, scraped_filename, override_filename

try:
  with open(override_filename + '.md5', 'w') as h:
    print(hash_file(override_filename), file = h)
  
  with open(scraped_filename + '.md5', 'w') as h:
    print(hash_file(scraped_filename), file = h)
except:
  pass