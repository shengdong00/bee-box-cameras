#coding=utf-8
from header import *

def get_total_sec(Y, m, d, H, M, S, f):
    # return total seconds from [2023/1/8 0:00] to given time
    within_day_seconds = f/1e6 + S + M*60 + H*3600
    month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
    if Y%4==0:
        month_days[1] = 29
    within_year_days = np.sum(month_days[:m-1]) + d - 1
    before_year_days = 365 * (Y-2023) + (Y-2021)//4
    total_sec = within_day_seconds + (within_year_days + before_year_days)*24*3600
    return total_sec
    

def generate_mp4(path, image_list):
    print('\nGenerating video... '+path)
    image_list.sort()
    t_steps = []
    for i in range(len(image_list)-1):
        im0_stamp = image_list[i][:-4].split('_')
        t0 = get_total_sec(
            int(im0_stamp[-7]), int(im0_stamp[-6]), int(im0_stamp[-5]),
            int(im0_stamp[-4]), int(im0_stamp[-3]), int(im0_stamp[-2]), int(im0_stamp[-1])
        )
        im1_stamp = image_list[i+1][:-4].split('_')
        t1 = get_total_sec(
            int(im1_stamp[-7]), int(im1_stamp[-6]), int(im1_stamp[-5]),
            int(im1_stamp[-4]), int(im1_stamp[-3]), int(im1_stamp[-2]), int(im1_stamp[-1])
        )
        t_steps.append(t1-t0)
    frame_rate = 1/np.mean(t_steps)
    
    size = (2448, 2048) #(width, height)
    four_cc = cv2.VideoWriter_fourcc(*'mp4v')

    # cam_id = 'camID'
    # video_name = cam_id+image_list[0][-31:-4]+'-'+image_list[-1][-19:-4]
    video_name = path.split('/')[2]
    if not os.path.exists('E:/monitor_data/saved_video/'):
        os.mkdir('E:/monitor_data/saved_video/')
    videowriter = cv2.VideoWriter('E:/monitor_data/saved_video/'+video_name+'.mp4', four_cc, frame_rate, size)

    for im in image_list:
        img = cv2.imread(path+im)
        # size = (img.shape[1], img.shape[0])
        videowriter.write(img)
    videowriter.release()
    cv2.destroyAllWindows()

    for im in image_list:
        os.remove(path+im)
    
    print('        Successfully generated video.')