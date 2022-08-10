# How to run this script to plot graphs:

# Step 1
# change which scenarios you want to run from the line 'for graph_type in ...'

# Step 2
# for all the scalability scenarios uncomment the first three lines of 'experiment_type' parameter in 3 separated runs.
# and the first line of 'protocols' parameter

# for all the rest experiments uncomment the fourth line which give to 'experiment_type' parameter an empty value
# and the two last lines of 'protocols' parameter in two separated runs


import os
from matplotlib import pyplot
import pandas as pd, csv

pd.options.display.float_format = "{:,.2f}".format
import numpy as np
# from hurry.filesize import size
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
# import plottools

global protocols, servers
global experiment_type
# experiment_type = 'readers_scalability'
# experiment_type = 'writers_scalability'
# experiment_type = 'servers_scalability'
experiment_type = '' #for filesize, minblock...,

# protocols = ['vmwABD', 'vmwABD_fragmentation', 'ARES_vmwABD', 'vmwARES_fragmentation_vmwABD_fragmentation', 'ARES_vmwEC', 'vmwARES_fragmentation_vmwEC_fragmentation']
# for filesize experiment (EC with parity 1 and EC with parity 5)
protocols = ['vmwABD', 'vmwABD_fragmentation', 'ARES_vmwABD', 'vmwARES_fragmentation_vmwABD_fragmentation', 'ARES_vmwEC_parity_1', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_1', 'ARES_vmwEC_parity_5_fast', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_5_fast', 'ARES_vmwEC_parity_5_slow', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_5_slow']
# protocols = ['vmwABD', 'vmwABD_fragmentation', 'ARES_vmwABD', 'vmwARES_fragmentation_vmwABD_fragmentation', 'ARES_vmwEC_parity_1', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_1', 'ARES_vmwEC_parity_5', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_5']
# protocols = ['vmwABD_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_1', 'vmwARES_fragmentation_vmwEC_fragmentation_parity_5']

#block size experiments
# protocols = ['vmwABD_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation', 'vmwARES_fragmentation_vmwEC_fragmentation']


# scalabilityrecofixed
# protocols = ['ARES_vmwABD', 'ARES_vmwEC']
# protocols = ['vmwARES_fragmentation_vmwABD_fragmentation', 'vmwARES_fragmentation_vmwEC_fragmentation']


# scalabilityrecon...
# protocols = ['ARES']
# protocols = ['vmwARES_fragmentation']

servers=0

global graph_type, daps
fast_ops = False  # False # compare fast and slow
subfigure = True
log_FM = False  # to show thw FM graph as log
global read_type
read_type = '_fast'
# read_type = ''
# read_type = '_slow'
details = False
if read_type == '':
    label_success_loc = 'upper right'
else:
    # label_success_loc = 'lower center'
    label_success_loc = 'upper center'

label_success_loc_lines = 'upper left'


    # best
	# upper right
	# upper left
	# lower left
	# lower right
	# right
	# center left
	# center right
	# lower center
	# upper center
	# center

success = True


'''
onlyFM = False
success = False
graph_type = None
'''


class Plot:
    def combine_graphs(self):
        global graph_type
        global read_type
        global protocols

        for i in range(10):
            pyplot.close(figs[i])

        print('graph type: ', graph_type, onlyFM, success)
        print('protocols 1: ', protocols)

        if 'maxblocksize' in graph_type or onlyFM or 'filesizeBigFragmented_s5w10r40' in graph_type:
            protocols = ['vmwABD_fragmentation']
            print(protocols)
        # else:
        #     protocols = ['vmwABD_fragmentation', 'vmwABD']
        #     print(protocols)

        print('protocols 2: ', protocols)
        # we need the fast and the slow reads' graphs
        if graph_type == 'filesizeBig_s5w5r5' and not read_type:
            graph_type_ = graph_type

            if onlyFM:
                read_type = '_fast'
                graph_type = graph_type_ + read_type
                # try:
                filenames, titles = self.start_plotting(protocols[0])
                # except:
                #     return
            else:

                for read_type in ['_slow', '_fast']:
                    graph_type = graph_type_ + read_type
                    for protocol in protocols:
                        # try:
                        filenames, titles = self.start_plotting(protocol)
                        # except:
                        #     return
                graph_type = graph_type_
        else:
            for protocol in protocols:
                # try:
                # if read_type:
                filenames, titles = self.start_plotting(protocol)
                # else: # new
                #     for read_type_ in ['_slow', '_fast']:
                #         read_type = read_type_
                #         filenames, titles = self.start_plotting(protocol)

                # except:
                #     return
        i = 0
        if not onlyFM and not success:
            for filename, title in zip(filenames, titles):
                if 'filesize' in graph_type:
                    path = 'combine_graphs/{}/{}_{}.png'.format(graph_type, filename, graph_type)
                elif experiment_type == 'servers_scalability':
                    path = 'combine_graphs/{}/{}_{}_writers{}_readers{}.png'.format(graph_type, filename, graph_type, writers, readers)
                else:
                    path = 'combine_graphs/{}/{}_{}_servers{}.png'.format(graph_type, filename,graph_type, servers)

                combine_path = 'combine_graphs/{}.png'.format(graph_type)

                print('path:', path, graph_type, filename)

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                print('figs read:', figs)
                if subfigure:
                    if figs[i]:
                        figs[i].savefig(path)
                else:
                    if fig:
                        fig.savefig(combine_path)
                i += 1

        elif success:
            if 'filesize' in graph_type:
                path = 'combine_graphs/{}/{}_{}.png'.format(graph_type, 'write_operation_latency_{}'.format(graph_type), graph_type)
            elif experiment_type == 'servers_scalability':
                path = 'combine_graphs/{}/{}.png'.format(graph_type, 'write_operation_latency_{}_writers{}_readers_{}'.format(graph_type, writers, readers))
            else:
                path = 'combine_graphs/{}/{}.png'.format(graph_type, 'write_operation_latency_{}_servers_{}'.format(graph_type, servers))
            # path = 'combine_graphs/{}/{}.png'.format(graph_type, filename)

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            #
            # ax = pyplot.subplot(111)
            # axins = zoomed_inset_axes(ax, 3, loc=1)  # zoom = 6
            # axins.plot([0,1], [0,50])
            # print('ax:',ax)#ax: AxesSubplot(0.125,0.11;0.775x0.77)
            # axins = zoomed_inset_axes(ax, 2, loc='lower left', bbox_to_anchor=(0, 0), borderpad=3)
            # axins.plot([26, 28], [0, 10])
            # axins.set_xlim([0, 20])
            # axins.set_ylim([0, 20])

            # ax_zoom = plottools.zoom_axes(fig, ax, [0.1, 0.2], [0.8, 0.9], [0.6, 0.9], [0.6, 0.9])
            # ax_zoom.plot(x, y)
            fig.savefig(path)
        else:
            path = 'combine_graphs/{}/{}.png'.format(graph_type, 'FM')
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            print('figs:', figs)

            # ax = pyplot.subplot(111)

            # axins = zoomed_inset_axes(ax, 1.5, loc='upper right')  # zoom = 1.5
            #
            # # plot in the inset axes
            # # axins.scatter(x, y, s=1)
            #
            # # fix the x, y limit of the inset axes
            # axins.set_xlim(-1, 1)
            # axins.set_ylim(-1, 1)
            #
            # # fix the number of ticks on the inset axes
            # axins.yaxis.get_major_locator().set_params(nbins=3)
            # axins.xaxis.get_major_locator().set_params(nbins=3)
            #
            # pyplot.show()
            if figs[0]:
                figs[0].savefig(path)

        # pyplot.show()

    def start_plotting(self, protocol):
        # new

        if "fast" in protocol or "slow" in protocol:
            if "slow" in protocol:
                graph_type_ = graph_type.replace("fast", "slow")
            else:
                graph_type_ = graph_type
            path = '{}/experiments_info_{}/{}.csv'.format(protocol, protocol, graph_type_)
        else:
            path = '{}/experiments_info_{}/{}.csv'.format(protocol + read_type, protocol + read_type, graph_type)

        # new



        print('path: ', path)

        if not os.path.exists(path):
            return None

        with open(path, 'r') as f:
            # 1st solution
            res = pd.read_csv(path, index_col=0)
            res = np.round(res, decimals=9)  # 9 dp, because some integers are set with strange dp
            res = res.to_dict()

            # 2nd solution
            # reader = csv.reader(open(path, 'r'))
            # res = {}
            # for row in reader:
            #     print(row)
            #      # k, v = row

            #     res[k] = v
            # for row in reader:
            #    d[row[0]][row[1]] = row[2]

        # print('res::', res)

        global servers, readers, writers
        if experiment_type == 'readers_scalability':
            res_ = {}
            servers = 11 #3, 5, 7, 9, 11
            writers = 5
            for k, v in res.items():
                if v['servers_no'] == servers and v['writers_no'] == writers:
                    res_[k] = v
            res = res_

        elif experiment_type == 'writers_scalability':
            res_ = {}
            servers = 11 #3, 5, 7, 9, 11
            readers = 5

            for k, v in res.items():
                if v['servers_no'] == servers and v['readers_no'] == readers:
                    res_[k] = v
            res = res_


        elif experiment_type == 'servers_scalability':
            res_ = {}
            # 5 10 15 20 25
            readers = 25
            writers = 5

            for k, v in res.items():
                if v['readers_no'] == readers and v['writers_no'] == writers:
                    res_[k] = v
            res = res_
        elif 'filesize' in graph_type:
            res_ = {}
            for k, v in res.items():
                if int(v['filesize']):#<=28:
                    res_[k] = v
            res = res_


        # print(res)
        global daps
        daps = ['','']

        print('\n\n\ngraph_type::',graph_type,'\n\n\n')


        if onlyFM:
            time_types = ['mean_write_operation_latency', 'mean_write_operation_latency_withoutFM',
                          'mean_computation_latency']
            y_axises = ['Update Latency of CoBFS (sec)',
                        'Update Latency of CoBFS (sec)',
                        'Update Latency of CoBFS (sec)']
            filenames = ['FM', 'FM', 'FM']

        elif 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type:
            if 'fragmentation' in protocol:
                daps = ['vmwABD_fragmentation', 'vmwEC_fragmentation']
                ext = '_fragmentation'
            else:
                daps = ['vmwABD', 'vmwEC']
                ext = '_non-fragmentation'

            time_types = []
            y_axises = []
            filenames = []

            # if 'scalabilityreconfixed_fast' in graph_type:
            #     for dap in daps:
            #         time_types.extend(['mean_write_operation_latency_{}'.format(dap),
            #                            'mean_read_operation_latency_{}'.format(dap)],
            #                           'mean_recon_operation_latency_{}'.format(dap))  # ['succ_writes_perc_{}'.format(dap),
            #
            #         y_axises.extend(['Operation Latency per File (sec)', 'Operation Latency per File (sec)'])  # 'success rate',
            #
            #         filenames.extend([experiment_type + ext, experiment_type + ext])  # ['success rate of {}.format(dap)',
            #     print('time_types::',time_types)
            #     y_axises.append('Operation Latency per File (sec)')
            #     filenames.append(experiment_type + ext)
            # else:
            for dap in daps:
                time_types.extend(['mean_write_operation_latency_{}'.format(dap),
                                   'mean_read_operation_latency_{}'.format(
                                       dap)])  # ['succ_writes_perc_{}'.format(dap),

                y_axises.extend(['Operation Latency per File (sec)', 'Operation Latency per File (sec)'])  # 'success rate',

                filenames.extend([experiment_type + ext, experiment_type + ext])  # ['success rate of {}.format(dap)',

            time_types.append('mean_recon_operation_latency')
            y_axises.append('Operation Latency per File (sec)')
            filenames.append(experiment_type + ext)
            # print(time_types,'\n\n\n\n')
                # time_types.append('mean_read_operation_latency_{}'.format(dap))
                # y_axises.append('Read Operation Latency of (sec)')
                # filenames.append('read_operation_latency_{}'.format(dap))

        elif 'scalabilityreconfixed_fast' in graph_type:
            if protocol == 'ARES_vmwABD':
                time_types = ['mean_write_operation_latency_vmwABD', 'mean_read_operation_latency_vmwABD', 'mean_recon_operation_latency']
                y_axises = ['Operation Latency per File (sec)', 'Operation Latency per File (sec)', 'Operation Latency per File (sec)']
                ext = '_non-fragmentation'
                filenames = [experiment_type + ext, experiment_type + ext, experiment_type + ext]
            elif protocol == 'ARES_vmwEC':
                time_types = ['mean_write_operation_latency_vmwEC', 'mean_read_operation_latency_vmwEC', 'mean_recon_operation_latency']
                y_axises = ['Operation Latency per File (sec)', 'Operation Latency per File (sec)', 'Operation Latency per File (sec)']
                ext = '_non-fragmentation'
                filenames = [experiment_type + ext, experiment_type + ext, experiment_type + ext]

            elif protocol == 'vmwARES_fragmentation_vmwABD_fragmentation':
                time_types = ['mean_write_operation_latency_vmwABD_fragmentation', 'mean_read_operation_latency_vmwABD_fragmentation', 'mean_recon_operation_latency']
                y_axises = ['Operation Latency per File (sec)', 'Operation Latency per File (sec)', 'Operation Latency per File (sec)']
                ext = '_fragmentation'
                filenames = [experiment_type + ext, experiment_type + ext, experiment_type + ext]
            elif protocol == 'vmwARES_fragmentation_vmwEC_fragmentation':
                time_types = ['mean_write_operation_latency_vmwEC_fragmentation', 'mean_read_operation_latency_vmwEC_fragmentation', 'mean_recon_operation_latency']
                y_axises = ['Operation Latency per File (sec)', 'Operation Latency per File (sec)', 'Operation Latency per File (sec)']
                ext = '_fragmentation'
                filenames = [experiment_type + ext, experiment_type + ext, experiment_type + ext]




        elif success:

            time_types =['succ_writes_perc', 'mean_write_operation_latency']
            y_axises = ['success rate', 'Update Operation Latency per File (sec)']
            filenames = ['success rate', 'write_operation_latency']  # , 'total_op_latency_withoutFM', 'com_latency_write']


        else:

            time_types = ['mean_read_operation_latency']  # , 'mean_write_operation_latency', 'mean_write_operation_latency_withoutFM', 'mean_computation_latency']
            y_axises = ['Read Operation Latency per File (sec)']  # , 'Write Operation Latency (sec)','Write Operation Latency without FM latency(sec)', 'Write Computation Latency of FM(sec)']
            filenames = ['read_operation_latency']  # , 'write_operation_latency', 'write_operation_latency_withoutFM', 'computation_latency']

        titles = []

        # new experiments for all algorithms in emulab, before proceding with AWS
        if experiment_type == 'writers_scalability':
            sorted_item = 'writers_no'
            x_axis = '# of Writers'


            if 'scalabilityreconfixed_fast' in graph_type or 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type:
                for y_axis in y_axises:
                    title = y_axis + ' vs {}\nwInt:3, rInt:3, reconInt:15, #writes:60, #reads:60, #recons:7, #Servers:{}, #Readers:{}, init_filesize:4MB'.format(
                        x_axis, servers, readers)
                    title += ',\nmaxBlockSize:1MB, minBlockSize:512KB, avgBlockSize:512KB'
                    titles.append(title)
            else:
                for y_axis in y_axises:
                    title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:20, #reads:20, #Servers:{}, #Readers:{}, init_filesize:4MB'.format(
                        x_axis, servers, readers)
                    title += ',\nmaxBlockSize:1MB, minBlockSize:512KB, avgBlockSize:512KB'
                    titles.append(title)
        elif experiment_type == 'readers_scalability':
            sorted_item = 'readers_no'
            x_axis = '# of Readers'

            if 'scalabilityreconfixed_fast' in graph_type or 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type:
                for y_axis in y_axises:
                    title = y_axis + ' vs {}\nwInt:3, rInt:3, reconInt:15, #writes:20, #reads:20, #recons:7, #Servers:{}, #Writers:{}, init_filesize:4MB'.format(x_axis, servers, writers)
                    title += ',\nmaxBlockSize:1MB, minBlockSize:512KB, avgBlockSize:512KB'
                    titles.append(title)

            else:
                for y_axis in y_axises:
                    title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:20, #reads:20, #Servers:{}, #Writers:{}, init_filesize:4MB'.format(x_axis, servers, writers)
                    title += ',\nmaxBlockSize:1MB, minBlockSize:512KB, avgBlockSize:512KB'
                    titles.append(title)

        elif experiment_type == 'servers_scalability':
            sorted_item = 'servers_no'
            x_axis = '# of Servers'

            for y_axis in y_axises:
                title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:20, #reads:20, #Writers:{}, #Readers:{}, init_filesize:4MB'.format(x_axis, writers, readers)
                title += ',\nmaxBlockSize:1MB, minBlockSize:512KB, avgBlockSize:512KB'
                titles.append(title)


        elif 'filesize' in graph_type:
            sorted_item = 'filesize'
            x_axis = 'Initial File Size ($2^x$ B)'

            for y_axis in y_axises:
                title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:20, #reads:20, #Servers:11, #Writers:5, #Readers:5'.format(x_axis)
                title += ',\nmaxBlockSize:1MB, minBlockSize:512KB, avgBlockSize:512KB'
                titles.append(title)

        elif 'minblocksize' in graph_type:
            sorted_item = 'minblocksize'
            x_axis = 'Min/Avg Block Size ($2^x$ B)'
            # x_axis_block = x_axis

            for y_axis in y_axises:
                title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:20, #reads:20, #Servers:11, #Writers:5, #Readers:5, init_filesize:4MB'.format(x_axis)

                # if protocol == 'vmwABD_fragmentation':
                title += ',\nmaxBlockSize:1MB'

                titles.append(title)

        elif 'MaxMinAvgblocksize' in graph_type:
            sorted_item = 'minblocksize'
            x_axis = 'Min/Avg Block Size ($2^x$ B), Max Block Size ($2^{x+1}$ B )'
            # x_axis_block = x_axis

            for y_axis in y_axises:
                title = y_axis + ' vs {}\nwInt:3, rInt:3, #writes:20, #reads:20, #Servers:11, #Writers:5, #Readers:5, init_filesize:512B'.format(x_axis)


                titles.append(title)

        # print('\n\n\nres:', res)

        fig_no = 0

        # print(time_types, y_axises, filenames)
        # print('time_types:',time_types)
        for time_type, y_axis, filename, title in zip(time_types, y_axises, filenames, titles):

            flag = any(time_type in d.keys() for d in res.values())
            if flag:
                if time_type == 'mean_write_operation_latency' or time_type == 'mean_write_operation_latency_withoutFM':
                    label = ['succ_writes_no', 'writes_no', 'succ_writes_perc']
                elif time_type == 'mean_read_operational_latency':
                    label = ['reads_no', 'reads_no_block']
                else:
                    label = None

                if not (('maxblocksize' in graph_type or 'mean_write_op_latency_withoutFM' in graph_type) and (protocol == 'vmwABD')):
                    # print('protocol:: ', protocol, time_type, '\n')

                    labels = self.plot_graph(res, sorted_item, time_type, x_axis, y_axis,
                                             '{}/graphs_{}/{}'.format(protocol, graph_type, filename + '.png'), label,
                                             fig_no, protocol, title)
                    total_labels.append(labels)

            # print('time_type:',time_type,'\n\n\n\n\n\n')
                # print('fig_no: ', fig_no)

        return filenames, titles

    def annotate(self, fig_no, label, x, y, y_dist, ha, color):
        if subfigure:
            f = pyplot
            size = 7
        else:
            f = axs[fig_no][0]
            size = 20
        f.annotate(label,  # this is the text
                   (x, y),  # this is the point to label
                   textcoords="offset points",  # how to position the text
                   xytext=(0, y_dist),  # distance from text to points (x,y)
                   ha=ha,  # horizontal alignment can be left, right or center
                   size=size,
                   color=color
                   )

    def plot_graph(self, out, sorted_item, time_type, x_axis, y_axis, filename, labels_name, fig_no=0, protocol=None,
                   title=None):

        # print('fig_no:: ', fig_no, protocol)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        # print('plot:',out.items())

        out = {k: v for k, v in sorted(out.items(), key=lambda item: item[1][sorted_item])}

        # print('\n\n\n\nkeys: \n', out.keys())
        '''
        if 'filesize' in graph_type:
            users = [1, 8, 64, 512]


        elif 'maxblocksize' in graph_type:
            users = [8, 32, 128, 512]

            #users = ['$\mathregular{2^10}$', '$\mathregular{2^13}$', '$\mathregular{2^16}$', '$\mathregular{2^19}$']

        else:
        '''

        if 'fragmentation' in protocol:
            start_blocks_no = []
            end_blocks_no = []
            for value in out.values():
                if 'start_blocks_no' in value:
                    start_blocks_no.append(value['start_blocks_no'])
                    end_blocks_no.append(value['end_blocks_no'])

        filesizes = []

        for value in out.values():
            if 'last_filesize' in value:
                filesizes.append(value['last_filesize'])

        users = []
        for value in out.values():
            if onlyFM and 'filesizeBig' in graph_type and log_FM:
                # users.append(value[sorted_item])
                users.append(2 ** value[sorted_item])
            else:
                users.append(value[sorted_item])

        time = []
        std = []
        maxes = []
        mins = []
        for i, value in enumerate(out.values()):
            time.append(value[time_type])

            if 'read' in time_type:
                std.append(value['std_read_operation_latency'])
                maxes.append(value['max_read_operation_latency'])
                mins.append(value['min_read_operation_latency'])
            elif 'write' in time_type:
                std.append(value['std_write_operation_latency'])
                maxes.append(value['max_write_operation_latency'])
                mins.append(value['min_write_operation_latency'])

        if success:
            if 'success' in y_axis:
                f = ax2
            else:
                f = ax
            labelsize = 9

        elif subfigure or onlyFM:
            # if onlyFM:
            #     pyplot.xscale("log")

            f = pyplot
            figs[fig_no] = pyplot.figure(fig_no, figsize=(10, 5))
            # figs[fig_no], ax_fig = pyplot.subplots(figsize=(10, 5))
            # print('figs: ', figs)
            labelsize = 9
        else:
            f = axs[fig_no][0]
            labelsize = 9

        # print('x,y: ', users, time)
        if onlyFM:
            # print('users:', users, ' time:',time)
            if 'recon' in time or 'recon' in time_type:
                mfc = 'none'
            else:
                mfc = line_features[protocol][2]
            f.plot(users, time, line_features[time_type][0], linestyle=line_features[time_type][1], linewidth=2,
                   markersize=4, marker=line_features[time_type][0], mfc=mfc)  # color=line_features[time_type][2]       # , label='write latency in seconds: ' + str(writers_time))#, marker='o')
        else:
            # in Read Operation Latency, put the filesize field in graph
            pass
            # if 'Read' in y_axis and 'filesize' not in graph_type and 'minblocksize' not in graph_type:
            #     for i, (fsize) in enumerate(filesizes):
            #         f.text(users[i] - 1.2, time[i] + 0.05, s=str(round(int(fsize) / 1024.0)) + 'KB')


                # if 'fragm' in protocol:
                #     f.annotate('final file size', size=10, xy=(users[0] + 0.1, time[0] + 0.1),
                #                xytext=(users[0] + 0.2, time[i] + 0.1), arrowprops=dict(arrowstyle='->'), fontsize=10,
                #                style='italic')  # shrink=0.0005, width=0.1,

            init_protocol = protocol
            if 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type:
                if 'read' in time_type:
                    op = 'read'
                elif 'write' in time_type:
                    op = 'write'
                elif 'recon' in time_type:
                    op = 'recon'

                if op == 'recon':
                    protocol = protocol + '_' + op
                else:
                    if 'fragmentation' in time_type:
                        splits = time_type.split('_')
                        dap = splits[-2]+'_'+splits[-1]
                    else:
                        dap = time_type.split('_')[-1]
                    protocol = protocol + '_' + dap + '_' + op
            elif 'scalabilityreconfixed_fast' in graph_type:
                if 'read' in time_type:
                    op = 'read'
                elif 'write' in time_type:
                    op = 'write'
                elif 'recon' in time_type:
                    op = 'recon'
                protocol = protocol + '_' + op

                # latencies.append(line_features[prot + '_' + 'recon'][-1] + ' latency')

            # axins = inset_axes(ax, 1, 1, loc="lower left", bbox_to_anchor=(0.1, 0.1))#, bbox_to_anchor=(1, 2), bbox_transform=ax.transAxes)#10, 20,

            if 'success' in y_axis:
                # ax2 = pyplot.twinx()

                if 'block' not in y_axis:
                    users = []

                    for value in out.values():
                        users.append(value[sorted_item])  # + line_features[time_type + '_' + protocol][0]) why I need this extra line?

                    if 'maxblocksize' in graph_type or 'minblocksize' in graph_type or 'MaxMinAvgblocksize' in graph_type or 'filesize' in graph_type:
                        if 'minblocksize' in graph_type or 'MaxMinAvgblocksize' in graph_type:
                            f.bar(users, time, width=0.2, fill=False, linestyle=line_features[protocol][1], edgecolor=line_features[protocol][2])
                        elif 'fragmentation' in protocol:
                            f.bar(users, time, width=0.3, fill=False, linestyle=line_features[protocol][1], edgecolor=line_features[protocol][2])
                        else:
                            users_ = [user - 0.3 for user in users]
                            f.bar(users_, time, width=0.3, fill=False, linestyle=line_features[protocol][1], edgecolor=line_features[protocol][2])

                        # 0.3 (max bl) 1.5 #color=line_features[time_type + '_' + protocol][1]
                    else:
                        # f.bar(users, time,  width=1.5)
                        if 'fragmentation' in protocol:
                            f.bar(users, time, width=1.5, fill=False, linestyle=line_features[protocol][1], edgecolor=line_features[protocol][2])
                        else:
                            users_ = [user - 1.5 for user in users]
                            f.bar(users_, time, width=1.5, fill=False, linestyle=line_features[protocol][1], edgecolor=line_features[protocol][2])


            else:
                if fast_ops and 'slow' in graph_type:
                    if 'recon' in time or 'recon' in protocol:
                        mfc = 'none'
                    else:
                        mfc = line_features[protocol][2]
                    # f.plot(users, time, line_features[protocol][0], linestyle=line_features[protocol][1], linewidth=2, markersize=4, color='chocolate')  # color=line_features[protocol][2]       #linestyle=line_features[protocol][1]# , label='write latency in seconds: ' + str(writers_time))#, marker='o')
                    f.plot(users, time, linestyle=line_features[protocol][1], linewidth=2, markersize=4,
                           color='chocolate',  marker=line_features[protocol][0], mfc=mfc)  # color=line_features[protocol][2]       #linestyle=line_features[protocol][1]# , label='write latency in seconds: ' + str(writers_time))#, marker='o')
                    f.errorbar(users, time, yerr=std, linestyle="None", capsize=3, linewidth=2, markersize=4,
                               ecolor='black', ls='none', zorder=3)

                    f.errorbar(users, time, [np.array(time) - np.array(mins), np.array(maxes) - np.array(time)],
                               fmt='.k', ecolor='gray', lw=1)


                elif fast_ops and 'fast' in graph_type:
                    if 'recon' in time or 'recon' in protocol:
                        mfc = 'none'
                    else:
                        mfc = line_features[protocol][2]

                    # f.plot(users, time, line_features[protocol][0], linestyle=line_features[protocol][1],linewidth=2, markersize=4, color='blue')  # color=line_features[protocol][2]       #linestyle=line_features[protocol][1]# , label='write latency in seconds: ' + str(writers_time))#, marker='o')
                    f.plot(users, time, linestyle=line_features[protocol][1], linewidth=2, markersize=4,
                           color=line_features[protocol][2],  marker=line_features[protocol][0], mfc=mfc) # , label='write latency in seconds: ' + str(writers_time))#, marker='o')



                    f.errorbar(users, time, yerr=std, linestyle="None", capsize=3, linewidth=2, markersize=4,
                               ecolor='black', ls='none', zorder=3)

                    f.errorbar(users, time, [np.array(time) - np.array(mins), np.array(maxes) - np.array(time)],
                               fmt='.k', ecolor='gray', lw=1)


                else:

                    if 'recon' in time or 'recon' in protocol:
                        mfc = 'none'
                    else:
                        mfc = line_features[protocol][2]

                    f.plot(users, time, linestyle=line_features[protocol][1], linewidth=2, markersize=4,color=line_features[protocol][2],  marker=line_features[protocol][0], label=line_features[protocol][-1], mfc=mfc)# , label='write latency in seconds: ' + str(writers_time))#, marker='o')

                    # zoom
                    # if "fragmentation" in protocol:
                    #     axins.plot(users, time)

                    # f.errorbar(users, time, yerr=std, linestyle="None", capsize=3, linewidth=2, markersize=4,ecolor='black', zorder=3)  # ls='none'

                    # f.errorbar(users, time, [np.array(time) - np.array(mins), np.array(maxes) - np.array(time)],
                    #            fmt='.k', ecolor='gray', lw=1)


        f.tick_params(axis='both', which='major', labelsize=labelsize)

        # zip joins x and y coordinates in pairs
        labels = []


        if 'success' in y_axis:
            f.set_ylabel('success (%)', size=labelsize)
            f.set_ylim([0, 100])

        elif subfigure and not success:
            pyplot.title(title, size=labelsize)
            pyplot.xlabel(x_axis, size=labelsize)
            pyplot.ylabel(y_axis, size=labelsize)
            #
            if 'scalabilityrecon' in graph_type:
                f.ylim([0, 3])
            elif 'scalability' in graph_type:
                f.ylim([0, 1.75])
            elif 'filesize' in graph_type:
                f.ylim([0,80])#40
            elif 'minblocksize' in graph_type:
                f.ylim(([0,7]))
        elif success:
            f.set_title(title, size=labelsize)
            f.set_xlabel(xlabel=x_axis, size=labelsize)
            f.set_ylabel(ylabel=y_axis, size=labelsize)
            if 'scalabilityrecon' in graph_type:
                f.set_ylim([0, 3])
            elif 'scalability' in graph_type:
                f.set_ylim([0, 1.75])
            elif 'filesize' in graph_type:
                f.set_ylim([0,80])#10
            elif 'minblocksize' in graph_type:
                f.set_ylim(([0,1]))
        else:
            f.set_title(title, size=30)
            f.set_xlabel(xlabel=x_axis, size=30)
            f.set_ylabel(ylabel=y_axis, size=30)
            f.text(0.5, -0.15, '({})'.format(axs[fig_no][1]), ha="center", size=50, transform=axs[fig_no][0].transAxes)

        # print('y_axis', y_axis)

        if success and 'success' in y_axis:
            latencies = []
            if 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type:
                for prot in protocols:
                    for dap in daps:
                        for op in ['write','read']:
                            latencies.append(line_features[prot+ '_' + dap + '_' +op][-1] + ' latency')
                latencies.append(line_features[prot + '_' + 'recon'][-1] + ' latency')

            elif 'scalabilityreconfixed_fast' in graph_type:
                for prot in protocols:
                    for op in ['write', 'read', 'recon']:
                        latencies.append(line_features[prot + '_' +op][-1] + ' latency')
            else:
                for prot in protocols:
                    latencies.append(line_features[prot][-1] + ' latency')

            for i,latency in enumerate(latencies):
                latencies[i] = latency.replace('latency', 'success ratio')

            if read_type != '':
                f.legend(latencies, loc=label_success_loc, prop={'size': labelsize}, bbox_to_anchor=((0.6, 1)))#bbox_to_anchor=((0.6, 1))
            else:
                f.legend(latencies, loc=label_success_loc, prop={'size': labelsize})

        elif success:
            latencies = []
            if 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type:
                for prot in protocols:
                    for dap in daps:
                        for op in ['write','read']:
                            latencies.append(line_features[prot+ '_' + dap + '_' +op][-1] + ' latency')
                latencies.append(line_features[prot + '_' + 'recon'][-1] + ' latency')
            elif 'scalabilityreconfixed_fast' in graph_type:
                for prot in protocols:
                    for op in ['write', 'read', 'recon']:
                        latencies.append(line_features[prot + '_' +op][-1] + ' latency')

            else:
                for prot in protocols:
                    latencies.append(line_features[prot][-1] + ' latency')

            f.legend(latencies, loc=label_success_loc_lines, prop={'size': labelsize})

            # f.legend(['initial # of blocks - final # of blocks'], loc='right', prop={'size': labelsize})

        elif not onlyFM:
            if 'Computation' in y_axis or 'without FM latency' in y_axis or 'maxblocksize' in graph_type or 'block' in y_axis:
                f.legend([protocols[0] + ' latency'], loc='best', prop={'size': labelsize})

            else:
                if fast_ops:
                    f.legend(['CoBFS latency', 'CoABD latency', 'CoBFS latency with read optimization',
                              'CoABD latency with read optimization'], loc='best', prop={'size': labelsize})

                else:
                    if 'ARESEC' in protocols:
                        f.legend(['ARES/EC latency'], loc='best', prop={'size': labelsize})
                    else:
                        latencies = []
                        if 'scalabilityreconserverschanging_fast' in graph_type or 'scalabilityreconrandom_fast' in graph_type or 'scalabilityreconchanging_fast' in graph_type:
                            for prot in protocols:
                                for dap in daps:
                                    for op in ['write', 'read']:
                                        latencies.append(line_features[prot + '_' + dap + '_' + op][-1] + ' latency')
                            latencies.append(line_features[prot + '_' + 'recon'][-1] + ' latency')

                        elif 'scalabilityreconfixed_fast' in graph_type:
                            for prot in protocols:
                                for op in ['write', 'read', 'recon']:
                                    latencies.append(line_features[prot + '_' +op][-1] + ' latency')

                        else:
                            for prot in protocols:
                                latencies.append(line_features[prot][-1] + ' latency')
                        f.legend(latencies, loc='best', prop={'size': labelsize})


        else:
            latencies = ['Update Operation Latency',
                         'Update Operation Latency without FM latency',
                         'Update Computation Latency of FM']
            f.legend(latencies, loc='best', prop={'size': labelsize})

        # if 'Read' in y_axis:
        #     f.legend(['file size in KB'], loc='upper left', prop={'size': labelsize})

        protocol = init_protocol

        print('graph_type:::',graph_type)

        # if 'filesize' in graph_type:
        # if subfigure:
        #     pyplot.yscale("log")
        # else:
        #     pyplot.set_yscale("log")

            # pyplot.yticks(np.arange(0.0, 70.0, 0.50))
        # try:
            # mark_inset(f, f, loc1=1, loc2=3, fc="none", ec="0.5")
            # ax_zoom = plottools.zoom_axes(fig, ax, [0.1, 0.2], [0.8, 0.9], [0.6, 0.9], [0.6, 0.9])
            # ax_zoom.plot(x, y)
        # except:
        #     pass

        # mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")



        return labels


