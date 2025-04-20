import os
import re
from pathlib import Path

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
FOUR_DIGIT_PATTERN = re.compile(r'^\d{4}\.(png|jpg|jpeg|webp|gif)$', re.IGNORECASE)

rename_log = """
"""

def revert(target_folder):
    pattern = re.compile(r"Renaming: <(.*?)> to <(.*?)>")
    revert_map = {}

    for line in rename_log.strip().splitlines():
        match = pattern.match(line.strip())
        if match:
            old_name, new_name = match.groups()
            revert_map[new_name] = old_name

    # 🔄 파일 이름 되돌리기
    folder = Path(target_folder)

    for new_name, old_name in revert_map.items():
        src = folder / new_name
        dst = folder / old_name
        if src.exists():
            print(f"Renaming: <{new_name}> to <{old_name}>")
            src.rename(dst)
        else:
            print(f"❗ File not found: {new_name}")
    print("✅ Revert completed.")


def all_files_are_4digit(images):
    return all(FOUR_DIGIT_PATTERN.match(img.name) for img in images)

def extract_numeric_part(filename: str):
    # 예: "10.png" -> 10
    return int(re.search(r"\d+", filename).group())

def rename_images_in_folder(folder_path):
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"❌ {folder} is not a folder.")
        return

    images = [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
    
    # ✅ 숫자 기준 정렬로 수정
    images.sort(key=lambda f: extract_numeric_part(f.stem))

    if all_files_are_4digit(images):
        print(f"✅ Skipping {folder.name}: already properly named.")
        return

    for i, img in enumerate(images, start=1):
        new_name = f"{i:04d}{img.suffix.lower()}"
        new_path = folder / new_name
        if img.name != new_name:
            print(f"Renaming: <{img.name}> to <{new_name}>")
            img.rename(new_path)

def process_all_subfolders(root_folder):
    root = Path(root_folder)
    if not root.is_dir():
        print(f"❌ Root path is not valid: {root_folder}")
        return

    for subfolder in root.iterdir():
        if subfolder.is_dir():
            print(f"\nProcessing: {subfolder.name}")
            rename_images_in_folder(subfolder)

if __name__ == "__main__":
    isAll = input("상위 폴더는 1, 특정 폴더는 2, 특정 폴더 이름 복구는 3").strip()
    if(isAll == '1'):
        root_input = input("상위 폴더 경로를 입력하세요 (예: ./Pages): ").strip()
        process_all_subfolders(root_input)
    elif(isAll == '2'):
        root_input = input("특정 폴더 경로를 입력하세요 (예: ./Pages): ").strip()
        rename_images_in_folder(root_input)
    elif(isAll == '3'):
        if(rename_log == ""):
            print('nothing in rename_log... Exiting')
        else:
            root_input = input("REVERT 특정 폴더 경로를 입력하세요 (예: ./Pages): ").strip()
            revert(root_input)
    else:
        print('1,2,3 가 아닌 INPUT 입니다.', isAll)
    
