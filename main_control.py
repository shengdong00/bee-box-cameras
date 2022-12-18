#coding=utf-8
from header import *

import mvsdk
import define_camera
from sequence import location

def main_loop():
	# 枚举相机
	DevList = mvsdk.CameraEnumerateDevice()
	nDev = len(DevList)
	if nDev < 1:
		print("No camera was found!")
		return

	print('Turning on all cameras...')
	cams = []
	for i, DevInfo in enumerate(DevList):
		camID = DevInfo.acSn.decode("utf-8")
		print("{}:  {}  {}".format(i, camID, location(camID)))
		cam = define_camera.Camera(DevList[i])
		if cam.open():
			cams.append(cam)
		else:
			print('Failed to open {}'.format(camID))
	
	while (cv2.waitKey(1) & 0xFF) != ord('q'):
		for cam in cams:
			frame = cam.grab()
			if frame is not None:
				frame = cv2.resize(frame, (640,480), interpolation = cv2.INTER_LINEAR)
				cv2.imshow("{} Press q to end".format(cam.DevInfo.acSn.decode("utf-8")), frame)


if __name__=='__main__':
    try:
        main_loop()
    finally:
        cv2.destroyAllWindows()