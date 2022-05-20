import argparse
import os
import sys

from usoptimize.convert import convert


def cli():
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