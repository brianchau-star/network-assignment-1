# P2P File Sharing 

## Manual

Step 1: Run the executable server at <SERVER_IP> (with fixed port 5124)

```
$ ./server
``` 

Step 2: Run the peer servers (with fixed ports 8500, 8501, 8502)

```
$ ./peer --server <SERVER_IP>
or 
$ ./peer -s <SERVER_IP>
```

Step 2: Run the client

```
$ ./client --server <SERVER_IP>
or 
$ ./client -s <SERVER_IP>
```
