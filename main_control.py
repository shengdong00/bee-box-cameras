#coding=utf-8
from header import *

import mvsdk
import define_camera
from sequence import location

def main_loop():
	# load datasheet
	df = pd.read_excel('./camera_sequence.xlsx', index_col=0)

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
	
	zero_time = time.time()
	# TODO: 等待滑轨移动到位？
	start_time = time.time()
	round, turn = 0, 0

	round += 1

	
	turn += 1
	turn_start = time.time()
	turn_time = turn_start
	while (cv2.waitKey(1) & 0xFF) != ord('q') and turn_time<15*60:
		for cam in cams:
			camID = cam.DevInfo.acSn.decode("utf-8")
			path = './image_storage/rail{}_loc{}_room{}_round{}_turn{}_cam{}/'.format(
				str(df.loc(camID, 'rail')),
				df.loc(camID, 'turn')[(round-1)*4 + turn-1],
				str(df.loc(camID, 'room')),
				str(round),
				str(turn),
				camID
			)
			if not os.path.exists(path):
				os.mkdir(path)
			frame = cam.grab(im_path=path)
			if frame is not None:
				frame = cv2.resize(frame, (640,480), interpolation = cv2.INTER_LINEAR)
				cv2.imshow("{} Press q to end".format(camID, frame))
		turn_time = time.time()-turn_start
	# TODO: write into mp4 videos


if __name__=='__main__':
    try:
        main_loop()
    finally:
        cv2.destroyAllWindows()