import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

algorithms = ['ABD', 'ARES_ABD', 'ARES_EC', 'CASSANDRA', 'REDIS', 'REDISW']

def plotBarChart(graph_type, mean_write_operation_latencies=[], mean_read_operation_latencies=[], title=''):
    print(title)
    # set width of bar
    barWidth = 0.25
    fig = plt.subplots(figsize=(12, 8))

    # Set position of bar on X axis
    br1 = np.arange(len(mean_write_operation_latencies))
    br2 = [x + barWidth for x in br1]

    # Make the plot
    if mean_write_operation_latencies:
        plt.bar(br1, mean_write_operation_latencies, color='r', width=barWidth,
            edgecolor='grey', label='write')

    if mean_read_operation_latencies:
        if not br2:
            br2 = np.arange(len(mean_read_operation_latencies))
        plt.bar(br2, mean_read_operation_latencies, color='g', width=barWidth,
            edgecolor='grey', label='read')

    plt.title(title)

    # Adding Xticks
    plt.xlabel('Algorithm', fontweight='bold', fontsize=15)
    plt.ylabel('Avg Operation Latency', fontweight='bold', fontsize=15)
    if mean_write_operation_latencies:
        print('\n\nlen samples',len(mean_write_operation_latencies), '\n\n', len(algorithms))

    if mean_read_operation_latencies and mean_write_operation_latencies:
        plt.xticks([r + barWidth for r in range(len(mean_write_operation_latencies))], algorithms)
    else:
        length = max([len(mean_read_operation_latencies), len(mean_write_operation_latencies)])
        plt.xticks([r for r in range(length)], algorithms)

    plt.ylim([0, 0.7])
    plt.legend()
    # plt.show()
    plt.savefig('throughput_graphs/'+graph_type+'.png')

# 3 - Server in EU vs Client EU
# throughputsEU3US0wEU1US0rEU1US0
# throughputsEU3US0wEU1US0rEU0US0
# throughputsEU3US0wEU0US0rEU1US0

# 3 - Server in US vs Client US
# throughputsEU0US3wEU0US1rEU0US1
# throughputsEU0US3wEU0US1rEU0US0
# throughputsEU0US3wEU0US1rEU1US0


# 3 - Server in EU vs Client US
# throughputsEU3US0wEU0US1rEU0US1
# throughputsEU3US0wEU0US1rEU0US0
# throughputsEU3US0wEU0US0rEU0US1


# 3 - Server in US vs Client EU
# throughputsEU0US3wEU1US0rEU1US0
# throughputsEU0US3wEU1US0rEU0US0
# throughputsEU0US3wEU0US0rEU1US0

# 3 - 2 Server in US & 1 in EU - Clients in US (minority)
# throughputsEU1US2wEU1US0rEU1US0
# throughputsEU1US2wEU1US0rEU0US0
# throughputsEU1US2wEU0US0rEU1US0

# 3 - 2 Server in EU & 1 in US - Clients in US (minority)
# throughputsEU2US1wEU0US1rEU0US1
# throughputsEU2US1wEU0US1rEU0US0
# throughputsEU2US1wEU0US0rEU0US1

isExist = os.path.exists('throughput_graphs')
if not isExist:
    os.makedirs('throughput_graphs')

graph_types = ['throughputsEU3US0wEU1US0rEU1US0', 'throughputsEU3US0wEU1US0rEU0US0', 'throughputsEU3US0wEU0US0rEU1US0',
            'throughputsEU0US3wEU0US1rEU0US1', 'throughputsEU0US3wEU0US1rEU0US0', 'throughputsEU0US3wEU0US0rEU0US1',
               'throughputsEU3US0wEU0US1rEU0US1', 'throughputsEU3US0wEU0US1rEU0US0', 'throughputsEU3US0wEU0US0rEU0US1',
               'throughputsEU0US3wEU1US0rEU1US0', 'throughputsEU0US3wEU1US0rEU0US0', 'throughputsEU0US3wEU0US0rEU1US0',
               'throughputsEU1US2wEU1US0rEU1US0', 'throughputsEU1US2wEU1US0rEU0US0', 'throughputsEU1US2wEU0US0rEU1US0',
               'throughputsEU2US1wEU0US1rEU0US1', 'throughputsEU2US1wEU0US1rEU0US0', 'throughputsEU2US1wEU0US0rEU0US1']


for graph_type in graph_types:

    if not os.path.exists('throughput_graphs/'+graph_type+'.png'):

        # graph_type = 'throughputsEU3US0wEU1US0rEU1US0'
        mean_write_operation_latencies = []
        mean_read_operation_latencies = []

        for alg in algorithms:
            path = '{}/experiments_info_{}/{}.csv'.format(alg, alg, graph_type)  # +extra

            if os.path.exists(path):
                print('path:',path)
                with open(path, 'r') as f:
                    # 1st solution
                    res = pd.read_csv(path, index_col=0)
                    res = np.round(res, decimals=9)  # 9 dp, because some integers are set with strange dp
                    res = res.to_dict()
                    key = list(res.keys())[0]  # the dict has only one key


                    sEU = res[key]['sEU']
                    wEU = res[key]['wEU']
                    rEU = res[key]['rEU']

                    sUS = res[key]['sUS']
                    wUS = res[key]['wUS']
                    rUS = res[key]['rUS']

                    servers_no = res[key]['servers_no']
                    writers_no = res[key]['writers_no']
                    readers_no = res[key]['readers_no']

                    if readers_no:
                        mean_read_operation_latencies.append(res[key]['mean_read_operation_latency'])
                    if writers_no:
                        mean_write_operation_latencies.append(res[key]['mean_write_operation_latency'])

                    title = 'wInt:0, rInt:0, #writes:1000, #reads:1000, #Servers:{}, #Writers:{}, #Readers:{}, \nEUServers:{}, #EUWriters:{}, #EUReaders:{}, #USServers:{}, #USWriters:{}, #USReaders:{}, filesize:32B'.format(
                        servers_no, writers_no, readers_no, sEU, wEU, rEU, sUS, wUS, rUS
                    )


            else:
                print('File {} does not exist!'.format(path))

        plotBarChart(graph_type, title=title, mean_write_operation_latencies=mean_write_operation_latencies,
                         mean_read_operation_latencies=mean_read_operation_latencies)



