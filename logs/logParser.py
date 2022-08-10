# How to run the script: python logParser_ARES.py -logFolder /Volumes/Andria/logs_ARES/reconsimplerandom
import os, json, csv, argparse
from pathlib import Path

class Parser:
    # read the array that includes dictionaries from a log file
    def get_dicts(self, path):
        f = open(path, 'r')
        messages = [json.loads(line) for line in f]
        return messages

    def extract_data(self, messages):
        output = []
        for msg in messages:
            entry = {}
            if 'START' in msg['message']:
                entry['sys_time'] = msg['op_latency_start']
            else:
                entry['sys_time'] = msg['op_latency_end']
                # entry['op_latency'] = msg['op_latency']

            if 'WRITE' in msg['message']:
                entry['client_id'] = 'writer_'+msg['clientID']
            elif 'READ' in msg['message']:
                entry['client_id'] = 'reader_'+msg['clientID']
            else:
                entry['client_id'] = 'recon_'+msg['clientID']
            entry['op_type'] = msg['message']
            entry['op_num'] = msg['opID'].split('-')[2]
            if 'RECONFIG' not in msg['message']:
                entry['object_id'] = msg['objectID']
                if msg['tag']:
                    entry['tag.z'] = tuple(msg['tag'])[0]
                    entry['tag.client_id'] = tuple(msg['tag'])[1]
                else:
                    entry['tag.z'] = None
                    entry['tag.client_id'] = None

            output.append(entry)
        return output

    def convert_csv(self, path, output):
        # convert it to csv file
        keys = output[1].keys()
        with open(path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(output)


    def get_paths(self, folder, logFile):
        listOfFiles = []
        for (dirpath, dirnames, filenames) in os.walk(folder):
            for file in filenames:
                if 'phase1' not in str(file) and all(x in str(file) for x in logFile) and not str(file).startswith('._'):
                    listOfFiles.append(os.path.join(dirpath, file))
        return listOfFiles

args_parser = argparse.ArgumentParser(description='')
args_parser.add_argument('-logFolder', type=str, help='Give the folder that has the logs', required=True)
args = args_parser.parse_args()
logFolder = args.logFolder

parser = Parser()
paths = parser.get_paths(logFolder, ['client-'])
for path in paths:
    messages = parser.get_dicts(path)
    output = parser.extract_data(messages)
    # get only a part of path
    path_splits = path.split('/')[0:8]
    print('path_splits[::-1]:',path_splits[-1])
    if 'daemon' in path_splits[-1] or '.log' in path_splits[-1]:
        path_splits.pop()

    path_splits[3] = path_splits[3] + '_csv'

    path_csv = "/".join(path_splits) + '/' + Path(path).stem + '.csv'
    if not os.path.exists(os.path.dirname(path_csv)):
        os.makedirs(os.path.dirname(path_csv))
    parser.convert_csv(path_csv, output)


