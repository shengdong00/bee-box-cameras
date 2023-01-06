#coding=utf-8
from header import *

def generate_mp4(path, image_list):
    print('\nGenerating video... '+path)
    image_list.sort()
    t_steps = []
    for i in range(len(image_list)-1):
        im0_stamp = image_list[i][:-4].split('_')
        t0 = int(im0_stamp[-1])/1e6 + int(im0_stamp[-2]) + int(im0_stamp[-3])*60 + int(im0_stamp[-4])*60*60
        im1_stamp = image_list[i+1][:-4].split('_')
        t1 = int(im1_stamp[-1])/1e6 + int(im1_stamp[-2]) + int(im1_stamp[-3])*60 + int(im1_stamp[-4])*60*60
        t_steps.append(t1-t0)
    frame_rate = 1/np.mean(t_steps)
    
    size = (2448, 2048) #(width, height)
    four_cc = cv2.VideoWriter_fourcc(*'mp4v')

    # cam_id = 'camID'
    # video_name = cam_id+image_list[0][-31:-4]+'-'+image_list[-1][-19:-4]
    video_name = path.split('/')[2]
    if not os.path.exists('./saved_video/'):
        os.mkdir('./saved_video/')
    videowriter = cv2.VideoWriter('./saved_video/'+video_name+'.mp4', four_cc, frame_rate, size)

    for im in image_list:
        img = cv2.imread(path+im)
        # size = (img.shape[1], img.shape[0])
        videowriter.write(img)
    videowriter.release()
    cv2.destroyAllWindows()

    for im in image_list:
        os.remove(path+im)
    
    print('        Successfully generated video.')