# for graph_type in ['maxblocksize_s10w10r10', 'filesize_s10w10r10']:
# for graph_type in ['minblocksize_s10w10r10']:
# for graph_type in ['minblocksize_s10w10r10', 'filesizeReadUnsucc_s10w10r10', 'writers_s10r10', 'readers_s10w10', 'servers_w10r10', 'maxblocksize_s10w10r10', 'filesize_s10w10r10']:
# for graph_type in ['minblocksize_s10w10r10']: readers_s10w1

# for graph_type in ['scalabilityreconserverschanging_fast']:#['MaxMinAvgblocksize_fast']:#['minblocksize_fast']:#['filesizeBig_fast']:   # ['filesizeBig_s5w5r5'+read_type]:#['readersfast_s10w10', 'writersfast_s10r10', 'serversfast_w10r10']:#['minblocksizefast_s10w10r10']:#['filesizeBig_s5w5r5'+read_type]:#['readersfast_s10w10', 'writersfast_s10r10', 'serversfast_w10r10']:#filesizeBigFragmented_s5w10r40: :#['filesizeBig_s5w5r5'+read_type]: #['filesizeBig_s5w5r5'+read_type]:
# for graph_type in ['scalability_fast', 'MaxMinAvgblocksize_fast', 'minblocksize_fast', 'scalabilityreconserverschanging_fast', 'scalabilityreconchanging_fast', 'scalabilityreconfixed_fast', 'scalabilityreconrandom_fast']:#filesizeBig_fast

