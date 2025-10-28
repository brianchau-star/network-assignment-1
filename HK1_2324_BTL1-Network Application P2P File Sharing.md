# ASSIGNMENT 1

# DEVELOP A NETWORK APPLICATION

COURSE: COMPUTER NETWORKS, SEMESTER 1, 2023-2024

# OBJECTIVES

Build a simple file-sharing application with application protocols defined by each group, using the TCP/IP protocol stack.

# APPLICATION DESCRIPTION

- A centralized server keeps track of which clients are connected and storing what files.  
- A client informs the server as to what files are contained in its local repository but does not actually transmit file data to the server.  
- When a client requires a file that does not belong to its repository, a request is sent to the server. The server identifies some other clients who store the requested file and sends their identities to the requesting client. The client will select an appropriate source node and the file is then directly fetched by the requesting client from the node that has a copy of the file without requiring any server intervention.  
- Multiple clients could be downloading different files from a target client at a given point in time. This requires the client code to be multithreaded.  
- The client has a simple command-shell interpreter that is used to accept two kinds of commands.

publish lname fname: a local file (which is stored in the client's file system at lname) is added to the client's repository as a file named fname and this information is conveyed to the server.  
$\bigcirc$  fetch fname: fetch some copy of the target file and add it to the local repository.  
The server has a simple command-shell interpreter  
O discover hostname: discover the list of local files of the host named hostname  
ping hostname: live check the host named hostname

![](images/147a35c10cbb3f7cd9506522de80ccd196d3c37d6a0df91d7102154677d87f20.jpg)  
The supported commands are illustrated in Figure 1.  
Figure 1. Illustration of file-sharing system activities.

- It's important to note that the connecting infrastructure is not implied by the representation in Figure 1. All devices are interconnected through the Internet. Separating them is the logical point of view regarding the protocol's activities.

# WORKING PLAN

Work in a team.  
Each group has up to 4 members.

Phase 1 (First 2 weeks):

- Define specific functions of the file-sharing application  
- Define the communication protocols used for each function

Phase 2 (Next 2 weeks)

- Implement and refine the application according to the functions and protocols defined in Phase 1

# RESULTS

Phase 1 (softcopy):

- Submit the report file of the first phase to BKeL in the predefined section as announced on BKeL.  
- File format (pdf): ASS1_P1_<Group_Name>.pdf

This report includes:

- Define and describe the functions of the application  
- Define the protocols used for each function

Phase 2 (hard and softcopy):

- Submit the report file of the assignment to BKeL  
- File format (.rar): ASS1_<Group_name>.rar

This report includes:

- Phase 1 content  
- Describe each specific function of the application  
Detailed application design (architecture, class diagrams, main classes ...)  
- Validation (sanity test) and evaluation of actual result (performance)  
- Extension functions of the system in addition to the requirements specified in section 2  
- Participants' roles and responsibilities  
- Manual document  
Source code (softcopy)  
- Application file (softcopy) compiled from source code

# EVALUATION

Assignment 1 is worth  $15\%$  of the course grade.

# DEADLINE FOR SUBMISSION

4 weeks from the assignment announcement.
