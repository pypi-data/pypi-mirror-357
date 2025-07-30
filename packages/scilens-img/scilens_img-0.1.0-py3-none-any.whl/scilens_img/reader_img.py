import logging
from scilens.readers.reader_interface import ReaderInterface
from scilens.components.compare_floats import CompareFloats
from PIL import Image,ImageChops
class ReaderImg(ReaderInterface):
	configuration_type_code='img';category='binary';extensions=['PNG','JPG','JPEG','BMP','TIFF','TIF']
	def close(A):0
	def read(A,reader_options):A.reader_options=reader_options;A.img=Image.open(A.origin.path).convert('RGBA');A.metrics=None
	def compare(F,compare_floats,param_reader,param_is_ref=True):
		N=False;H=param_is_ref;G=param_reader;O=F if H else G;P=F if not H else G;U=F.reader_options;V=N;W=N;A=O.img;D=P.img;X,I=compare_floats.compare_errors.add_group('pixels','img')
		if A.size!=D.size:I.error=f"Image sizes differ: {A.size} != {D.size}";return
		Q,R=A.size;E=[]
		for B in range(R):
			for C in range(Q):
				J=A.getpixel((C,B));K=D.getpixel((C,B))
				if J!=K:E.append(((C,B),J,K))
		if E:
			L=f"Found {len(E)} different pixels.";I.error=L;logging.debug(L)
			for((C,B),S,T)in E[:10]:logging.debug(f"Pixel at ({C}, {B}) differs: {S} vs {T}")
			M=ImageChops.difference(A,D);M.show();M.save('difference.png')
		else:logging.debug('No pixel differences found.')
	def class_info(A):return{'metrics':A.metrics}