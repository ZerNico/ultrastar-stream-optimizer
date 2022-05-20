import argparse
import codecs
import errno
import os
import re
import runpy
import ffmpeg
import sys
from pathlib import Path
from shutil import copyfile
from qtfaststart2 import processor
from chardet import UniversalDetector
from tqdm import tqdm

detector = UniversalDetector()
txt_pattern = re.compile(r'(#VIDEO.*)(\.avi|\.mp4|\.divx)', re.IGNORECASE)
avi_pattern = re.compile(r'(.*)(\.avi|\.divx|\.flv|\.mkv)', re.IGNORECASE)


def create_dir(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


def convert_to_mp4(in_path, out_path):
    try:
        (
            ffmpeg
                .input(os.path.abspath(in_path))
                .output(os.path.abspath(out_path), vcodec='libx264', movflags='faststart')
                .global_args('-loglevel', 'error', '-n')
                .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print("\nFailed to convert " + str(in_path))
        print('ffmpeg error:', e.stderr.decode('utf8'))


def convert_txt(in_path, out_path):
    detector.reset()
    for line in open(in_path, 'rb'):
        detector.feed(line)
        if detector.done: break
    detector.close()

    encoding = detector.result.get('encoding')

    with codecs.open(in_path, 'r', encoding) as original_file:
        original_content = original_file.read()

    new_content = re.sub(txt_pattern, r'\1.mp4', original_content)

    with codecs.open(out_path, 'w+', "UTF-8") as new_file:
        new_file.write(new_content)


def convert(in_path, out_path, replace):
    abs_in_path = os.path.abspath(in_path)

    in_file_paths = list(Path(abs_in_path).rglob('*.*'))

    for in_file_path in tqdm(in_file_paths):
        # remove abs in path from in file path
        relative_path = str(in_file_path).replace(abs_in_path, '', 1).replace('\\', '/').replace('/', '', 1)
        out_file_path = os.path.abspath(os.path.join(out_path, relative_path))

        if os.path.isdir(in_file_path):
            continue

        if in_file_path.suffix in ['.avi', '.mp4', '.divx', '.flv', '.mkv']:
            out_file_path = re.sub(avi_pattern, r'\1.mp4', out_file_path)

        if os.path.exists(out_file_path):
            if replace:
                os.unlink(out_file_path)
            else:
                continue

        create_dir(out_file_path)

        if in_file_path.suffix in ['.mp4']:
            processor.process(in_file_path, out_file_path, 0, False)
        elif in_file_path.suffix in ['.txt']:
            convert_txt(in_file_path, out_file_path)
        elif in_file_path.suffix in ['.avi', '.divx', '.flv', '.mkv']:
            convert_to_mp4(in_file_path, out_file_path)
        else:
            copyfile(in_file_path, out_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert UltraStar Songs to mp4.')
    parser.add_argument('-i', '--input', metavar='<path of songs>', type=str, nargs=1, required=True,
                        help='Filepath of songs that should be converted')
    parser.add_argument('-o', '--output', metavar='<output path>', type=str, nargs=1, required=True,
                        help='Destination directory of converted songs')
    parser.add_argument('-r', '--replace', action="store_true",
                        help='Whether or not to replace old existing files in output dir')

    args = parser.parse_args()

    input_path = args.input[0]
    output_path = args.output[0]

    if not os.path.isdir(input_path) or not os.path.isdir(output_path):
        print('The path specified does not exist')
        sys.exit()

    convert(input_path, output_path, args.replace)
