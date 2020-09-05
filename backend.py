import socket
import string
import random
from zipfile import ZipFile
import os

temp_dir = 'data'

def filename_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))


s = socket.socket()
host = socket.gethostname()
port = 10069
s.bind((host, port))
s.listen(100)
while True:
    c, addr = s.accept()
    print('Got connection from {}'.format(addr))
    print("Receiving...")
    filename = filename_generator() + '.pack'
    with open(filename, 'wb') as f:
        l = c.recv(1024)
        while (l):
            print ("Receiving...")
            f.write(l)
            l = c.recv(1024)
        c.close()
    outdir = temp_dir + '/' + filename.split('.pack')[0]
    os.mkdir(outdir)
    with ZipFile(filename, 'r') as zippy:
        zippy.extractall(path=outdir)
    with open(outdir + '/meta.dat', 'r') as metadata:
        slug = metadata.readline()
    os.rename(outdir, temp_dir + '/' + slug)




