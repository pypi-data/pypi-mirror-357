import logging
from scilens.readers.reader_interface import ReaderInterface
from scilens.components.compare_floats import CompareFloats
from PIL import Image,ImageChops
import io,base64
def data_png_base64(img):A=io.BytesIO();img.save(A,format='PNG');B=base64.b64encode(A.getvalue()).decode('utf-8');return f"data:image/png;base64,{B}"
class ReaderImg(ReaderInterface):
	configuration_type_code='img';category='binary';extensions=['PNG','JPG','JPEG','BMP','TIFF','TIF']
	def close(A):0
	def read(A,reader_options):A.reader_options=reader_options;A.img=Image.open(A.origin.path).convert('RGBA');A.metrics=None
	def compare(F,compare_floats,param_reader,param_is_ref=True):
		N=False;H=param_is_ref;G=param_reader;O=F if H else G;P=F if not H else G;V=F.reader_options;W=N;X=N;A=O.img;D=P.img;Y,I=compare_floats.compare_errors.add_group('pixels','img')
		if A.size!=D.size:I.error=f"Image sizes differ: {A.size} != {D.size}";return
		Q,R=A.size;E=[]
		for B in range(R):
			for C in range(Q):
				J=A.getpixel((C,B));K=D.getpixel((C,B))
				if J!=K:E.append(((C,B),J,K))
		L=None
		if E:
			M=f"Found {len(E)} different pixels.";I.error=M;logging.debug(M)
			for((C,B),S,T)in E[:10]:logging.debug(f"Pixel at ({C}, {B}) differs: {S} vs {T}")
			U=ImageChops.difference(A,D);L=data_png_base64(U)
		else:logging.debug('No pixel differences found.')
		return{'diff_image':L}
	def class_info(A):return{'metrics':A.metrics}