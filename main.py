import argparse
import yaml
from loader.base_json_loader import BaseJsonLoaderV1
from writer.delimiter_separated_values import dsv_writer


def call_std2dsv(args: argparse.Namespace):
    # Load standard JSON
    loader = BaseJsonLoaderV1(filepath=args.input)

    # Load default configs
    with open(file='configs/config_dsv_default.yaml', mode='r') as file:
        default_config = yaml.load(file, Loader=yaml.FullLoader)

    # Look for user-specific config YAML file
    if args.config is None:
        yaml_file = 'configs/config_dsv_default.yaml'
    elif args.config == 'yolo':
        yaml_file = 'configs/config_dsv_yolo.yaml'
    else:
        yaml_file = args.config

    # Load YAML file
    with open(file=yaml_file, mode='r') as file:
        config_params = yaml.load(file, Loader=yaml.SafeLoader)

    # Merge default config with user config
    config_params = {**default_config, **config_params}

    # Output is a folder if 'filePerImage' is True, otherwise it is a file
    if config_params['filePerImage']:
        config_params['outputFolder'] = args.output
    else:
        config_params['outputFile'] = args.output

    # Write DSV file(s)
    dsv_writer(images=loader.images, path='', **config_params)


if __name__ == '__main__':
    # main parser
    parser = argparse.ArgumentParser(description='Computer Vision Data Format Converter')

    # different converters
    converters = parser.add_subparsers(dest='converters', help='list of available converters')

    # std2dsv converter parameters
    std2dsv = converters.add_parser('std2dsv', help='Converting standard JSON to a specific DSV format')
    std2dsv.add_argument('input', type=str, metavar='INPUT-PATH',
                         help='path to input file with standard JSON format')
    std2dsv.add_argument('output', type=str, metavar='OUTPUT-PATH',
                         help='file or folder depending on \'filePerImage\' parameter')
    std2dsv.add_argument('--config', type=str, metavar='{CONFIG-PATH, yolo}',
                         help='path to config file or a pre-defined config')
    # TODO: optional arguments for config parameters

    merge = converters.add_parser('merge', help='Merges a list of standard JSONs into one JSON')
    merge.add_argument('list', type=str, metavar='FILE-PATH', help='path to file with standard JSON paths')
    merge.add_argument('output', type=str, metavar='OUTPUT-PATH', help='path of merged file')

    # parse arguments
    args = parser.parse_args()

    # Look which converter should be called
    if args.converters == 'std2dsv':
        call_std2dsv(args)

    # TODO: just use argparse? each schript its own argparser to call
