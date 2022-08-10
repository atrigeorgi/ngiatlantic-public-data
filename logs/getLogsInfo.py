# how to run: python getLogsInfo.py Assertion.<test>
# e.g. python getLogsInfo.py Assertion.test_clientTS

# https://www.datadoghq.com/blog/python-logging-best-practices/
# https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertLogs
# https://pythonicways.wordpress.com/2016/12/20/log-file-parsing-in-python/
import unittest
import os, math, re
import json
import numpy as np
import itertools
from pandas import DataFrame
from stat import *
import ntpath

# vmwABD forks
# logs = ["/Volumes/Andria/logs_new/"]
# logs = ["/Volumes/Andria/logs_new/vmwABD_fast/", "/Volumes/Andria/logs_new/vmwABD_fragmentation_fast"]

# last sirocco experiments
# logs = ['/Volumes/Andria/sirocco_paper_data/sirocco/logs_new/']
# logs = ['/Volumes/Andria/logs_new/awslab11.eisai.gr/home/rpilab/logs_new/scalability_fast_vmwARES_fragmentation_vmwEC_fragmentation_eu/']
# logs = ['/Volumes/Andria/AWS_last/']
# logs = ['/Volumes/Andria/AWS-2021-opodis+usinex/logs_new/awslab8.eisai.gr/home/rpilab/logs_new/']

# filesizeBig_fast_5_vmwARES_fragmentation_vmwEC_fragmentation/
# logs = ['/Volumes/Andria/logs_emulab/logs_new/scalabilityreconserverschanging_fast_vmwARES_fragmentation/']#pickle old orjson    all
# logs = ['/Volumes/Andria/sirocco_paper_data/sirocco/logs_new/vmwABD_fast/', '/Volumes/Andria/sirocco_paper_data/sirocco/logs_new/vmwABD_fragmentation_fast/']
exp_repeats = 3#5
# logs = ['/Volumes/Andria/download-emulab/logs_new/filesizeBig_slow_5_vmwARES_fragmentation_vmwEC_fragmentation/']
# logs = ['/Volumes/Andria/download-emulab/logs_new/filesizeBig_slow_5_ARES_vmwEC/']

logs = ['/Users/andria/Library/Mobile Documents/com~apple~CloudDocs/icloud_Documents/ARESproject2022/logs_new/']

