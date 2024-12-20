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


class SimilarityCalculation:
    REFERENCE_IMAGE_PATH = "./images/reference_image/"

    def __init__(self, path1, path2):
        # self.image_euclidean(path1, path2)
        self.image_hash(path1, path2)
        self.image_ssim(path1, path2)
        # self.image_orb(path1, path2)

    def image_cnn(self, path1, path2):
        """使用CNN计算图片的相似度"""

    def image_orb(self, path1, path2):
        """计算图片的orb特征"""

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

        # 计算匹配质量
        similarity = len(matches) / min(len(kp1), len(kp2))
        print(f"ORB：匹配的特征点数量: {len(matches)},匹配质量: {similarity}")

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
        print(f"耗时: {end_time - start_time}")
        print(f"SSIM 相似度: {score}")

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
        print(f"耗时: {end_time - start_time}")
        print(f"whash：{similarity}")

    def image_euclidean(self, path1, path2):
        """计算图片的欧氏距离"""
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
        # 计算相似度指标（百分比）
        similarity = (1 - dist / np.linalg.norm(gray1))
        print(f"欧几里得距离：{similarity}")


def compute_hash(path):
    image = Image.open(path)
    return imagehash.whash(image)


if __name__ == '__main__':
    path1 = "./images/A4-sgqsm.1.jpg"
    path2 = "./images/A4-sgqsm.3.jpg"
    path3 = "./images/BLGT.jpg"
    path4 = "./images/SGQ.jpg"
    #
    # SimilarityCalculation(path1, path2)
    SimilarityCalculation(path2, path3)
    # with Pool() as pool:
    #     paths = [path1, path2]
    #     hashes = pool.map(compute_hash, paths)
    #
    # similarity = 1 - (hashes[0] - hashes[1]) / len(hashes[0].hash)
    # print(f"WHash similarity: {similarity}")
