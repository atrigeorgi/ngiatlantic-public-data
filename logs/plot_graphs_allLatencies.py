import os
from matplotlib import pyplot
import pandas as pd, csv
pd.options.display.float_format = "{:,.2f}".format
import numpy as np
# from hurry.filesize import size
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
# import plottools

#global protocols
# global fig_no
# fig_no = 0
# protocols = ['ARES']#['ARES_EC', 'ARES_ABD']#['ARES_mix']#['ARES']#['ARES_mix_random']#['ARES_mix']#['ARES_EC', 'ARES_ABD']#['ARES'] #'vmwABD_fragmentation', 'vmwABD'
#extra = ''#'mix_random'#''
#file_ext = '_filesizeBig' #'_mix'#'_mix'   '_EC_ABD'    'filesizeBig'


global graph_type
fast_reads = False # compare fast and simple
subfigure = True
log_FM = True # to show thw FM graph as log
global read_type
# read_type = '_fast'
read_type = ''
# read_type = '_simple'
details = False
if read_type == '':
    label_success_loc = 'upper right'
else:
    label_success_loc = 'left'

label_success_loc_lines = 'upper left'

show_std = False # show std on graphs or not

# figs = []
# for i in range(10):
#     figs.append(None)
# pyplot.close(figs[i])


