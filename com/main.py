import time

import imagehash
from PIL import Image

count = 0
start_time = time.time()
for n in range(0, 10):
    for i in range(0, 10):
        hash1 = imagehash.whash(Image.open('./' + str(i) + '.jpg'))
        hash2 = imagehash.whash(Image.open('./ref.jpg'))
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        print(f"whash：{similarity}")
end_time = time.time()
print(end_time - start_time)
