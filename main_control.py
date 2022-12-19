#coding=utf-8
from header import *

import mvsdk
import define_camera
# from sequence import location
from generate_mp4 import generate_mp4

def main_loop():
	# load datasheet
	df = pd.read_excel('./camera_sequence.xlsx', index_col=0)

	Total_Turn = 0
	for camID in df.index:
		temp = len(df.loc[camID, 'turn'])
		if Total_Turn!=0 and Total_Turn!=temp:
			print("Total turn doesn't match in cam{}.".format(camID))
			return
		else:
			Total_Turn = temp

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
		print("{}:  {}  rail={}  room={}".format(i, camID, df.loc[camID, 'rail'], df.loc[camID, 'room']))
		cam = define_camera.Camera(DevList[i])
		if cam.open():
			cams.append(cam)
		else:
			print('Failed to open {}'.format(camID))
	
	# TODO: 等待滑轨移动到位
	if input('Press <enter> to start.')=='':
		print("Let's goooo!!!!")
	start_time = time.time()

	total_turn = 0
	while(total_turn<Total_Turn):
		turn_start = time.time()
		
		total_turn += 1
		round = total_turn//4 + 1
		turn = total_turn - round*4
		print("===== round={}  turn={} =====\nProgram has been running for {}sec.".format(round, turn, turn_start-start_time()))
		
		turn_time = turn_start
		while (cv2.waitKey(1) & 0xFF) != ord('q') and turn_time<15*60:
			for cam in cams:
				camID = cam.DevInfo.acSn.decode("utf-8")
				path = './image_storage/rail{}_loc{}_room{}_round{}_turn{}_cam{}/'.format(
					str(df.loc[camID, 'rail']),
					df.loc[camID, 'turn'][total_turn],
					str(df.loc[camID, 'room']),
					str(round).zfill(3),
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

		processes = []
		for cam in cams:
			camID = cam.DevInfo.acSn.decode("utf-8")
			path = './image_storage/rail{}_loc{}_room{}_round{}_turn{}_cam{}/'.format(
				str(df.loc[camID, 'rail']),
				df.loc[camID, 'turn'][total_turn],
				str(df.loc[camID, 'room']),
				str(round),
				str(turn),
				camID
			)
			print("Generating video from '{}'...".format(path))
			raw_list = os.listdir(path)
			im_list = [i for i in raw_list if i[-4:]=='.bmp']
			process = multiprocessing.Process(name=path, target=generate_mp4, args=(path, im_list), daemon=False)
			processes.append(process)
		for pr in processes:
			pr.start()
		save_start = time.time()
		save_time = save_start
		while(save_time<=60*14):
			save_time = time.time()
			c = len(multiprocessing.active_children())
			if c<=0:
				break
		# kill and clean ongoing child-processes
		for process in multiprocessing.active_children():
			process.kill()
			process.close()
			print("Forced process '{}' shutdown".format(process.name))
		wait_time = 30*60 - (time.time()-turn_start)
		time.sleep(wait_time)


if __name__=='__main__':
    try:
        main_loop()
    finally:
        cv2.destroyAllWindows()