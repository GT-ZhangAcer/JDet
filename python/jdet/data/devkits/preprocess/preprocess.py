import cv2
import argparse
import os
from jdet.config import init_cfg, get_cfg
from jdet.data.devkits.ImgSplit_multi_process import process
from jdet.data.devkits.convert_data_to_mmdet import convert_data_to_mmdet
from jdet.data.devkits.fair_to_dota import fair_to_dota

def clear(cfg):
    os.system(f"rm -rf {os.path.join(cfg.source_dataset_path, 'trainval')}")
    os.system(f"rm -rf {os.path.join(cfg.target_dataset_path)}")

def run(cfg):
    if (cfg.type=='FAIR'):
        for task in cfg.convert_tasks:
            print('==============')
            print("convert to dota:", task)
            fair_to_dota(os.path.join(cfg.source_fair_dataset_path, task), os.path.join(cfg.source_dataset_path, task))
    for task in cfg.tasks:
        label = task.label
        cfg_ = task.config
        print('==============')
        print("processing", label)

        subimage_size=600 if cfg_.subimage_size is None else cfg_.subimage_size
        overlap_size=150 if cfg_.overlap_size is None else cfg_.overlap_size
        multi_scale=[1.] if cfg_.multi_scale is None else cfg_.multi_scale
        horizontal_flip=False if cfg_.horizontal_flip is None else cfg_.horizontal_flip
        vertical_flip=False if cfg_.vertical_flip is None else cfg_.vertical_flip
        rotation_angles=[0.] if cfg_.rotation_angles is None else cfg_.rotation_angles
        assert(rotation_angles == [0.]) #TODO support multi angles
        assert(horizontal_flip == False) #TODO support horizontal_flip
        assert(vertical_flip == False) #TODO support vertical_flip

        assert(label in ['trainval', 'train', 'val', 'test'])
        in_path = os.path.join(cfg.source_dataset_path, label)
        out_path = os.path.join(cfg.target_dataset_path, label)
        # generate trainval
        if (label == 'trainval' and (not os.path.exists(in_path))):
            out_img_path = os.path.join(cfg.source_dataset_path, 'trainval', 'images')
            out_label_path = os.path.join(cfg.source_dataset_path, 'trainval', 'labelTxt')
            os.makedirs(out_img_path)
            os.makedirs(out_label_path)
            # TODO support Windows etc.
            os.system(f"cp {os.path.join(cfg.source_dataset_path, 'train', 'images', '*')} {out_img_path}")
            os.system(f"cp {os.path.join(cfg.source_dataset_path, 'val', 'images', '*')} {out_img_path}")
            os.system(f"cp {os.path.join(cfg.source_dataset_path, 'train', 'labelTxt', '*')} {out_label_path}")
            os.system(f"cp {os.path.join(cfg.source_dataset_path, 'val', 'labelTxt', '*')} {out_label_path}")
        target_path = process(in_path, out_path, subsize=subimage_size, gap=overlap_size, rates=multi_scale)
        if (label != "test"):
            print("converting to mmdet format...")
            print(cfg.type)
            convert_data_to_mmdet(target_path, os.path.join(target_path, 'labels.pkl'), type=cfg.type)

def main():
    parser = argparse.ArgumentParser(description="Jittor DOTA data preprocess")
    parser.add_argument(
        "--config-file",
        default="",
        metavar="FILE",
        help="path to config file",
        type=str,
    )
    parser.add_argument(
        "--clear",
        default=False,
        action='store_true'
    )
    args = parser.parse_args()
    if args.config_file:
        init_cfg(args.config_file)
    cfg = get_cfg()
    print(cfg.dump())

    if (args.clear):
        clear(cfg)
    else:
        run(cfg)

if __name__ == "__main__":
    main()