# for graph_type in ['scalability_fast']:
# for graph_type in ['scalabilityreconfixed_fast']:
# for graph_type in ['MaxMinAvgblocksize_fast', 'minblocksize_fast']:
for graph_type in ['filesizeBig_fast']:
# for graph_type in ['filesizeBig']:

    # for graph_type in ['scalabilityreconserverschanging_fast', 'scalabilityreconchanging_fast','scalabilityreconrandom_fast']:

    for onlyFM, success in zip([True, False, False], [False, True, False]):

        # https://matplotlib.org/3.2.1/tutorials/intermediate/legend_guide.html
        if not onlyFM:
            # protocols = ['vmwABD_fragmentation', 'vmwABD', 'vmwARES_fragmentation_vmwEC_fragmentation', 'vmwARES_fragmentation_vmwABD_fragmentation', 'ARES_vmwABD', 'ARES_vmwEC']

            line_features = {}
            line_features['vmwABD'] = ['D', '-', 'orange', 'CoABD']
            line_features['ARES_vmwABD'] = ['s', '-', 'green', 'CoARES_ABD']
            line_features['ARES_vmwEC'] = ['o', '-', 'purple', 'CoARES_EC']

            line_features['ARES_vmwABD_write'] = ['s', '-', 'green', 'CoARES_ABD write']
            line_features['ARES_vmwABD_read'] = ['s', ':', 'green', 'CoARES_ABD read']
            line_features['ARES_vmwEC_write'] = ['o', '-', 'purple', 'CoARES_EC write']
            line_features['ARES_vmwEC_read'] = ['o', ':', 'purple', 'CoARES_EC read']

            # vmwARES_fragmentation
            line_features['vmwARES_fragmentation_vmwABD_fragmentation_write'] = ['s', '-', 'green', 'CoARES_ABD-F write']#'-.'
            line_features['vmwARES_fragmentation_vmwABD_fragmentation_read'] = ['s', ':', 'green', 'CoARES_ABD-F read']
            line_features['vmwARES_fragmentation_vmwEC_fragmentation_write'] = ['o', '-', 'purple', 'CoARES_EC-F write']#'-.'
            line_features['vmwARES_fragmentation_vmwEC_fragmentation_read'] = ['o', ':', 'purple', 'CoARES_EC-F read']


            line_features['vmwARES_fragmentation_recon'] = ['x', '--', 'blue', 'CoARES-F recon']
            line_features['ARES_recon'] = ['x', '--', 'blue', 'CoARES recon']

            line_features['vmwARES_fragmentation_vmwEC_fragmentation_recon'] = ['o', '--', 'purple', 'CoARES_EC-F recon']
            line_features['vmwARES_fragmentation_vmwABD_fragmentation_recon'] = ['s', '--', 'green', 'CoARES_ABD-F recon']

            line_features['ARES_vmwEC_recon'] = ['o', '--', 'purple', 'CoARES_EC recon']
            line_features['ARES_vmwABD_recon'] = ['s', '--', 'green', 'CoARES_ABD recon']


            line_features['ARES_vmwEC_parity_1'] = ['o', '-', 'mediumpurple', 'CoARES_EC with parity 1']
            line_features['ARES_vmwEC_parity_5'] = ['o', '-', 'purple', 'CoARES_EC with parity 5']
            line_features['ARES_vmwEC_parity_5_fast'] = ['o', '-', 'purple', 'CoARES_EC with parity 5']#new
            line_features['ARES_vmwEC_parity_5_slow'] = ['o', '-', 'grey', 'CoARES_EC with parity 5 \n(without optimization)']#new



            line_features['vmwABD_fragmentation'] = ['D', '-.', 'orange', 'CoABD-F']
            line_features['vmwARES_fragmentation_vmwABD_fragmentation'] = ['s', '-.', 'green', 'CoARES_ABD-F']
            line_features['vmwARES_fragmentation_vmwEC_fragmentation'] = ['o', '-.', 'purple', 'CoARES_EC-F']
            line_features['vmwARES_fragmentation_vmwEC_fragmentation_parity_1'] = ['o', '-.', 'mediumpurple', 'CoARES_EC-F with parity 1']
            line_features['vmwARES_fragmentation_vmwEC_fragmentation_parity_5'] = ['o', '-.', 'purple', 'CoARES_EC-F with parity 5']
            line_features['vmwARES_fragmentation_vmwEC_fragmentation_parity_5_fast'] = ['o', '-.', 'purple', 'CoARES_EC-F with parity 5'] # new
            line_features['vmwARES_fragmentation_vmwEC_fragmentation_parity_5_slow'] = ['o', '-.', 'grey', 'CoARES_EC-F with parity 5 \n(without optimization)'] # new

            line_features['succ_writes_perc_vmwABD'] = [0.00, 'cyan']
            line_features['succ_writes_perc_vmwABD_fragmentation'] = [1, 'violet']  # 3 for filesize, 1

            # # line_features['succ_writes_perc_block_vmwABD_fragmentation_new'] = [2, 'red'] #0.50#lightsteelblue



        else:
            line_features = {}
            line_features['mean_write_operation_latency'] = ['x', '-.', 'gray']
            line_features['mean_write_operation_latency_withoutFM'] = ['x', '-.', 'plum']
            line_features['mean_computation_latency'] = ['x', '-.', 'skyblue']

        # protocol = 'vmwABD'#'vmwABD_fragmentation'

        total_labels = []

        figs = []
        for i in range(10):
            figs.append(None)
            pyplot.close(figs[i])

        # success rate
        ax, ax2 = None, None
        fig, ax = pyplot.subplots(figsize=(10, 5))
        ax2 = ax.twinx()

        # Set ax's patch invisible
        # Set ax's patch invisible
        ax.patch.set_visible(False)
        # Set axtwin's patch visible and colorize it in grey
        ax2.patch.set_visible(True)

        # move ax in front
        ax.set_zorder(ax2.get_zorder() + 1)

        if not subfigure:
            fig, ((ax1, ax2), (ax3, ax4)) = pyplot.subplots(2, 2, figsize=(50, 30))
            fig.tight_layout(pad=20.0)
            axs = {0: [ax1, 'a'], 1: [ax2, 'b'], 2: [ax3, 'c'], 3: [ax4, 'd']}

        pyplot.close(fig)

        if not onlyFM:
            Plot().combine_graphs()


