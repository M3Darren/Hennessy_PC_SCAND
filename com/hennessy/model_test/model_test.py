import cv2
import imagehash
import numpy as np
from PIL import ImageOps, Image


class ModelTest:
    @staticmethod
    def opencv_test(image_path):
        img = cv2.imread(image_path)
        if len(img.shape) == 2:
            return "Grayscale"
        elif len(img.shape) == 3:
            b, g, r = cv2.split(img)
            if np.array_equal(b, g) and np.array_equal(g, r):
                unique_vals = np.unique(b)
                if set(unique_vals).issubset({0, 255}):
                    return "Black and White"
                return "Grayscale-like"
            else:
                return "Color"
        else:
            return "Unknown type"


def convert_to_bw(image, threshold=128):
    """
    将图像转换为黑白二值图像
    :param image: PIL 图像对象
    :param threshold: 二值化阈值（默认128）
    :return: 黑白二值化后的 PIL 图像
    """
    # 转为灰度图
    gray_image = ImageOps.grayscale(image)

    # 二值化
    bw_image = gray_image.point(lambda x: 255 if x > threshold else 0, '1')
    return bw_image


def compute_phash_bw(image_path, threshold=128):
    """
    对黑白化后的图像计算感知哈希值
    :param image_path: 图像文件路径
    :param threshold: 黑白化阈值
    :return: pHash 哈希值
    """
    # 打开图像
    image = Image.open(image_path)

    # 转换为黑白图
    bw_image = convert_to_bw(image, threshold)
    bw_image.save('save.jpg')
    # 计算感知哈希
    return imagehash.phash(bw_image)


def compare_images_phash(image1_path, image2_path, threshold=128):
    """
    比较两张图像的黑白化 pHash 相似度
    :param image1_path: 第一张图像路径
    :param image2_path: 第二张图像路径
    :param threshold: 黑白化阈值
    :return: 相似度（范围 0-1）
    """
    # 计算两张图像的黑白化 pHash
    hash1 = compute_phash_bw(image1_path,threshold)
    hash2 = compute_phash_bw(image2_path,threshold)

    # 计算汉明距离
    hamming_distance = hash1 - hash2

    # 相似度计算：1 - 标准化的汉明距离
    similarity = 1 - (hamming_distance / len(hash1.hash))
    return similarity

image1 = "A4_0_ref.jpg"
image2 = "scan0004.jpeg"

# 比较两张图像的相似度
similarity = compare_images_phash(image2, image1, threshold=128)
print(f"Image Similarity (pHash with BW conversion): {similarity:.2f}")

