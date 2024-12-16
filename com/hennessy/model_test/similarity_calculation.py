import os
import time
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image
import imagehash
from skimage.metrics import structural_similarity as ssim
import torch
import torchvision.transforms as transforms
from torchvision import models

REFERENCE_IMAGE_PATH = "./images/reference_image/"

resList = []


class SimilarityCalculation:

    def __init__(self, path1, path2):
        self.path1 = path1
        self.path2 = path2

    def get_result(self):
        return [
            self.image_euclidean(self.path1, self.path2),
            self.image_hash(self.path1, self.path2),
            self.image_ssim(self.path1, self.path2),
            self.image_orb(self.path1, self.path2)
        ]

    def image_cnn(self, path1, path2):
        """使用CNN计算图片的相似度"""

    def image_orb(self, path1, path2):
        """计算图片的orb特征"""
        start_time = time.time()
        # 加载图像并转为灰度图
        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)

        # 初始化 ORB 特征点检测器
        orb = cv2.ORB_create()

        # 计算关键点和描述符
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        # 使用 BFMatcher 进行特征匹配
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # 根据距离排序匹配结果
        matches = sorted(matches, key=lambda x: x.distance)
        end_time = time.time()
        # 计算匹配质量
        similarity = len(matches) / min(len(kp1), len(kp2))
        return ('ORB', similarity, round(end_time - start_time, 3))

    def image_ssim(self, path1, path2):
        """计算图片的结构相似性"""
        start_time = time.time()
        # 加载图像并转换为灰度图像
        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)

        # 调整较小的图像大小以匹配较大的图像
        img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # 计算 SSIM
        score, _ = ssim(img1, img2_resized, full=True)
        end_time = time.time()

        return {'name': 'SSIM', 'si': round(score, 3), 'time': round(end_time - start_time, 3)}

    def image_hash(self, path1, path2):
        """计算图片的hash距离"""
        start_time = time.time()
        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)
        # 生成图像的感知哈希
        hash1 = imagehash.whash(Image.fromarray(img1))
        hash2 = imagehash.whash(Image.fromarray(img2))
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        end_time = time.time()

        return {'name': 'whash', 'si': similarity, 'time': round(end_time - start_time, 3)}

    def image_phash(self, path1, path2):
        """计算图片的hash距离"""
        start_time = time.time()
        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)
        # 生成图像的感知哈希
        hash1 = imagehash.phash(Image.fromarray(img1))
        hash2 = imagehash.phash(Image.fromarray(img2))
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        end_time = time.time()

        return {'name': 'phash', 'si': similarity, 'time': round(end_time - start_time, 3)}

    def image_euclidean(self, path1, path2):
        """计算图片的欧氏距离"""
        start_time = time.time()
        # 读取图片
        img1 = cv2.imread(path1)
        img2 = cv2.imread(path2)
        # 转换为灰度图像
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        # 将 gray2 调整为与 gray1 相同的尺寸
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
        # 计算欧几里得距离
        dist = np.linalg.norm(gray2 - gray1)
        end_time = time.time()
        # 计算相似度指标（百分比）
        similarity = (1 - dist / np.linalg.norm(gray1))
        return {'name': '欧几里得距离', 'si': similarity, 'time': round(end_time - start_time, 3)}


def compute_hash(path):
    image = Image.open(path)
    return imagehash.whash(image)


if __name__ == '__main__':
    path1 = "./A41_ref.jpg"
    path2 = "./A4_0_ref.jpg"

    for filename in sorted(os.listdir('./images')):
        file_path = os.path.join('./images', filename)
        print(filename)
        res = SimilarityCalculation(file_path, path2).get_result()
        print(res)
