#!/bin/bash

python3 P2PFileSharingPeer.py 127.0.0.1:8088 PeerTestRepositories/peer1-repo  ../example-input/peer1-schedule.txt  > Peer1.log 2>&1 &
pid2=$!

python3 P2PFileSharingPeer.py 127.0.0.1:8088 PeerTestRepositories/peer2-repo  ../example-input/peer2-schedule.txt  > Peer2.log 2>&1 &
pid3=$!

python3 P2PFileSharingPeer.py 127.0.0.1:8088 PeerTestRepositories/peer3-repo  ../example-input/peer3-schedule.txt 

wait $pid2 $pid3 

echo "All scripts finished. Outputs are in script1.log, script2.log, script3.log, and script4.log"