class Plot:
    def combine_graphs(self):
        global graph_type
        global read_type
        global protocols

        # for i in range(10):
        #     pyplot.close(figs[i])
        pyplot.figure(0, figsize=(10, 5))


        for protocol in protocols:
            self.start_plotting(protocol)


        if 'mix' in protocols[0]:
            latencies = ['Write Operation Latency of EC', 'Read Operation Latency of EC', 'Write Operation Latency of ABD', 'Read Operation Latency of ABD', 'Total Write Operation Latency', 'Total Read Operation Latency', 'Recon Operation Latency']
        else:
            latencies = ['Write Operation Latency of EC', 'Read Operation Latency of EC', 'Recon Operation Latency of EC', 'Write Operation Latency of ABD', 'Read Operation Latency of ABD', 'Recon Operation Latency of ABD']

        # if 'reconslowratio' in graph_type:
        #     labelsize = 7
        # else:
        labelsize = 11
        # pyplot.legend(latencies, loc='best', prop={'size': labelsize})
        # if 'reconslowratio' in graph_type:
        #     # pyplot.legend(loc='upper right', prop={'size': labelsize})
        #     pass
        # else:
        pyplot.legend(loc='best', prop={'size': labelsize})

        i = 0

        # path = 'ARES_experiments/combine_graphs/{}{}{}/{}.png'.format(graph_type, extra, file_ext, 'alllatencies')  # filename)
        path = 'combine_graphs/{}{}{}/{}.png'.format(graph_type, extra, file_ext, 'alllatencies')  # filename)


        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        # print('figs read::', figs)
        # if figs[i]:
        #     figs[i].savefig(path)
        # i += 1

        pyplot.savefig(path)





    def start_plotting(self, protocol):
        global graph_type

        if 'ARES' in protocol:
            graph_type_ext = 'reconfixed_slow'
        else:
            graph_type_ext = protocol

        path = '{}/experiments_info_{}/{}.csv'.format(protocol + read_type, protocol + read_type, graph_type + graph_type_ext)  # +extra

        print('path:: ', path)


        with open(path, 'r') as f:
            # 1st solution
            res = pd.read_csv(path, index_col=0)
            res = np.round(res, decimals=9) # 9 dp, because some integers are set with strange dp
            res = res.to_dict()

        # print('keys:', res.values())

        z_axis, sorted_item1, sorted_item2 = None, None, None

        if 'filesize' in graph_type and 'Cassandra' in protocol:
            time_types = ['mean_write_operation_latency', 'mean_read_operation_latency']
            sorted_item = 'filesize'

            x_axis = 'Initial File Size ($2^x$ B)'
            # x_axis = 'Initial File Size (B)'

            y_axis = 'Operation Latency (sec)'

            title = y_axis + ' vs {}\nwInt:2, rInt:2, #writes:60, #reads:60, #Servers:10, #Writers:5, #Readers:5'.format(
                x_axis)


        elif 'filesize' in graph_type:

            time_types = ['mean_write_operation_latency_EC', 'mean_read_operation_latency_EC',
                          'mean_write_operation_latency_ABD', 'mean_read_operation_latency_ABD',
                          'mean_recon_operation_latency']
            sorted_item = 'filesize'

            x_axis = 'Initial File Size ($2^x$ B)'
            # x_axis = 'Initial File Size (B)'

            y_axis = 'Operation Latency (sec)'

            title = y_axis + ' vs {}\nwInt:2, rInt:2, #writes:60, #reads:60, #Servers:10, #Writers:5, #Readers:5'.format(x_axis)

        elif'differentk' in graph_type:
            time_types = ['mean_write_operation_latency_EC', 'mean_read_operation_latency_EC']
            sorted_item = 'k'

            x_axis = 'k'
            # x_axis = 'Initial File Size (B)'

            y_axis = 'Operation Latency (sec)'

            title = y_axis + ' vs {}\nwInt:2, rInt:2, #writes:60, #reads:60, #Servers:10, #Writers:5, #Readers:5, filesize:4MB'.format(
                x_axis)


        elif 'reconslowratio' in graph_type:
            time_types = ['mean_write_operation_latency_total',
                          'mean_read_operation_latency_total',
                          'mean_recon_operation_latency']
            # time_types = ['mean_write_operation_latency_EC', 'mean_read_operation_latency_EC','mean_recon_operation_latency']

            sorted_item = 'reads_count'
            writes_count = 60
            x_axis = '# of Reads'

            y_axis = 'Operation Latency (sec)'

            title = y_axis + ' vs {}\nwInt:2, rInt:2, reconInt:15, #writes:{}, #reconfigs:6, #Servers:10, #Writers:5, #Readers:5, #Recons:1, filesize:4MB'.format(x_axis, writes_count)


        elif 'reconsimpleservers' in graph_type:
            time_types = ['mean_write_operation_latency_EC', 'mean_read_operation_latency_EC',
                          'mean_write_operation_latency_ABD', 'mean_read_operation_latency_ABD',
                          'mean_recon_operation_latency']
            # time_types = ['mean_write_operation_latency_total',
            #               'mean_read_operation_latency_total',
            #               'mean_recon_operation_latency']
            y_axis = 'Operation Latency (sec)'
            x_axis = '# of Servers'

            sorted_item = 'servers_no'
            title = y_axis + ' vs {}\nwInt:2, rInt:2, reconInt:15, #writes:60, #reads:60, #reconfigs:6, #Writers:5, #Readers:5, filesize:4MB'.format(x_axis)

        elif 'scalability' in graph_type and ('Cassandra' in protocol or 'Redis' in protocol) :
            time_types = ['mean_write_operation_latency_'+protocol, 'mean_read_operation_latency_'+protocol]
            sorted_item = 'readers_no'

            x_axis = '# of Readers'
            y_axis = 'Operation Latency (sec)'

            # title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:50, #reads:50, #Servers:5, #Writers:5, filesize:1MB'.format(x_axis)
            title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:50, #reads:50, #Servers:7, #Writers:5, filesize:1MB'.format(x_axis)

        else:
            if 'mix' in protocols[0]:
                time_types = ['mean_write_operation_latency_EC', 'mean_read_operation_latency_EC',
                              'mean_write_operation_latency_ABD', 'mean_read_operation_latency_ABD',
                              'mean_recon_operation_latency']
                #  'mean_write_operation_latency_total', 'mean_read_operation_latency_total',
                #

            else:

                time_types = ['mean_write_operation_latency_EC', 'mean_read_operation_latency_EC',
                              'mean_write_operation_latency_ABD', 'mean_read_operation_latency_ABD',
                              'mean_recon_operation_latency']

            y_axis = 'Operation Latency (sec)'
            x_axis = '# of Readers'

            sorted_item = 'readers_no'
            title = y_axis + ' vs {}\nwInt:3, rInt:3, reconInt:15, #writes:50, #reads:50, #reconfigs:6, #Servers:5, #Writers:5, #Recons:1, filesize:1MB'.format(x_axis)

        # global fig_no


        # print(time_types, y_axises, filenames)
        fig_no = 0
        if z_axis:
            self.plot_graph_3D(res, sorted_item1, sorted_item2, time_types, x_axis, y_axis, z_axis, fig_no, protocol, title)
        else:
            if 'reconslowratio' in graph_type:
                res = {k: v for k, v in res.items() if int(v['writes_count'])==writes_count}
            self.plot_graph(res, sorted_item, time_types, x_axis, y_axis, fig_no, protocol, title)
                # total_labels.append(labels)

                # fig_no += 1
                #print('fig_no: ', fig_no)










    def plot_graph(self, out, sorted_item, time_types, x_axis, y_axis, fig_no=0, protocol=None, title=None):
        print('sorted_item: ', sorted_item)
        #print('fig_no:: ', fig_no, protocol)
        # if not os.path.exists(os.path.dirname(filename)):
        #     os.makedirs(os.path.dirname(filename))

        # print('plot:',out.items())

        out = {k: v for k, v in sorted(out.items(), key=lambda item: item[1][sorted_item])}

        # print('out:',out)

        users = []
        for value in out.values():
            # if 'filesizeBig' in graph_type and log_FM:
            #     users.append(value[sorted_item])
            #     print('value[sorted_item]::',2 ** value[sorted_item])
            #     users.append(2 ** value[sorted_item])
            # else:
            users.append(value[sorted_item])

        #latencies = ['Write Operation Latency of EC', 'Read Operation Latency of EC', 'Write Operation Latency of ABD', 'Read Operation Latency of ABD', 'Recon Operation Latency']
        line_features = {}
        #  red,pink     blue,skyblue  yellow
        line_features['mean_write_operation_latency_EC'] = ['bo-', '-', 'orange', 'Write Operation Latency of EC', 'red']
        line_features['mean_read_operation_latency_EC'] = ['bo-', '-', 'blue', 'Read Operation Latency of EC', 'black']

        line_features['mean_write_operation_latency_ABD'] = ['x', '-.', 'orange', 'Write Operation Latency of ABD', 'brown']
        line_features['mean_read_operation_latency_ABD'] = ['x', '-.', 'blue', 'Read Operation Latency of ABD', 'skyblue']


        if 'ARES_EC' in protocol:
            line_features['mean_recon_operation_latency'] = ['bo-', '-', 'green', 'Recon Operation Latency of EC', 'green']
        elif 'ARES_ABD' in protocol:
            line_features['mean_recon_operation_latency'] = ['x', '-.', 'green', 'Recon Operation Latency of ABD', 'green']
        else:
            line_features['mean_recon_operation_latency'] = ['bo-', '--', 'green', 'Recon Operation Latency', 'green']#-- dotted

        line_features['mean_write_operation_latency_total'] = ['bo-', '--', 'orange', 'Write Operation Latency', 'red']#dotted
        line_features['mean_read_operation_latency_total'] = ['bo-', '--', 'blue', 'Read Operation Latency', 'black']# dotted

        # Cassandra
        line_features['mean_write_operation_latency_Cassandra'] = ['bo-', ':', 'orange', 'Write Operation Latency of Cassandra', 'red']
        line_features['mean_read_operation_latency_Cassandra'] = ['bo-', ':', 'blue', 'Read Operation Latency of Cassandra', 'black']



        line_features['mean_write_operation_latency_Redis'] = ['bo-', '-.', 'orange','Write Operation Latency of Redis', 'red']
        line_features['mean_read_operation_latency_Redis'] = ['bo-', '-.', 'blue','Read Operation Latency of Redis', 'black']

        line_features['mean_write_operation_latency_RedisClustermode'] = ['bo-', '--', 'orange','Write Operation Latency of RedisClustermode', 'red']
        line_features['mean_read_operation_latency_RedisClustermode'] = ['bo-', '--', 'blue','Read Operation Latency of RedisClustermode', 'black']

        for time_type in time_types:
            print('time_type:',time_type,'\n',value,'\n\n')
            print('value:',value,'\n\n')
            print('time_type:',time_type,'\n\n')
            if time_type in value:
                print('time_type:', time_type)

                time = []
                std = []
                for i, value in enumerate(out.values()):
                    time.append(value[time_type])
                    # if not 'recon' in time_type:
                    if show_std:
                        std_operation_latency = time_type.replace('mean', 'sem')#'std')
                        std.append(value[std_operation_latency])



                # f = pyplot
                # figs[fig_no] = pyplot.figure(fig_no, figsize=(10, 5))
                print(time_type, time)
                pyplot.plot(users, time, line_features[time_type][0], linestyle=line_features[time_type][1], linewidth=2, color=line_features[time_type][2], markersize=6, label=line_features[time_type][3])  # color=line_features[time_type][2]       # , label='write latency in seconds: ' + str(writers_time))#, marker='o')
                # pyplot.plot(users[:4], time[:4], line_features[time_type][0], linestyle=line_features[time_type][1], linewidth=2, color=line_features[time_type][2], markersize=6, label=line_features[time_type][3])  # color=line_features[time_type][2]       # , label='write latency in seconds: ' + str(writers_time))#, marker='o')

                if std:
                    print(line_features[time_type])
                    pyplot.errorbar(users, time, yerr=std, linestyle="None", capsize=5, ecolor=line_features[time_type][4])# linewidth=2, capsize=5, markersize=6, zorder=10, ecolor='black'

        labelsize = 11
        pyplot.tick_params(axis='both', which='major', labelsize=labelsize)


        # zip joins x and y coordinates in pairs
        labels = []

        if 'differentk' in graph_type:
            y_lim = 1
        elif 'reconsimpleservers' in graph_type:# or 'reconslowratio' in graph_type:
            y_lim = 2
        else:
            y_lim = 2#10 #7
            # y_lim = 1 #7


        pyplot.ylim([0, y_lim])  # 0.12 0.40 1.5 2(mbs)])

        pyplot.title(title, size=labelsize)
        pyplot.xlabel(x_axis, size=labelsize)
        pyplot.ylabel(y_axis, size=labelsize)

        return labels








    def plot_graph_3D(self, out, sorted_item1, sorted_item2, time_types, x_axis, y_axis, z_axis, fig_no=0, protocol=None, title=None):


        # out1 = {k: v for k, v in sorted(out.items(), key=lambda item: item[1][sorted_item1])}
        # out2 = {k: v for k, v in sorted(out.items(), key=lambda item: item[1][sorted_item2])}

        out = {k: v for k, v in out.items()}

        users1 = []
        for value in out.values():
            users1.append(value[sorted_item1])

        users2 = []
        for value in out.values():
            users2.append(value[sorted_item2])

        line_features = {}
        #  red,pink     blue,skyblue  yellow
        line_features['mean_write_operation_latency_EC'] = ['.', '-', 'orange', 'Write Operation Latency of EC', 'darkorange']
        line_features['mean_read_operation_latency_EC'] = ['.', '-', 'blue', 'Read Operation Latency of EC', 'darkblue']

        line_features['mean_write_operation_latency_ABD'] = ['.', '-.', 'orange', 'Write Operation Latency of ABD', 'peru']
        line_features['mean_read_operation_latency_ABD'] = ['.', '-.', 'blue', 'Read Operation Latency of ABD', 'royalblue']

        if protocol == 'ARES_EC':
            line_features['mean_recon_operation_latency'] = ['bo-', '-', 'green', 'Recon Operation Latency of EC']
        elif protocol == 'ARES_ABD':
            line_features['mean_recon_operation_latency'] = ['x', '-.', 'green', 'Recon Operation Latency of ABD']
        else:
            line_features['mean_recon_operation_latency'] = ['bo-', 'dotted', 'green', 'Recon Operation Latency']#--

        line_features['mean_write_operation_latency_total'] = ['bo-', 'dotted', 'orange', 'Total Write Operation Latency', 'darkorange']
        line_features['mean_read_operation_latency_total'] = ['bo-', 'dotted', 'blue', 'Total Read Operation Latency', 'darkblue']

        # Cassandra
        line_features['mean_write_operation_latency'] = ['bo-', ':', 'orange', 'Write Operation Latency of Cassandra', 'red']
        line_features['mean_read_operation_latency'] = ['bo-', ':', 'blue', 'Read Operation Latency of Cassandra', 'black']

        line_features['mean_write_operation_latency_Redis'] = ['bo-', ':', 'orange', 'Write Operation Latency of Redis', 'red']
        line_features['mean_read_operation_latency_Redis'] = ['bo-', ':', 'blue', 'Read Operation Latency of Redis', 'black']
        line_features['mean_write_operation_latency_RedisClustermode'] = ['bo-', ':', 'orange', 'Write Operation Latency of RedisClustermode','red']
        line_features['mean_read_operation_latency_RedisClustermode'] = ['bo-', ':', 'blue', 'Read Operation Latency of RedisClustermode', 'black']


        ax = pyplot.axes(projection='3d')

        for time_type in time_types:
            # print('value::',value)
            if time_type in value:
                print('time_type:', time_type)

                time = []
                for i, value in enumerate(out.values()):
                    time.append(value[time_type])
                print(time_type, users1,'\n', users2,'\n', time)
                ax.scatter3D(users1, users2, time, line_features[time_type][0], color=line_features[time_type][2], label=line_features[time_type][3], s=6)
                # pyplot.plot(users, time, line_features[time_type][0], linestyle=line_features[time_type][1], linewidth=2, color=line_features[time_type][2], markersize=6, label=line_features[time_type][3])



        labelsize = 11
        pyplot.tick_params(axis='both', which='major', labelsize=labelsize)


        # zip joins x and y coordinates in pairs
        labels = []


        pyplot.title(title, size=labelsize)

        ax.set_xlabel(x_axis, size=labelsize)
        ax.set_ylabel(y_axis, size=labelsize)
        ax.set_zlabel(z_axis, size=labelsize)

        # ax.legend(loc='upper left', prop={'size': labelsize})
        labelsize = 11
        pyplot.legend(bbox_to_anchor=(-0.55, 1),loc='upper left', prop={'size': labelsize})
        return labels








# for graph_type, protocols,extra,file_ext in zip(['filesizeBig_s10w5r5'], [['ARES_EC', 'ARES_ABD', 'Cassandra']], [''], ['_filesizeBig']):
# for graph_type, protocols, extra, file_ext in zip(['scalabilityreconfixed_slow'], [['ARES_EC_slow', 'ARES_ABD_slow', 'Cassandra']],[''], ['_scalability']):
for graph_type, protocols, extra, file_ext in zip(['scalability','scalability'],
                                                      [['Redis', 'RedisClustermode']], [''],
                                                      ['_scalability']):

    #for graph_type in ['readers_s10w5']:#['filesizeBig_s10w5r5']:#['readers_s10w5']:
    operations = ['write', 'read', 'recon']

    pyplot.cycler('color', pyplot.cm.Paired(np.linspace(0, 1, 2)))


    Plot().combine_graphs()

    pyplot.close()





