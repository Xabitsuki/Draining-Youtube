import cv2
import json
import os

def get_dic_info(dir_id):

    info = [el for el in os.listdir(dir_id) if el.endswith('.info.json')]

    path_info = os.path.join(dir_id,info[0])

    with open(path_info) as f:
        dic_info = json.load(f)

    return dic_info

if __name__ == '__main__':

    dir_video = 'videos/'
    dir_id = 'LXb3EKWsInQ/'
    id_ = 'LXb3EKWsInQ_3840x2160' #TODO change hierarchy to not look for video file
    ext = '.webm'
    path_video = '{}{}{}{}'.format(dir_video, dir_id, id_, ext)

    imgs_per_sec = 2

    # Get info on the video and get the rate of frames:
    info = get_dic_info(dir_video+dir_id)
    fps = info['fps']
    duration = info['duration']

    # Start reading video
    vidcap = cv2.VideoCapture(path_video)

    # Read first image
    ret, image = vidcap.read()
    count = 0;

while ret:

    ret, frame = vidcap.read()

    # Take only some images for each second
    if count % (fps/imgs_per_sec) == 0:
        cv2.imwrite("{}{}/frames/frame{}.jpg".format(dir_video,dir_id,count), #TODO create dir for frames
                    frame)

        print(count)
    # exit if Escape is hit
    if cv2.waitKey(10) == 27:
        break

    count += 1
