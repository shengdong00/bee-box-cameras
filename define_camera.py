#coding=utf-8
from header import *
import mvsdk

exp_time = 20 # define exposure time (ms)
# image_path = './image_storage/'

class Camera(object):
	def __init__(self, DevInfo):
		super(Camera, self).__init__()
		self.DevInfo = DevInfo
		self.hCamera = 0
		self.cap = None
		self.pFrameBuffer = 0

	def open(self):
		if self.hCamera > 0:
			return True

		# 打开相机
		hCamera = 0
		try:
			hCamera = mvsdk.CameraInit(self.DevInfo, -1, -1)
		except mvsdk.CameraException as e:
			print("CameraInit Failed({}): {}".format(e.error_code, e.message) )
			return False

		# 获取相机特性描述
		cap = mvsdk.CameraGetCapability(hCamera)

		# 判断是黑白相机还是彩色相机
		monoCamera = True # (cap.sIspCapacity.bMonoSensor != 0)

		# 黑白相机让ISP直接输出MONO数据，而不是扩展成R=G=B的24位灰度
		if monoCamera:
			mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO12) #NOTE: check image type
		else:
			mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

		# 计算RGB buffer所需的大小，这里直接按照相机的最大分辨率来分配
		FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)

		# 分配RGB buffer，用来存放ISP输出的图像
		# 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
		pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

		# 相机模式切换成连续采集
		mvsdk.CameraSetTriggerMode(hCamera, 0)

		# 手动曝光，曝光时间(ms)
		mvsdk.CameraSetAeState(hCamera, 0)
		mvsdk.CameraSetExposureTime(hCamera, exp_time * 1000)

		# 让SDK内部取图线程开始工作
		mvsdk.CameraPlay(hCamera)

		self.hCamera = hCamera
		self.pFrameBuffer = pFrameBuffer
		self.cap = cap
		return True

	def close(self):
		if self.hCamera > 0:
			mvsdk.CameraUnInit(self.hCamera)
			self.hCamera = 0

		mvsdk.CameraAlignFree(self.pFrameBuffer)
		self.pFrameBuffer = 0

	def grab(self, im_path):
		# 从相机取一帧图片
		hCamera = self.hCamera
		pFrameBuffer = self.pFrameBuffer
		try:
			pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)
			mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
			mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)


			# 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
			# 把图片保存到硬盘文件中
			image_name = self.DevInfo.acSn.decode("utf-8")+'_'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
			status = mvsdk.CameraSaveImage(hCamera, im_path+image_name+".bmp", pFrameBuffer, FrameHead, mvsdk.FILE_BMP_8BIT, 100) # TODO: check image type
			if status == mvsdk.CAMERA_STATUS_SUCCESS:
				# print("Save image successfully. {}.bmp  image_size = {}X{}".format(image_name, FrameHead.iWidth, FrameHead.iHeight) )
				print("\r","Save image successfully. {}.bmp  image_size = {}X{}".format(image_name, FrameHead.iWidth, FrameHead.iHeight), end="",flush=True)	# object为需要打印的内容
			else:
				print("Save image failed. err={}".format(status) )

			# windows下取到的图像数据是上下颠倒的，以BMP格式存放。转换成opencv则需要上下翻转成正的
			# linux下直接输出正的，不需要上下翻转
			if platform.system() == "Windows":
				mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)
			
			# 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
			# 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
			frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
			frame = np.frombuffer(frame_data, dtype=np.uint8)
			frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )
			return frame
		except mvsdk.CameraException as e:
			if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
				print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message) )
			return None