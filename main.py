import json
import yaml
import argparse
import os
import collections


def read_json(filepath):
    file = open(filepath)
    data = json.load(file)
    return data


def read_yaml(filepath):
    with open(filepath) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        return data


def write_json(data, filepath):
    with open(filepath, "w") as outfile:
        json.dump(data, outfile)


def write_yaml(data, filepath):
    with open(filepath, 'w') as outfile:
        yaml.dump(data, outfile)


def merge_server(main, branch):
    print("Trying to merge servers object")
    for mr_server in branch["servers"]:
        if mr_server in main["servers"]:
            print("Updating entry:" + mr_server)
        else:
            print("Creating entry:" + mr_server)

        main["servers"][mr_server] = branch["servers"][mr_server]

    return main["servers"]


def merge_paths(main, branch):
    for branch_path in branch["paths"]:
        if args.pathextension + branch_path in main["paths"]:
            main["paths"][args.pathextension + branch_path].update(branch["paths"][branch_path])
        else:
            main["paths"][args.pathextension + branch_path] = branch["paths"][branch_path]

    return main["paths"]


def merge_schema(main, branch):
    main["components"]["schemas"].update(branch["components"]["schemas"])
    return main["components"]["schemas"]


def merge_responses(main, branch):
    if "responses" in main["components"]:
        main["components"]["responses"].update(branch["components"]["responses"])
    else:
        main["components"]["responses"] = branch["components"]["responses"]
    return main["components"]["responses"]


def merge_parameters(main, branch):
    if "parameters" in branch["components"]:
        main["components"]["parameters"].update(branch["components"]["parameters"])
    return main["components"]["parameters"]


parser = argparse.ArgumentParser()
parser.add_argument("-b", "--basefile", help="Path of the base file", type=str, required=True)
parser.add_argument("-m", "--mergefile", help="Path of the merging file", type=str, required=True)
parser.add_argument("-o", "--outputfile", help="Path of the output file", type=str, required=False)
parser.add_argument("-p", "--pathextension", default="",
                    help="Extension if basefile needs somthing in front of normal path",
                    type=str, required=False)
parser.add_argument("-server", "--server", action='store_true', help="skips server object")
parser.add_argument("-paths", "--paths", action='store_true', help="skips paths object")
parser.add_argument("-componants", "--componants", action='store_true', help="skips componants object")
parser.add_argument("-override", "--override", action="store_true", help="overrides basefile")

args = parser.parse_args()

output = collections.OrderedDict()

if not os.path.isfile(args.basefile):
    print("NON_VALID_BASEFILE\n")
    print(args.basefile)
    exit(1)
else:
    originFilePath, originExtension = os.path.splitext(args.basefile)
    originFilePath += originExtension

if not os.path.isfile(args.mergefile):
    print("NON_VALID_MERGEFILE\n")
    print(args.mergefile)
    exit(1)
else:
    mergerFilePath, mergerExtension = os.path.splitext(args.mergefile)
    mergerFilePath += mergerExtension

if args.outputfile:
    outputFilePath, outputExtension = os.path.splitext(args.outputfile)
    outputFilePath += outputExtension
elif args.override:
    outputFilePath = originFilePath
else:
    print("NO_OUTPUT_GIVEN\n")
    print("use -o du specify a output file or -override to override the basefile")
    exit(1)

if originExtension == ".json":
    origin = read_json(originFilePath)
elif originExtension == ".yaml":
    origin = read_yaml(originFilePath)
else:
    print("NO_VALID_FILE")
    exit(1)

if mergerExtension == ".json":
    merger = read_json(mergerFilePath)
elif mergerExtension == ".yaml":
    merger = read_yaml(mergerFilePath)
else:
    print("NO_VALID_FILE")
    exit(1)

output["openapi"] = origin["openapi"]
output["info"] = origin["info"]

if not args.server:
    print("Merging server-objects:\n")
    output["servers"] = merge_server(origin, merger)
else:
    print("Skiped server-object merging.\n Just basefile servers")
    output["servers"] = origin["servers"]

if not args.paths:
    print("Merging path-objects:\n")
    output["paths"] = merge_paths(origin, merger)
else:
    print("Skiped paths-object merging.\n Just basefile paths")
    output["paths"] = origin["paths"]

output["components"] = dict()

if not args.componants:
    print("Merging responses-object:\n")
    output["components"]["responses"] = merge_responses(origin, merger)
    print("Merging parameters-object:\n")
    output["components"]["parameters"] = merge_parameters(origin, merger)
    print("Merging schema-objects:\n")
    output["components"]["schemas"] = merge_schema(origin, merger)
else:
    print("skipped responses\n just basefile responses")
    output["components"]["responses"] = origin["components"]["responses"]
    print("skipped parameters\n just basefile parameters")
    output["components"]["parameters"] = origin["components"]["parameters"]
    print("skipped schema\n just basefile schemas")
    output["components"]["schemas"] = origin["components"]["schemas"]

if outputExtension == ".yaml" or originExtension == ".yaml":
    write_yaml(output, outputFilePath)
elif outputExtension == ".json" or originExtension == ".json":
    write_json(output, outputFilePath)
