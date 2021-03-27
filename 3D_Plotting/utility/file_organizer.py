import os
import string
import random

allowed_chars = "".join([string.digits, ' _'])


def parse_filename(f):
    num = ''
    for c in f:
        if c in string.digits:
            num += c
    return int(num) if num else 0


def present(words, filename):
    for w in words:
        if not w:
            continue
        if w in filename:
            return True
    return False


def fix_files(file_arr, src_dir, dest_dir, num):
    keywords = ['img', 'verts', 'object', 'j3d']
    not_keywords = [['out', 'occ'], [''], [''], ['17']]
    extension = ['png', 'npy', 'obj', 'npy']
    for file in file_arr:
        for i, k in enumerate(keywords):
            if k in file and not present(not_keywords[i], file):
                # print(file)
                path = os.path.join(dest_dir, f'{k}_{num:06d}.{extension[i]}')
                os.rename(os.path.join(src_dir, file), path)
                # print(path)
                # print()
                break


def walk():
    root_dir = '/Users/raunitdalal/Desktop/Blender Scripts/3D_Plotting/folders'
    for _, d, filenames in os.walk(root_dir):
        if not d:
            num = 0
            idx = 0
            while not num and idx < len(filenames):
                num = parse_filename(filenames[idx])
                idx += 1
            dest_path = os.path.join(root_dir, f'{num:06d}')
            if os.path.exists(dest_path):
                dest_path += f'_{random.randint(0, 1000)}'
            os.mkdir(dest_path)
            src_path = os.path.join(_)
            fix_files(filenames, src_path, dest_path, num)


walk()
