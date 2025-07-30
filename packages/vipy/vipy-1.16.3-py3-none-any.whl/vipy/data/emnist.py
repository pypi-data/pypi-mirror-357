import os
import numpy as np
from vipy.util import remkdir, tocache, filetail
import gzip
import struct
from array import array
import vipy.image
import string


TRAIN_IMG_URL = 'http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz'
TRAIN_IMG_SHA1 = '6c95f4b05d2bf285e1bfb0e7960c31bd3b3f8a7d'
TRAIN_LBL_URL = 'http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz'
TRAIN_LBL_SHA1 = '2a80914081dc54586dbdf242f9805a6b8d2a15fc'
TEST_IMG_URL = 'http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz'
TEST_IMG_SHA1 = 'c3a25af1f52dad7f726cce8cacb138654b760d48'
TEST_LBL_URL = 'http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz'
TEST_LBL_SHA1 = '763e7fa3757d93b0cdec073cef058b2004252c17'

EMNIST_URL = 'https://biometrics.nist.gov/cs_links/EMNIST/gzip.zip'


class MNIST():
    def __init__(self, datadir=None, redownload=False):        
        raise ValueError('moved to huggingface')

        outdir = tocache('mnist') if datadir is None else datadir
        
        self._datadir = remkdir(os.path.expanduser(outdir))
        if redownload or not os.path.exists(os.path.join(self._datadir, '.complete')):
            vipy.downloader.download(TRAIN_IMG_URL, os.path.join(self._datadir, filetail(TRAIN_IMG_URL)), sha1=TRAIN_IMG_SHA1)
            vipy.downloader.download(TRAIN_LBL_URL, os.path.join(self._datadir, filetail(TRAIN_LBL_URL)), sha1=TRAIN_LBL_SHA1)
            vipy.downloader.download(TEST_IMG_URL, os.path.join(self._datadir, filetail(TEST_IMG_URL)), sha1=TEST_IMG_SHA1)
            vipy.downloader.download(TEST_LBL_URL, os.path.join(self._datadir, filetail(TEST_LBL_URL)), sha1=TEST_LBL_SHA1)            

            open(os.path.join(self._datadir, '.complete'), 'a').close()
            
    @staticmethod
    def _labels(gzfile):
        with gzip.open(gzfile, 'rb') as file:
            magic, size = struct.unpack(">II", file.read(8))
            if magic != 2049:
                raise ValueError('Magic number mismatch, expected 2049,'
                                 'got %d' % magic)
            labels = array("B", file.read())
        return labels

    @staticmethod
    def _imread(dataset, index):
        """Read MNIST encoded images, adapted from: https://github.com/sorki/python-mnist/blob/master/mnist/loader.py"""
        gzfile = None

        with gzip.open(gzfile, 'rb') as file:
            magic, size, rows, cols = struct.unpack(">IIII", file.read(16))
            if magic != 2051:
                raise ValueError('Magic number mismatch, expected 2051, got %d' % magic)
            file.seek(index * rows * cols + 16)
            image = np.asarray(array("B", file.read(rows * cols)).tolist())
            return np.reshape(image, (rows,cols))

    @staticmethod
    def _dataset(img_gzfile, label_gzfile, N):
        y = MNIST._labels(label_gzfile).tolist()
        x = []
        train_img_file = img_gzfile
        with gzip.open(train_img_file, 'rb') as gzfile:
            magic, size, rows, cols = struct.unpack(">IIII", gzfile.read(16))
            if magic != 2051:
                raise ValueError('Magic number mismatch, expected 2051, got %d' % magic)
            x = [np.asarray(array("B", gzfile.read(rows * cols)).tolist(), dtype=np.uint8).reshape((rows, cols)) for k in range(N)]
        return tuple((xi,yi) for (xi,yi) in zip(x,y))

    def trainset(self):
        (labelfile, imgfile, N) = (os.path.join(self._datadir, 'train-labels-idx1-ubyte.gz'), os.path.join(self._datadir, 'train-images-idx3-ubyte.gz'), 60000)
        return vipy.dataset.Dataset(self._dataset(imgfile, labelfile, N=N), loader=lambda z: vipy.image.ImageCategory(array=z[0], category=str(z[1]), colorspace='lum'), id='mnist')
    
    def testset(self):
        (labelfile, imgfile, N) = (os.path.join(self._datadir, 't10k-labels-idx1-ubyte.gz'), os.path.join(self._datadir, 't10k-images-idx3-ubyte.gz'), 10000)                
        return vipy.dataset.Dataset(self._dataset(imgfile, labelfile, N=N), loader=lambda z: vipy.image.ImageCategory(array=z[0], category=str(z[1]), colorspace='lum'), id='mnist_test')



    
