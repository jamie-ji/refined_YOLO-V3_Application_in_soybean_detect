import argparse
from logging import FATAL
import time
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, non_max_suppression, apply_classifier, scale_coords, \
    xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized
import globalvar as gl
import numpy as np
from sklearn.cluster import KMeans

def detect(save_img=False):
    source, weights, view_img, save_txt, imgsz = gl.get_value("opt").source, gl.get_value("opt").weights, gl.get_value("opt").view_img, gl.get_value("opt").save_txt, gl.get_value("opt").img_size
    
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://'))
    
    X=np.array([[0,0]])
    num = 0
    # Directories
    save_dir = Path(increment_path(Path(gl.get_value("opt").project) /gl.get_value("opt").name, exist_ok=gl.get_value("opt").exist_ok))  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(gl.get_value("opt").device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = True
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
    else:
        save_img = True
        dataset = LoadImages(source, img_size=imgsz)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=gl.get_value("opt").augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, gl.get_value("opt").conf_thres,gl.get_value("opt").iou_thres, classes=gl.get_value("opt").classes, agnostic=gl.get_value("opt").agnostic_nms)
        t2 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f'{n} {names[int(c)]}s, '  # add to string
                    #对应的检测个数
                    num += n.item();
                    #print(str(n.item()))

            # Write results
            c=0
            for *xyxy, conf, cls in reversed(det):
                if save_txt:  # Write to file
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    
                    tmp=np.array([[xywh[1],0]])
                    if(c==0):
                        X = X + tmp
                    else:
                        X=np.append(X,tmp,axis=0)
                    
                    
                    #print(xywh[1])
                    c=c+1
                    
                    line = (cls, *xywh, conf) if gl.get_value("opt").save_conf else (cls, *xywh)  # label format
                    with open(txt_path + '.txt', 'a') as f:
                        f.write(('%g ' * len(line)).rstrip() % line + '\n')

                if save_img or view_img:  # Add bbox to image
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
            
            #print(X)
                
            n=gl.get_value("km")


            print("聚类数："+str(n))

            #聚类：
            kmeans = KMeans(n_clusters=n, random_state=0, ).fit(X)	#聚类    
            centpoint = kmeans.cluster_centers_[:,0]	#质心
            #计数
            cnt = np.zeros(n)	
            for i, c in enumerate(kmeans.labels_):
                cnt[c] += 1        
            #print(cnt)  
            
            
            
            
            
            # Print time (inference + NMS)
            #print(f'{s}Done. ({t2 - t1:.3f}s)')

            # Stream results
            if view_img:
                cv2.imshow(str(p), im0)

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                else:  # 'video'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer

                        fourcc = 'mp4v'  # output video codec
                        fps = vid_cap.get(cv2.CAP_PROP_FPS)
                        w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                    vid_writer.write(im0)
        X=np.array([[0,0]])
    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        print(f"Results saved to {save_dir}{s}")

        #print(f'Done. ({time.time() - t0:.3f}s)')
    return num,cnt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='weights\YOLOV3+CIOU.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default=r'images', help='source')  # file/folder, 0 for webcam
   
    parser.add_argument('--img-size', type=int, default=992, help='inference size (pixels)')
    #置信度
    parser.add_argument('--conf-thres', type=float, default=0.2, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    # 去掉label
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')

    #保存文件路径
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    #文件夹名
    parser.add_argument('--name', default='exp', help='save results to project/name')
    
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    
    opt = parser.parse_args()
    #print(opt)
    #check_requirements()

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov3.pt', 'yolov3-spp.pt', 'yolov3-tiny.pt']:
                num,cnt = detect(False,opt)
                strip_optimizer(opt.weights)
        else:
            num,cnt = detect(False,opt)
    #对应的num就是检测模型的检测个数
    print("检测对象数:"+str(num)+"第一行："+str(cnt[0])+"  第二行"+str(cnt[1]))
