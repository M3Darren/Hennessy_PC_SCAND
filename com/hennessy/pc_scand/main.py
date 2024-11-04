import imagehash
from PIL import Image

hash1 = imagehash.whash(Image.open('./1.jpg'))
hash2 = imagehash.whash(Image.open('./2.jpg'))
# 计算相似度
similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
print(f"whash：{similarity}")