class EMNIST(MNIST):
    def __init__(self, datadir=None, redownload=False):
        datadir = tocache('emnist') if datadir is None else datadir
        
        self._datadir = vipy.util.remkdir(datadir)        
        if redownload or not os.path.exists(os.path.join(self._datadir, '.complete')):
            vipy.downloader.download_and_unpack(EMNIST_URL, self._datadir)        
        super().__init__(datadir)

        open(os.path.join(self._datadir, '.complete'), 'a').close()
        
    def letters_train(self):
        (imgfile, labelfile) = (os.path.join(self._datadir, 'gzip/emnist-letters-train-images-idx3-ubyte.gz'), os.path.join(self._datadir, 'gzip/emnist-letters-train-labels-idx1-ubyte.gz'))
        d_categoryidx_to_category = {str(k):x for (k,x) in enumerate(string.ascii_lowercase, start=1)}        
        return vipy.dataset.Dataset(self._dataset(imgfile, labelfile, N=124800), loader=lambda z: vipy.image.ImageCategory(array=z[0], category=d_categoryidx_to_category[str(z[1])], colorspace='lum'), id='emnist_letters_train')

    def letters_test(self):
        (imgfile, labelfile) = (os.path.join(self._datadir, 'gzip/emnist-letters-test-images-idx3-ubyte.gz'), os.path.join(self._datadir, 'gzip/emnist-letters-test-labels-idx1-ubyte.gz'))
        d_categoryidx_to_category = {str(k):x for (k,x) in enumerate(string.ascii_lowercase, start=1)} 
        return vipy.dataset.Dataset(self._dataset(imgfile, labelfile, N=145600-124800), loader=lambda z: vipy.image.ImageCategory(array=z[0], category=d_categoryidx_to_category[str(z[1])], colorspace='lum'), id='emnist_letters_test')       

    def letters(self):
        return (self.letters_train(), self.letters_test())

    def digits_train(self):
        (imgfile, labelfile) = (os.path.join(self._datadir, 'gzip/emnist-digits-train-images-idx3-ubyte.gz'), os.path.join(self._datadir, 'gzip/emnist-digits-train-labels-idx1-ubyte.gz')) 
        return vipy.dataset.Dataset(self._dataset(imgfile, labelfile, N=240000), loader=lambda z: vipy.image.ImageCategory(array=z[0], category=str(z[1]), colorspace='lum'), id='emnist_digits_train')              

    def digits_test(self):
        (imgfile, labelfile) = (os.path.join(self._datadir, 'gzip/emnist-digits-test-images-idx3-ubyte.gz'), os.path.join(self._datadir, 'gzip/emnist-digits-test-labels-idx1-ubyte.gz'))
        return vipy.dataset.Dataset(self._dataset(imgfile, labelfile, N=280000-240000), loader=lambda z: vipy.image.ImageCategory(array=z[0], category=str(z[1]), colorspace='lum'), id='emnist_digits_test')                      

    def digits(self):
        return (self.digits_train(), self.digits_test())
    
    def trainset(self):
        return vipy.dataset.Union(self.letters()[0], self.digits()[0], id='emnist')

    def testset(self):
        return vipy.dataset.Union(self.letters()[0], self.digits()[0], id='emnist_test')        
    

    

    