class Assertion(unittest.TestCase):
    # read_type = ''
    # filesizeBig experiment
    # read_type = '_fast'
    read_type = '_slow'


    def get_path(self, folder='', logFile=[], not_patterns=[]):
        # client - 23 - scalability_fast_vmwABD_fragmentation_11 - 25 - 5_1_phase1.log
        # print('path:',folder, logFile, not_patterns)
        listOfFiles = []
        for (dirpath, dirnames, filenames) in os.walk(folder):
            for file in filenames:
                if (self.read_type in dirpath) and 'phase1' not in str(file) and "lastreader" not in str(file) and all(x in str(file) for x in logFile) and all(x not in str(file) for x in not_patterns) and not str(file).startswith('._'):
                    listOfFiles.append(os.path.join(dirpath, file))
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
                if phrase in p['message'] and "BLOCK" not in p['message']:
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
        total_ops = None
        if latency in values:
            avgs = values[latency]

            total_avg = np.mean(avgs)
        return total_avg


    def readlastfile(self, exp_name, exp_type, protocol, out):

        try:
            if exp_name in out and 'last_filesize' not in out[exp_name]:
                path_lastread_ = logs[0]+"readfile/" + exp_type + '_' + protocol + '/readfile_' + exp_name

                # print('path_lastread_: ', path_lastread_)
                path_lastread = self.get_path(path_lastread_, [exp_name + '.txt'])

                # print('path_lastread:', path_lastread)

                path_lastread_stat = path_lastread_+'/file_stat'

                # print('path_lastread_stat:',path_lastread_stat)


                # print('path_lastread_stat:', path_lastread_stat)

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

    # filesize experiment
    # start = True if we want to count the blocks number at the end of the experiment
    # start = False if we want to count the blocks number at the start of the experiment
    def read_blocks_no(self, exp_name, exp_type, protocol, out, start=True):
        if 'fragmentation' in protocol:
            try:
                path = logs[0] + '/' + exp_type + '/' + protocol+self.read_type + '/logs_' + protocol + '_' + exp_name
                if exp_name in out:
                    for (dirpath, dirnames, filenames) in os.walk(path):
                        for file in filenames:

                            if start and 'user-1-' + exp_name + '_phase1.log' in str(file):
                                path = os.path.join(dirpath, file)
                            elif not start and 'user-0-read_file.log' in str(file):
                                path = os.path.join(dirpath, file)

                    # if start:
                    #     path = logs[0] + '/' + exp_type + '/' + protocol + '/logs_' + protocol + '_' + exp_name + '/daemon1/local/experiment/src/log/' + 'user-1-' + exp_name + '_phase1.log'
                    # else:
                    #     path = logs[0] + '/' + exp_type + '/' + protocol + '/logs_' + protocol + '_' + exp_name + '/daemon1/local/experiment/src/log/user-0-read_file.log'

                    # operational latency of read operations
                    info = self.get_specificMessages(path, ['READ'])
                    for i in info:
                        if 'blocks' in i:
                            blocks_len = len(i['blocks'][0])
                        else:
                            blocks_len = i['blocks_no']

                        if start:
                            entry = 'start_blocks_no'
                        else:
                            entry = 'end_blocks_no'
                        out[exp_name][entry] = int(blocks_len)

            except IOError:
                print("failed to get information about %s" % path)

        return out

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def userlatencies(self, protocol, paths, out):

        dictionary = {}

        for path in paths:
            filename = ntpath.basename(path)
            # user-1-maxblocksize_vmwABD_fragmentation_1024_10-10-10_1.log
            exp_name = filename.split('-', 2)[2].split(".")[0]

            if exp_name not in out:
                out[exp_name] = {}
            if exp_name not in dictionary:
                dictionary[exp_name] = {}

            # print('protocol: ', protocol)

            # print('filename::',filename,'\n\n\n\n\n')

            if "filesize" in filename:
                filesize = filename.split('_')[-3]
                # print('filesize', filesize)
                out[exp_name]['filesize'] = math.log(int(filesize),2)

            if "differentk" in filename:
                k = filename.split('_')[-3]
                # print('k=',k)
                out[exp_name]['k'] = int(k)

            if "reconslowratio" in filename:
                reads_count = filename.split('_')[-3]
                out[exp_name]['reads_count'] = int(reads_count)

                writes_count = filename.split('_')[-4]
                out[exp_name]['writes_count'] = int(writes_count)


            if "maxblocksize" in filename:
                maxblocksize = filename.split('_')[-3]
                # print('maxblocksize', maxblocksize)
                out[exp_name]['maxblocksize'] = math.log(int(maxblocksize),2)

            if "minblocksize" in filename or "MaxMinAvgblocksize" in filename:
                minblocksize = filename.split('_')[-3]
                # print('minblocksize', minblocksize)
                out[exp_name]['minblocksize'] = math.log(int(minblocksize),2)

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

            write_operation_latency = {}
            write_operation_latency_withoutFM = {}
            computation_latency = {}
            read_operation_latency = {}
            recon_operation_latency = []


            if 'fragmentation' in protocol:
                daps = ['vmwABD_fragmentation', 'vmwEC_fragmentation']
            elif 'vmw' in protocol:
                daps = ['vmwABD', 'vmwEC']
            else:
                daps = ['ABD', 'EC']

            for dap in daps:
                write_operation_latency[dap] = []
                write_operation_latency_withoutFM[dap] = []
                computation_latency[dap] = []
                read_operation_latency[dap] = []
            write_operation_latency['total'] = []
            read_operation_latency['total'] = []


            reads_no = 0
            recons_no = 0
            writes_no = 0
            succ_writes_no = 0
            unsucc_writes_no = 0
            not_prop_no = 0

            succ_blocks = 0
            unsucc_blocks = 0

            # operational latency of read operations
            info = self.get_specificMessages(path, ['READ'])
            for i in info:
                # print(i)
                reads_no += 1
                # if 'op_latency' in i:
                try:
                    read_operation_latency['total'].append(i['op_latency'])
                except:
                    print('\n\ni::',i)
                    exit(0)
                if 'dap_protocols' in i:
                    if len(i['dap_protocols']) == 2:
                        print('yes 2:: ', exp_name, filename)
                    if 'fragmentation' in protocol:
                        if 'vmwEC_fragmentation' in i['dap_protocols']:
                            read_operation_latency['vmwEC_fragmentation'].append(i['op_latency'])
                        if 'vmwABD_fragmentation' in i['dap_protocols']:
                            read_operation_latency['vmwABD_fragmentation'].append(i['op_latency'])
                    else:
                        for dap in i['dap_protocols']:
                            read_operation_latency[dap].append(i['op_latency'])

                        # if 'vmwEC' in i['dap_protocols']:
                        #     read_operation_latency['vmwEC'].append(i['op_latency'])
                        # if 'vmwABD' in i['dap_protocols']:
                        #     read_operation_latency['vmwABD'].append(i['op_latency'])

                if 'prop' in i: # non-fragmented algorithms
                    if i["prop"] == False:
                        not_prop_no += 1


            # if reads_no:
            #     print('read len:', len(read_operation_latency['total']), len(read_operation_latency['EC']), len(read_operation_latency['ABD']))
            #     print('read_total:', read_operation_latency['total'])
            #     print('read_ec:', read_operation_latency['EC'])
            #     print('read_abd:', read_operation_latency['ABD'])



            info = self.get_specificMessages(path, ['RECON'])
            for i in info:
                recons_no += 1
                recon_operation_latency.append(i['op_latency'])


            if not 'fragmentation' in protocol:
                # operational latency of write operations
                info = self.get_specificMessages(path, ['WRITE'])
                for i in info:
                    writes_no += 1
                    write_operation_latency['total'].append(i['op_latency'])
                    if 'dap_protocols' in i:
                        for dap in i['dap_protocols']:
                            write_operation_latency[dap].append(i['op_latency'])

                        # if 'vmwEC' in i['dap_protocols']:
                        #     write_operation_latency['vmwEC'].append(i['op_latency'])
                        # if 'vmwABD' in i['dap_protocols']:
                        #     write_operation_latency['vmwABD'].append(i['op_latency'])


                    if i["status"]==1 or i["status"] == 'SUCCESS': # we change it to write-complete
                        succ_writes_no += 1
                    elif i["status"] == 0 or i["status"] == 'UNSUCCESS':
                        unsucc_writes_no += 1


            elif 'fragmentation' in protocol:
                # computational latency of write operations
                info = self.get_specificMessages(path, ['WRITE'])
                write_operation_latency['frag_comp_latency'] = []
                write_operation_latency['total_withoutFM'] = []


                for i in info:
                    if 'dap_protocols' in i:
                        if 'vmwEC_fragmentation' in i['dap_protocols']:
                            write_operation_latency['vmwEC_fragmentation'].append(i['op_latency'])
                        if 'vmwABD_fragmentation' in i['dap_protocols']:
                            write_operation_latency['vmwABD_fragmentation'].append(i['op_latency'])

                    write_operation_latency['total'].append(i['op_latency'])
                    writes_no += 1
                    write_operation_latency['frag_comp_latency'].append(i['frag_comp_latency'])
                    write_operation_latency['total_withoutFM'].append(i['op_latency'] - i['frag_comp_latency'])

                    succ_blocks += i['not_prop_count']
                    unsucc_blocks += i['prop_count']

                    if i["status"]==1 or i["status"] == 'SUCCESS': # we change it to write-complete
                        succ_writes_no += 1
                    elif i["status"] == 0 or i["status"] == 'UNSUCCESS':
                        unsucc_writes_no += 1


            # compute the mean and median of each FM
            for dap in daps:
                dictionary = self.compute_mean_median('write_operation_latency_{}'.format(dap), exp_name, write_operation_latency[dap],
                                                      dictionary)
                dictionary = self.compute_mean_median('computation_latency_{}'.format(dap), exp_name, computation_latency[dap], dictionary)
                dictionary = self.compute_mean_median('read_operation_latency_{}'.format(dap), exp_name, read_operation_latency[dap],
                                                      dictionary)

                dictionary = self.compute_mean_median('write_operation_latency_withoutFM_{}'.format(dap), exp_name,
                                                      write_operation_latency_withoutFM[dap], dictionary)
            dictionary = self.compute_mean_median('recon_operation_latency', exp_name,
                                                  recon_operation_latency,
                                                  dictionary)
            dictionary = self.compute_mean_median('read_operation_latency', exp_name, read_operation_latency['total'], dictionary)
            dictionary = self.compute_mean_median('write_operation_latency', exp_name, write_operation_latency['total'], dictionary)

            if 'reads_no' not in dictionary[exp_name]:
                dictionary[exp_name]['reads_no'] = []
                dictionary[exp_name]['recons_no'] = []
                dictionary[exp_name]['writes_no'] = []
                dictionary[exp_name]['succ_writes_no'] = []
                dictionary[exp_name]['unsucc_writes_no'] = []
                dictionary[exp_name]['fast_ops_no'] = []

                if 'vmwABD_fragmentation' in protocol:
                    dictionary[exp_name]['succ_blocks'] = []
                    dictionary[exp_name]['unsucc_blocks'] = []


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

            dictionary[exp_name]['fast_ops_no'].append(not_prop_no)

            if 'vmwABD_fragmentation' in protocol:
                if succ_blocks:
                    dictionary[exp_name]['succ_blocks'].append(succ_blocks)
                if unsucc_writes_no:
                    dictionary[exp_name]['unsucc_blocks'].append(unsucc_blocks)

        if 'vmwABD_fragmentation' in protocol:
            features = ['reads_no', 'writes_no', 'recons_no', 'succ_writes_no', 'unsucc_writes_no', 'succ_blocks', 'unsucc_blocks']
        else:
            features = ['reads_no', 'writes_no', 'recons_no', 'succ_writes_no', 'unsucc_writes_no', 'fast_ops_no']
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
            for dap in daps:
                for latency in ['mean_write_operation_latency_'+dap, 'mean_read_operation_latency_'+dap]:

                    if latency in dictionary[k] and not (
                            not 'fragmentation' in protocol and latency == 'mean_write_operation_latency_withoutFM'):
                        avg = self.compute_mean(latency, dictionary[k])  # , dictionary[k][operations_no_label])
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
        # values = {'readers_s10w10':['scalability', ['_10-10']], 'writers_s10r10':['scalability', ['_10','10_']], 'servers_w10r10':['scalability', ['_','10-10_']], 'filesizeReadUnsucc_s10w10r10':['filesizeReadUnsucc', ['_']], 'maxblocksize_s10w10r10': ['maxblocksize', ['']], 'filesize_s10w10r10':['filesize', ['_']]}

        # {'filesizeReadUnsucc_s10w10r10':['filesizeReadUnsucc', ['_']]}
        # values = {'filesize_s10w10r10':['filesize', ['_']]}
        # values = {'maxblocksize_s10w10r10': ['maxblocksize', ['']]}

        # values = {'minblocksize_s10w10r10': ['minblocksize', ['']]}

        # SIROCCO PAPER
        # values = {'filesizeBig_s5w5r5':['filesizeBig', ['_']]}
        # values = {'minblocksizefast_s10w10r10': ['minblocksizefast', ['']]} # physical nodes (not VM)
        # values = {'readersfast_s10w10':['scalabilityfast', ['_10-10']], 'writersfast_s10r10':['scalabilityfast', ['_10','10_']], 'serversfast_w10r10':['scalabilityfast', ['_','10-10_']]}


        # values = {'filesizeBigFragmented_s5w10r40':['filesizeBigFragmented', ['_']]}


        # values = {'readers_s10w1': ['readers', ['_10-1']]}

        # values = {'readers_s10w10': ['scalabilityslow', ['_10-10']], 'writers_s10r10': ['scalabilityslow', ['_10','10_']]}

        # values = {'readers_s10w10':['reconslow_old', ['_10-10']], 'writers_s10r10':['reconslow_old', ['_10','10_']]}

        # test vmwABD
        # values = {'filesizeBig_s1w1r1':['filesizeBigslow', ['_']]}

        # values = {'scalability_fast': ['scalability_fast', ['']]}
        # values = {'scalability_slow': ['scalability_slow', ['']]}

        # values = {'filesizeBig_fast':['filesizeBig_fast', ['_']]}
        # values = {'filesizeBig_slow':['filesizeBig_slow', ['_']]}
        # values = {'MaxMinAvgblocksize_fast':['MaxMinAvgblocksize_fast', ['_']]}
        # values = {'minblocksize_fast':['minblocksize_fast', ['_']]}


        # values = {'scalabilityreconserverschanging_fast':['scalabilityreconserverschanging_fast', ['_']]}
        # values = {'scalabilityreconchanging_fast':['scalabilityreconchanging_fast', ['_']]}
        # values = {'scalabilityreconfixed_fast':['scalabilityreconfixed_fast', ['_']]}
        # values = {'scalabilityreconrandom_fast':['scalabilityreconrandom_fast', ['_']]}


        # ARES ABD / EC
        # values = {'scalabilityreconfixed_slow':['scalabilityreconfixed_slow', ['_']]}

        # values = {'throughputsEU3US0wEU1US0rEU1US0':['throughputsEU3US0wEU1US0rEU1US0_slow', ['_']]}

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

        # graph_types = ['filesizeBig']

        graph_types = ['scalabilityreconfixed']

        for val in graph_types:

            values = {val: [val+'_slow', ['_']]}

            for l in logs:
                # for protocol in ['vmwABD', 'ARES_vmwABD', 'ARES_vmwEC', 'vmwABD_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation', 'vmwARES_fragmentation_vmwEC_fragmentation']:

                # for protocol in ['ARES_vmwABD', 'ARES_vmwEC','vmwARES_fragmentation_vmwABD_fragmentation','vmwARES_fragmentation_vmwEC_fragmentation']:
                # for protocol in ['ARES_vmwEC']:
                # for protocol in ['vmwARES_fragmentation_vmwEC_fragmentation']:

                # for protocol in ['vmwARES_fragmentation','ARES']:

                # for protocol in ['vmwABD', 'ARES_vmwABD', 'vmwABD_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation']:

                # for protocol in ['vmwABD', 'ARES_vmwABD', 'vmwABD_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation']:

                # for protocol in ['vmwABD_fragmentation', 'vmwARES_fragmentation_vmwEC_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation']:

                for protocol in ['ARES_EC']:#'ARES_ABD', 'ARES_EC', 'ABD']:  # , 'Cassandra']:

                    # logs_vmwABD_scalability_vmwABD_10-5-10_1
                    not_patterns = []
                    if 'fragmentation' in protocol:
                        not_patterns = []
                    else:
                        not_patterns.append('fragmentation')

                    for graph_type, k in values.items():

                        path = '{}/experiments_info_{}/{}.csv'.format(protocol, protocol, graph_type)
                        if not os.path.exists(path):

                            paths_users = []

                            out = {}
                            res = {}

                            type_of_exp = k[0]

                            # l + type of exp + protocol
                            # user-1-filesize_vmwABD_fragmentation_1024_10-10-10_1.log
                            log = l  # +type_of_exp+'/'+protocol+self.read_type

                            patterns = []
                            # pattern = type of exp + protocol + specific matching
                            patterns.append(type_of_exp + '_' + protocol + k[1][0])
                            if len(k[1]) > 1:
                                for i in range(1, len(k[1])):
                                    patterns.append(k[1][i])

                            # patterns.append('1.log') # only the 1st round
                            # not_patterns.append('40')
                            # not_patterns.append('50')

                            # patterns.append('_11-')
                            p = self.get_path(log, ['client-'] + patterns, not_patterns)
                            # print('paths:',p)
                            paths_users.extend(p)

                            out = self.userlatencies(protocol, paths_users, out)

                            # after each experiment the last client read the modified file
                            for exp in out:
                                out = self.readlastfile(exp, type_of_exp, protocol, out)

                            # read the number of blocks in case of fragmentation protocol
                            # if 'fragmentation' in protocol:
                            #     for exp in out:
                            #         out = self.read_blocks_no(exp, type_of_exp, protocol, out, True)
                            #         out = self.read_blocks_no(exp, type_of_exp, protocol, out, False)

                            out_keys = sorted(list(out.keys()))

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
                                    if items[0][0] == 'mean_read_operation_latency' or items[0][0] == 'mean_write_operation_latency':
                                        d[items[0][0].replace('mean', 'median')] = np.median([x[1] for x in items])
                                        d[items[0][0].replace('mean', 'std')] = np.std([x[1] for x in items])
                                        d[items[0][0].replace('mean', 'max')] = np.max([x[1] for x in items])
                                        d[items[0][0].replace('mean', 'min')] = np.min([x[1] for x in items])

                                exp_name = ''.join(exp_list)
                                # exp_name = exp_list[0].rsplit("_", 1)[0]
                                res[exp_name] = d


                            if res:

                                for exp_name in res:
                                    whole = res[exp_name]['succ_writes_no'] + res[exp_name]['unsucc_writes_no']
                                    if whole:
                                        res[exp_name]['succ_writes_perc'] = self.percentage(
                                            res[exp_name]['succ_writes_no'],
                                            whole)
                                        res[exp_name]['unsucc_writes_perc'] = self.percentage(
                                            res[exp_name]['unsucc_writes_no'],
                                            whole)
                                if protocol == 'vmwABD_fragmentation':
                                    for exp_name in res:
                                        whole = res[exp_name]['succ_blocks'] + res[exp_name]['unsucc_blocks']
                                        if whole:
                                            res[exp_name]['succ_writes_perc_block'] = self.percentage(
                                                res[exp_name]['succ_blocks'],
                                                whole)
                                            res[exp_name]['unsucc_writes_perc_block'] = self.percentage(
                                                res[exp_name]['unsucc_blocks'], whole)

                                # save info about the experiment
                                df = DataFrame(res)
                                if not os.path.exists(os.path.dirname(path)):
                                    os.makedirs(os.path.dirname(path))
                                df.to_csv(path)

                                for exp_list in experiments:
                                    folder_name = exp_list[0].rsplit("_", 1)[0]

                                    for exp_name in exp_list:
                                        path = '{}/individual_experiments_info_{}/{}/{}/{}.csv'.format(protocol,
                                                                                                       protocol,
                                                                                                       graph_type + "_" + protocol,
                                                                                                       folder_name,
                                                                                                       exp_name)
                                        if not os.path.exists(os.path.dirname(path)):
                                            os.makedirs(os.path.dirname(path))

                                        df = DataFrame(out[exp_name], index=[0])
                                        df.to_csv(path)
                            else:
                                print('Not found!', path)


if __name__ == '__main__':
    unittest.main()

