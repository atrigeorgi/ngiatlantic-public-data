# ngiatlantic-public-data
Public data collected from the experiments of NGIAtlantic.
This repository contains all the collected raw data from the experiments of the paper “Towards Practical Atomic Distributed Shared Memory: An Experimental Evaluation”. 

## Table of Contents  
[Folders’ Description](#Folders)  
[Different types of log files](#DifferentLogs)

## Folders’ Description

There results of experiments carried out using the Fed4fire testbed. This repository contains subfolders named with the titles of the experimental scenarios in the above paper. 

**Fault-tolerance Test – Node Crashes (only ARES)**: This folder contains subfolders for ARES variants. At the end of each .log filename there is some number, e.g., 11-10-5-1_1. The first four numbers define the number of servers, writers, readers, and reconfigurers, and the last number is the iteration number. 

**Scalability Test – Participation (all algorithms)**: This folder contains subfolders for all algorithms. At the end of each .log filename there is some number, e.g., 11-10-5-0_1. The first four numbers define the number of servers, writers, readers, and reconfigurers, and the last number is the iteration number. 

**Stress Test – Fragmentation Parameter k (only ARES-EC)**: This folder contains subfolders for ARES. At the end of each .log filename there is some number, e.g., 10_11-5-5_1. The first number defines the k value of EC, the next three numbers define the number of servers, writers, and readers, and the last number is the iteration number. 

**Stress Test – Object Size (all algorithms)**: This folder contains a subfolder for each algorithm. The subfolder name has the pattern filesizeBig_fast + the name of the algorithm. In Emulab_logs there are two different subfolders for vmwARES_EC and its fragmented variant, each with different number in their name; this number is the parity value. At the end of each .log filename there is some number, e.g., 1048576_6-1-1_1. The first number is the filesize, the next three numbers define the number of servers, writers, and readers, and the last number is the iteration number. 

**Stress Test – Topology (all algorithms) - Scenario 1**: This folder contains a subfolder for each algorithm.  At the end of each .log filename there is a text of the form: sEU0US3wEU0US0rEU0US1_3-0-1_1. After the ’s’ character, there is the number of EU and US servers, after the ’w’ character, there is the number of EU and US writers; and after the ‘r’ character, there is the number of EU and US readers. For example, in the above string, there are 0 EU servers and 3 US servers etc.  The next three numbers define the total number of servers, writers, and readers, and the last number is the iteration number.

**Stress Test – Topology (all algorithms) - Scenario 2**: This folder contains a subfolder for each algorithm. At the end of each .log filename there is some number, e.g., 6-1-1_1. The first three numbers define the number of servers, writers, and readers, and the last number is the iteration number. 

**Reconfiguring DAP Alternately and Servers randomly,Reconfiguring to the same DAP**: These folders contain subfolders for only ARES variants. At the end of each .log filename there is some number, e.g., 11-10-5-1_1. The first four numbers define the number of servers, writers, readers, and reconfigurers, and the last number is the iteration number. 


## Different types of log files

There are .log files starting with ’user’ and .log files starting with ’client’.  
According to our architecture there is the user level, where a client can pass command through our command-line interface. The log files starting with ’user’ record information from this system level. Subsequently, the requested commands are executed to the Distributed Shared Memory Module (DSMM). The log files starting with ‘client’ record information from the level of DSM Client. 

![architecture](https://user-images.githubusercontent.com/15169270/185813247-ddbbadb7-bd56-4bc4-8971-cb86de896b3d.png)
 
For our experimental results, we use the ’client’ files. This choice is made to have a fair comparison with the commercial databases, Cassandra and Redis. Also, we do not consider the logs ending in phase1 in our results since they are files from the bootstrap phase. We also do not consider the files ending with read_file since they are files from an extra phase at the end, where we do a last read operation to get some statistics of the last generated object. 

