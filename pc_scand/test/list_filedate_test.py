import os


def load_images():
    image_dir = os.listdir("./umg")

    # 按文件的创建时间排序
    sorted_files = sorted(
        image_dir,
        key=lambda x: os.path.getmtime(os.path.join("./umg", x))
    )

    for filename in sorted_files:
        # 检查文件是否为图片格式（比如jpg或png）
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            # 在这里处理图片文件
            print(f"Processing image: {filename}")


load_images()
