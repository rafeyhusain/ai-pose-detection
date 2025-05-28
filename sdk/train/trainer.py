import os
import shutil
import random
import zipfile
from pathlib import Path
from ultralytics import YOLO

from sdk.app.logger import Logger

class Trainer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.zip_dir = r"C:\Users\HP\Downloads"
        self.extract_dir = "temp"
        self.target_dir = ".\datasets\cheating"
        self.splits = ['train', 'val', 'test']
        self.split_ratios = [0.7, 0.2, 0.1]  # 70% train, 20% val, 10% test
        self.zip_path = self.get_latest_zip()

    def get_latest_zip(self):
        zips = sorted(Path(self.zip_dir).glob("project-1*.zip"), key=os.path.getmtime, reverse=True)
        if not zips:
            raise FileNotFoundError("❌ No zip files starting with 'project-1' found.")
        self.logger.info(f"📦 Using ZIP: {zips[0]}")
        return str(zips[0])

    def unzip_file(self):
        self.logger.info(f"🔍 Extracting {self.zip_path}...")
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)
        self.logger.info("✅ Unzip complete.")

    def make_dirs(self):
        for split in self.splits:
            os.makedirs(os.path.join(self.target_dir, 'images', split), exist_ok=True)
            os.makedirs(os.path.join(self.target_dir, 'labels', split), exist_ok=True)

    def get_file_stems(self, path):
        return sorted([f.stem for f in Path(path).glob('*.jpg')])

    def copy_and_rename(self, stems, split):
        for stem in stems:
            img_src = os.path.join(self.extract_dir, 'images', f"{stem}.jpg")
            lbl_src = os.path.join(self.extract_dir, 'labels', f"{stem}.txt")
            img_dst = os.path.join(self.target_dir, 'images', split, f"{stem}.jpg")
            lbl_dst = os.path.join(self.target_dir, 'labels', split, f"{stem}.txt")

            if not os.path.exists(img_src):
                self.logger.error(f"Image file not found [{img_src}]")
                continue

            if not os.path.exists(lbl_src):
                self.logger.error(f"Label file not found [{lbl_src}]")
                continue
                
            shutil.copyfile(img_src, img_dst)
            shutil.copyfile(lbl_src, lbl_dst)
    
    def prepare(self):
        self.unzip_file()
        self.make_dirs()

        images = os.path.join(self.extract_dir, 'images')
        stems = self.get_file_stems(images)
        random.shuffle(stems)

        total = len(stems)
        train_end = int(self.split_ratios[0] * total)
        val_end = train_end + int(self.split_ratios[1] * total)

        self.copy_and_rename(stems[:train_end], 'train')
        self.copy_and_rename(stems[train_end:val_end], 'val')
        self.copy_and_rename(stems[val_end:], 'test')

        self.logger.info(f"✅ Dataset ready in: {self.target_dir}")

    def train(self):
        self.logger.info(f"✅ Training YOLO: {self.target_dir}")
        model = YOLO("yolov8n.pt")
        model.train(data="datasets/cheating/cheating.yaml", epochs=100, imgsz=640)
