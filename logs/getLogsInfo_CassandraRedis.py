import unittest
import os, math, re
import json
import numpy as np
import itertools
from pandas import DataFrame
from stat import *
import ntpath

exp_repeats = 3#5
# logs = ['/Users/andria/Library/Mobile Documents/com~apple~CloudDocs/icloud_Documents/ARESproject2022/Cassandra/logsEmulab/']
# logs = ['/Volumes/Andria/experiments/jfed/logs_new']
logs = ['/Users/andria/Library/Mobile Documents/com~apple~CloudDocs/icloud_Documents/ARESproject2022/logs_new/']

# How to find a file from terminal
#'/Users/andria/Library/Mobile\ Documents/com~apple~CloudDocs/icloud_Documents/ARESproject2022/Cassandra/logsEmulab/logs/filesizeCassandra/logs_filesizeCassandra_1048576_10-5-5_1/user-1-filesizeCassandra_1048576_10-5-5_1_phase1.log'


class Assertion(unittest.TestCase):

    def get_path(self, folder='', logFile=[], not_patterns=[]):
        # client - 23 - scalability_fast_vmwABD_fragmentation_11 - 25 - 5_1_phase1.log
        listOfFiles = []
        print('folder:',folder, logFile)

        for (dirpath, dirnames, filenames) in os.walk(folder):
            for file in filenames:
                if 'phase1' not in str(file) and "lastreader" not in str(file) and all(x in str(file) for x in logFile) and all(x not in str(file) for x in not_patterns) and not str(file).startswith('._'):
                    listOfFiles.append(os.path.join(dirpath, file))
        print('listOfFiles:', listOfFiles, '\n\n')
        return listOfFiles

    def get_dict(self, path, features):
        f = open(path, 'r')
        data = [json.loads(line) for line in f]
        output = []
        for p in data:
            if all(feature in p for feature in features):
                output.append(p)
        f.close()
        return output

    def get_specificMessages(self, path, phrases):
        f = open(path, 'r')
        data = [json.loads(line) for line in f]
        f.close()
        output = {}
        for i, phrase in enumerate(phrases):
            output[i] = []
        for p in data:
            i = 0
            for phrase in phrases:
                if phrase in p['message']:
                    output[i].append(p)
                i += 1
        return output[0]

    def compute_mean_median(self, latency_type, exp_name, values, dictionary):
        if values:
            median = np.median(values)
            mean = np.mean(values)

            if 'median_{}'.format(latency_type) not in dictionary[exp_name]:
                dictionary[exp_name]['median_{}'.format(latency_type)] = []
            if 'mean_{}'.format(latency_type) not in dictionary[exp_name]:
                dictionary[exp_name]['mean_{}'.format(latency_type)] = []

            dictionary[exp_name]['median_{}'.format(latency_type)].append(median)
            dictionary[exp_name]['mean_{}'.format(latency_type)].append(mean)
        return dictionary


    def compute_mean(self, latency, values):
        total_avg = None
        if latency in values:
            avgs = values[latency]

            total_avg = np.mean(avgs)
        return total_avg


    def readlastfile(self, exp_name, exp_type, out):

        try:
            if exp_name in out and 'last_filesize' not in out[exp_name]:
                path_lastread_ = logs[0]+"readfile/" + exp_type + '/readfile_' + exp_name

                path_lastread = self.get_path(path_lastread_, [exp_name + '.txt'])

                path_lastread_stat = path_lastread_+'/file_stat'

                if len(path_lastread)>0:
                    path_lastread = path_lastread[0]
                    path_lastread = path_lastread
                    if path_lastread:
                        path_lastread = path_lastread
                    else:
                        return out
                    st = os.stat(path_lastread)
                    file_size = str(st[ST_SIZE])
                    out[exp_name]['last_filesize'] = int(file_size)
                    print('file_size: ', file_size)

                # I change the method of getting the size of the file
                # So I have second way in whic ansisble uses stat
                elif os.path.isfile(path_lastread_stat):
                    with open(path_lastread_stat, 'rb') as f:
                        dict_stat = json.load(f)
                    file_size = dict_stat['results'][0]['stat']['size']
                    out[exp_name]['last_filesize'] = int(file_size)
                    print('file_size: ', file_size)

        except IOError:
            print("failed to get information about %s" % path_lastread)

        return out



    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def userlatencies(self, algorithm, paths, out):

        dictionary = {}

        for path in paths:
            filename = ntpath.basename(path)
            exp_name = filename.split('-', 2)[2].split(".")[0]

            if exp_name not in out:
                out[exp_name] = {}
            if exp_name not in dictionary:
                dictionary[exp_name] = {}

            if "filesize" in filename:
                filesize = filename.split('_')[-3]
                # print('filesize', filesize)
                out[exp_name]['filesize'] = math.log(int(filesize),2)

            if 'readers_no' not in out[exp_name]:
                participants = exp_name.rsplit("_", 2)[1].split("-")
                if len(participants)==4:
                    servers, writers, readers, recons = participants
                else:
                    servers, writers, readers = participants
                    recons = 0
                # print(servers, writers, readers)

                out[exp_name]['servers_no'] = int(servers)

                out[exp_name]['readers_no'] = int(readers)

                out[exp_name]['writers_no'] = int(writers)

            # get the continent of servers, writers, readers
            if 'throughput' in exp_name:
                for count in ['sEU', 'wEU', 'rEU']:
                    match = re.search(count + '(\d+)' + 'US' + '(\d+)', exp_name).group(0)
                    match = re.split('EU|US', match)
                    EU, US = match[1], match[2]
                    out[exp_name][count] = int(EU)
                    out[exp_name][count.replace('EU', 'US')] = int(US)

            write_operation_latency = []
            write_operation_latency_withoutFM = []
            computation_latency = []
            read_operation_latency = []


            reads_no = 0
            recons_no = 0
            writes_no = 0
            succ_writes_no = 0
            unsucc_writes_no = 0
            succ_reads_no = 0
            unsucc_reads_no = 0


            # operational latency of read operations
            info = self.get_specificMessages(path, ['READ'])
            for i in info:
                print(i)
                reads_no += 1
                # if 'op_latency' in i:
                read_operation_latency.append(i['op_latency'])

                if i["status"]==1 or i["status"] == 'SUCCESS':
                    succ_reads_no += 1
                elif i["status"] == 0 or i["status"] == 'UNSUCCESS':
                    unsucc_reads_no += 1


            # operational latency of write operations
            info = self.get_specificMessages(path, ['WRITE'])
            for i in info:
                writes_no += 1
                write_operation_latency.append(i['op_latency'])

                if i["status"]==1 or i["status"] == 'SUCCESS':
                    succ_writes_no += 1
                elif i["status"] == 0 or i["status"] == 'UNSUCCESS':
                    unsucc_writes_no += 1


            # compute the mean and median
            dictionary = self.compute_mean_median('write_operation_latency', exp_name, write_operation_latency, dictionary)
            dictionary = self.compute_mean_median('computation_latency', exp_name, computation_latency, dictionary)
            dictionary = self.compute_mean_median('read_operation_latency', exp_name, read_operation_latency,dictionary)

            dictionary = self.compute_mean_median('write_operation_latency_withoutFM', exp_name, write_operation_latency_withoutFM, dictionary)

            dictionary = self.compute_mean_median('read_operation_latency', exp_name, read_operation_latency, dictionary)
            dictionary = self.compute_mean_median('write_operation_latency', exp_name, write_operation_latency, dictionary)

            if 'reads_no' not in dictionary[exp_name]:
                dictionary[exp_name]['reads_no'] = []
                dictionary[exp_name]['recons_no'] = []
                dictionary[exp_name]['writes_no'] = []
                dictionary[exp_name]['succ_writes_no'] = []
                dictionary[exp_name]['unsucc_writes_no'] = []


            if reads_no:
                dictionary[exp_name]['reads_no'].append(reads_no)

            if writes_no:
                dictionary[exp_name]['writes_no'].append(writes_no)

            if recons_no:
                dictionary[exp_name]['recons_no'].append(recons_no)

            if succ_writes_no:
                dictionary[exp_name]['succ_writes_no'].append(succ_writes_no)
            if unsucc_writes_no:
                dictionary[exp_name]['unsucc_writes_no'].append(unsucc_writes_no)



        features = ['reads_no', 'writes_no', 'recons_no', 'succ_writes_no', 'unsucc_writes_no']
        # in each experiment (keys = exp name)
        for k in dictionary.keys():
            for feature in features:
                values = dictionary[k][feature]
                if values:
                    total_ops = sum(values)
                    out[k][feature] = total_ops
                else:
                    out[k][feature] = 0


        # print('keys:', dictionary.keys())
        # for each experimeny
        for k in dictionary.keys():
            for latency in ['mean_write_operation_latency', 'mean_read_operation_latency']:
                if latency in dictionary[k]:
                    avg = self.compute_mean(latency, dictionary[k])
                    out[k][latency] = avg
            for latency in ['mean_write_operation_latency', 'mean_read_operation_latency']:
                if latency in dictionary[k]:
                    avg = self.compute_mean(latency, dictionary[k])
                    out[k][latency] = avg

            for latency in ['mean_recon_operation_latency']:
                if latency in dictionary[k]:
                    avg = dictionary[k][latency][0]
                    out[k][latency] = avg

        return out


    def percentage(self, percent, whole):
        return (percent / whole) * 100.0

    def test_latency(self):

        # values = {'filesizeCassandra':['filesizeCassandra', ['_']]}
        # values = {'scalabilityCassandra':['scalabilityCassandra', ['_']]}
        # algorithm = 'Cassandra'

        # values = {'scalabilityRedis': ['scalabilityRedis', ['_']]}
        # algorithm = 'Redis'

        # values = {'scalabilityRedisClustermode': ['scalabilityRedisClustermode', ['_']]}
        # algorithm = 'RedisClustermode'

        # values = {'throughputsEU3US0wEU1US0rEU1US0':['throughputRedissEU3US0wEU1US0rEU1US0', ['_']]}
        # algorithm = 'Redis'
        #
        # values = {'throughputsEU3US0wEU1US0rEU1US0': ['throughputCassandrasEU3US0wEU1US0rEU1US0', ['_']]}
        # algorithm = 'Cassandra'

        # values = {'throughputsEU3US0wEU1US0rEU1US0':['throughputRedisWsEU3US0wEU1US0rEU1US0', ['_']]}
        # algorithm = 'RedisW'

        # graph_types = ['throughputsEU3US0wEU1US0rEU1US0', 'throughputsEU3US0wEU1US0rEU0US0',
        #                'throughputsEU3US0wEU0US0rEU1US0',
        #                'throughputsEU0US3wEU0US1rEU0US1', 'throughputsEU0US3wEU0US1rEU0US0',
        #                'throughputsEU0US3wEU0US0rEU0US1',
        #                'throughputsEU3US0wEU0US1rEU0US1', 'throughputsEU3US0wEU0US1rEU0US0',
        #                'throughputsEU3US0wEU0US0rEU0US1',
        #                'throughputsEU0US3wEU1US0rEU1US0', 'throughputsEU0US3wEU1US0rEU0US0',
        #                'throughputsEU0US3wEU0US0rEU1US0',
        #                'throughputsEU1US2wEU1US0rEU1US0', 'throughputsEU1US2wEU1US0rEU0US0',
        #                'throughputsEU1US2wEU0US0rEU1US0',
        #                'throughputsEU2US1wEU0US1rEU0US1', 'throughputsEU2US1wEU0US1rEU0US0',
        #                'throughputsEU2US1wEU0US0rEU0US1']

        graph_types = ['filesize']

        for t, algorithm in itertools.product(graph_types, ['Cassandra']):#, 'Redis', 'RedisW'
            # values = {t: [t, ['_']]}
            values = {t: [t, ['']]}


            for l in logs:

                for graph_type, k in values.items():

                    path = '{}/experiments_info_{}/{}.csv'.format(algorithm, algorithm, graph_type)

                    if not os.path.exists(path):
                        paths_users = []

                        out = {}
                        res = {}

                        type_of_exp = k[0]

                        log = l

                        patterns = []
                        # pattern = type of exp + specific matching
                        patterns.append(type_of_exp + k[1][0])
                        if len(k[1]) > 1:
                            for i in range(1, len(k[1])):
                                patterns.append(k[1][i])

                        # patterns.append('1.log') # only the 1st round
                        not_patterns = []
                        # not_patterns.append('40')
                        # not_patterns.append('50')
                        # patterns.append('_11-')
                        p = self.get_path(log, ['user-', algorithm] + patterns, not_patterns)
                        print('paths:', p)
                        paths_users.extend(p)

                        out = self.userlatencies(algorithm, paths_users, out)

                        # after each experiment the last client read the modified file
                        for exp in out:
                            out = self.readlastfile(exp, type_of_exp, out)

                        out_keys = list(out.keys())

                        out_keys = sorted(out_keys)


                        print('exp_repeats:', exp_repeats)

                        experiments = [out_keys[i:i + exp_repeats] for i in range(0, len(out_keys), exp_repeats)]

                        # get the mean of values
                        for exp_list in experiments:
                            sub_out = {k: v for k, v in out.items() if k in exp_list}

                            # print('sub_out: ', sub_out)
                            # print('\n\n\n', sub_out)
                            d = {}
                            for k, items in itertools.groupby(
                                    sorted(itertools.chain(*[x.items() for x in sub_out.values()])),
                                    lambda x: x[0]):
                                items = list(items)
                                # print('items:',items,'\n\n\n\n')
                                if items[0][1] != None:
                                    d[k] = sum(x[1] for x in items) / len(items)
                                # print('item:',items[0][0])
                                if items[0][0] == 'mean_read_operation_latency' or items[0][
                                    0] == 'mean_write_operation_latency':
                                    d[items[0][0].replace('mean', 'median')] = np.median([x[1] for x in items])
                                    d[items[0][0].replace('mean', 'std')] = np.std([x[1] for x in items])
                                    d[items[0][0].replace('mean', 'max')] = np.max([x[1] for x in items])
                                    d[items[0][0].replace('mean', 'min')] = np.min([x[1] for x in items])

                            exp_name = ''.join(exp_list)
                            # exp_name = exp_list[0].rsplit("_", 1)[0]
                            res[exp_name] = d

                        for exp_name in res:
                            whole = res[exp_name]['succ_writes_no'] + res[exp_name]['unsucc_writes_no']
                            if whole:
                                res[exp_name]['succ_writes_perc'] = self.percentage(res[exp_name]['succ_writes_no'],
                                                                                    whole)
                                res[exp_name]['unsucc_writes_perc'] = self.percentage(res[exp_name]['unsucc_writes_no'],
                                                                                      whole)

                        # save info about the experiment
                        df = DataFrame(res)
                        if not os.path.exists(os.path.dirname(path)):
                            os.makedirs(os.path.dirname(path))
                        df.to_csv(path)

                        for exp_list in experiments:
                            folder_name = exp_list[0].rsplit("_", 1)[0]

                            for exp_name in exp_list:
                                path = '{}/individual_experiments_info_{}/{}/{}/{}.csv'.format(algorithm, algorithm,
                                                                                               graph_type + "_" + algorithm,
                                                                                               folder_name, exp_name)
                                if not os.path.exists(os.path.dirname(path)):
                                    os.makedirs(os.path.dirname(path))

                                df = DataFrame(out[exp_name], index=[0])
                                df.to_csv(path)


if __name__ == '__main__':
    unittest.main()

