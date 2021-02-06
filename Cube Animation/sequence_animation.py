import os
import cv2


def format_number(num):
    return '%.4d' % num


def move_files(src, dest):
    for i in range(1, 251):
        os.rename(os.path.join(src, f'{format_number(i)}.png'), os.path.join(dest, f'{format_number(i)}.png'))


def create_gif(source):
    import imageio
    filenames = [os.path.join(source, f'{format_number(i)}.png') for i in range(1, 251)]
    images = [imageio.imread(filename) for filename in filenames]
    imageio.mimsave(f'{source}/movie.gif', images, fps=40)


def create_movie(source):
    video_name = 'Cube_animation.avi'
    images = [os.path.join(source, f'{format_number(i)}.png') for i in range(1, 251)]
    frame = cv2.imread(os.path.join(source, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 1, (width, height))
    for image in images:
        video.write(cv2.imread(os.path.join(source, image)))

    cv2.destroyAllWindows()
    video.release()


if __name__ == '__main__':
    source_path = '/Users/raunitdalal/Desktop'
    destination_path = '/Users/raunitdalal/Desktop/Cube Animation Images'
    create_gif(destination_path)

