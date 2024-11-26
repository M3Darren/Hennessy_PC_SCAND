import os
import time

import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def similarity_pHash(path, ref_path):
    # 生成图像的感知哈希

    hash1 = imagehash.phash(Image.open(path))
    hash2 = imagehash.phash(Image.open(ref_path))
    # self.__merge_objects['pil_image_obj'].close()

    # 计算相似度
    similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
    return similarity


def similarity_wHash(path, ref_path):
    # 生成图像的感知哈希

    hash1 = imagehash.whash(Image.open(path))
    hash2 = imagehash.whash(Image.open(ref_path))
    # self.__merge_objects['pil_image_obj'].close()

    # 计算相似度
    similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
    return similarity


# aHash
def average_hash(path, ref_path):
    hash1 = imagehash.average_hash(Image.open(path))
    hash2 = imagehash.average_hash(Image.open(ref_path))
    # self.__merge_objects['pil_image_obj'].close()

    # 计算相似度
    similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
    return similarity


# pHash
def perceptual_hash(image_path, hash_size=8):
    image = Image.open(image_path).convert("L").resize((hash_size * 4, hash_size * 4), Image.RESAMPLE.LANCZOS)
    pixels = np.asarray(image)
    dct = cv2.dct(np.float32(pixels))
    dct_low = dct[:hash_size, :hash_size]
    avg = dct_low.mean()
    return (dct_low > avg).astype(int).flatten()


# dHash
def difference_hash(image_path, hash_size=8):
    image = Image.open(image_path).convert("L").resize((hash_size + 1, hash_size), Image.RESAMPLE.LANCZOS)
    pixels = np.asarray(image)
    diff = pixels[:, 1:] > pixels[:, :-1]
    return diff.astype(int).flatten()


def hamming_distance(hash1, hash2):
    return np.sum(hash1 != hash2)


# 直方图
def histogram_similarity(image_path1, image_path2):
    image1 = cv2.imread(image_path1)
    image2 = cv2.imread(image_path2)
    # # 假设你已经有 PIL 图像对象
    # pil_image1 = Image.open(image_path1)
    # pil_image2 = Image.open(image_path2)
    #
    # # 将 PIL 图像转换为 OpenCV 格式
    # image1 = cv2.cvtColor(np.array(pil_image1), cv2.COLOR_RGB2BGR)
    # image2 = cv2.cvtColor(np.array(pil_image2), cv2.COLOR_RGB2BGR)
    hist1 = cv2.calcHist([image1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([image2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)


def ssim_s(path, ref_path):
    img1 = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)

    # 调整较小的图像大小以匹配较大的图像
    img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # 计算 SSIM
    score, _ = ssim(img1, img2_resized, full=True)
    return score


def calculate_mse(image1_path, image2_path):
    # 读取两张图片并灰度化
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    # 调整两图大小一致
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)

    # 计算 MSE
    mse = np.mean((img1 - img2) ** 2)
    return mse


whash_list = []
phash_list = []
ahash_list = []
mse_list = []
zft_list = []

for filename in sorted(os.listdir("./umg")):
    file_path = os.path.join("./umg/", filename)
    print(filename)
    phash = similarity_pHash(file_path, "../resources/reference_image/B5_JIS0_ref.jpg")
    phash_list.append(phash)
    whash = similarity_wHash(file_path, "../resources/reference_image/B5_JIS0_ref.jpg")
    whash_list.append(whash)
    ahash = average_hash(file_path, "../resources/reference_image/B5_JIS0_ref.jpg")
    ahash_list.append(ahash)
    mse_list.append(calculate_mse(file_path, "../resources/reference_image/B5_JIS0_ref.jpg"))
    zft_list.append(ssim_s(file_path, "../resources/reference_image/B5_JIS0_ref.jpg"))

print(f'whash:{whash_list}')
print(f'phash:{phash_list}')
print(f'ahash:{ahash_list}')
print(f'mse:{mse_list}')
print(f'phash:{zft_list}')
