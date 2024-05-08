# import the necessary libraries
import argparse
from concurrent import futures
import grpc
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc
import random
from enum import Enum
import threading

# define the possible states of the node
class NodeState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

# define the constants
ELECTION_TIMEOUT_MIN = 2000
ELECTION_TIMEOUT_MAX = 4000
APPEND_ENTRIES_TIMEOUT = 400

# Global variables for the node
NODE_ID = None
SERVERS_INFO = {}
SUSPEND = False
NODE_STATE = NodeState.FOLLOWER
CURRENT_TERM = 0
commited_value = 0
uncommited_value = 0
timer = None
LeaderID = None
Votes = 0
VOTED = False

# start the timer
def start_timer():
    global timer, NODE_STATE
    if NODE_STATE == NodeState.LEADER:
        return
    timer_interval = random.randint(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX) / 1000.0
    timer = threading.Timer(timer_interval, hold_election) 
    timer.start()

# stop the timer
def stop_timer():
    global timer
    if timer:
        timer.cancel()

# reset the timer
def reset_timer():
    stop_timer()
    start_timer()

# hold the election
def hold_election():
    print("TIMEOUT Expired | Leader Died")
    global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
    
    if SUSPEND:
        return
    
    
    NODE_STATE = NodeState.CANDIDATE
    CURRENT_TERM += 1
    VOTED = True
    Votes = 1

    print(f"STATE: {NODE_STATE.name} | TERM: {CURRENT_TERM}")
    
    for node_id in SERVERS_INFO.keys():
        if node_id == NODE_ID:
            continue

        node_proxy = get_node_proxy(node_id)
        try:
            vote_request = pb2.RequestVoteArgs(candidate_term=CURRENT_TERM, candidate_id=NODE_ID)
            vote_response = node_proxy.RequestVote(vote_request)
            if vote_response.vote_result:
                Votes += 1
        except grpc.RpcError as e:
            continue
        
    print("Votes aggregated")

    # It should become a leader if it gets more than half of the votes
    if Votes > len(SERVERS_INFO) // 2:
        NODE_STATE = NodeState.LEADER
        print(f"STATE: {NODE_STATE.name} | TERM: {CURRENT_TERM}")
        LeaderID = NODE_ID
        stop_timer()
        append_entries()  # Start the append_entries function
    else:
        NODE_STATE = NodeState.FOLLOWER
        print(f"STATE: {NODE_STATE.name} | TERM: {CURRENT_TERM}")
        reset_timer()  # Reset the timer if the node did not become a leader

    # Reset votes
    Votes = 0
    
# append entries to the followers and send the heartbeat
def append_entries():
    global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
    
    # count the number of nodes that acknowledged the heartbeat message
    count = 0
    
    if NODE_STATE != NodeState.LEADER:
        return
    
    if SUSPEND:
        return
    
    for node_id in SERVERS_INFO.keys():
        if node_id == NODE_ID:
            continue

        node_proxy = get_node_proxy(node_id)
        try:
            append_entries_request = pb2.AppendEntriesArgs(leader_term=CURRENT_TERM, leader_id=NODE_ID, committed_value=commited_value, uncommitted_value=uncommited_value)
            append_entries_response = node_proxy.AppendEntries(append_entries_request)
            if append_entries_response.heartbeat_result:
                count += 1
       
        except grpc.RpcError as e:
            continue
    
    if count >= len(SERVERS_INFO) // 2:
        commited_value = uncommited_value
        
    # Schedule the next heartbeat
    if NODE_STATE == NodeState.LEADER:
        timeout = APPEND_ENTRIES_TIMEOUT / 1000.0
        threading.Timer(timeout, append_entries).start()


# define the function to get the node proxy
def get_node_proxy(node_id):
    channel = grpc.insecure_channel(SERVERS_INFO[node_id])
    return pb2_grpc.RaftNodeStub(channel)

# request vote from the followers
def handle_request_vote(term):
    global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
    
    if term < CURRENT_TERM:
        return False
    
    if term == CURRENT_TERM:
        return not VOTED
    
    CURRENT_TERM = term
    NODE_STATE = NodeState.FOLLOWER
    VOTED = True
    
    return True

# Handler class to handle the RPCs
class Handler(pb2_grpc.RaftNodeServicer):
    def __init__(self):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        super().__init__()
        print(f"STATE: {NODE_STATE.name} | TERM: {CURRENT_TERM}")
        start_timer()


    def AppendEntries(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        
        if SUSPEND:
            context.set_details("Server suspended")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return pb2.AppendEntriesResponse()
        
        print(f'RPC[AppendEntries] Invoked')
        print(f'\tArgs:')
        print(f'\t\tleader_id: {request.leader_id}')
        print(f'\t\tleader_term: {request.leader_term}')
               
        if request.leader_term >= CURRENT_TERM:
            CURRENT_TERM = request.leader_term
            NODE_STATE = NodeState.FOLLOWER
            print(f"STATE: {NODE_STATE.name} | TERM: {CURRENT_TERM}")
            LeaderID = request.leader_id
            commited_value = request.committed_value
            uncommited_value = request.uncommitted_value
            reset_timer()
        
        heartbeat_result = True  # Acknowledge the heartbeat
        
        return pb2.AppendEntriesResponse(term=CURRENT_TERM, heartbeat_result=heartbeat_result)

    def RequestVote(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        
        if SUSPEND:
            context.set_details("Server suspended")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return pb2.RequestVoteResponse()
        
        print(f'RPC[RequestVote] Invoked')
        print(f'\tArgs:')
        print(f'\t\tcandidate_id: {request.candidate_id}')
        print(f'\t\tcandidate_term: {request.candidate_term}')
        vote_granted = handle_request_vote(request.candidate_term)
        if vote_granted:
            print(f"Voted for NODE {request.candidate_id}")
        print(f"STATE: {NODE_STATE.name} | TERM: {CURRENT_TERM}")
        reset_timer()
        return pb2.RequestVoteResponse(term=CURRENT_TERM, vote_result=vote_granted)


    def GetLeader(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        if SUSPEND:
            context.set_details("Server suspended")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return pb2.GetLeaderResponse()
        print(f'RPC[GetLeader] Invoked')
        return pb2.GetLeaderResponse(**{"leader_id": LeaderID})
       
        
    def AddValue(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        if SUSPEND:
            context.set_details("Server suspended")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return pb2.AddValueResponse()
        print(f'RPC[AddValue] Invoked')
        print(f'\tArgs:')
        print(f'\t\tvalue_to_add: {request.value_to_add}')
        
        if NODE_STATE != NodeState.LEADER:
            stub = get_node_proxy(LeaderID)
            response = stub.AddValue(request)
            return response
            
        uncommited_value += request.value_to_add
        
        return pb2.AddValueResponse(**{})
    
    def GetValue(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        if SUSPEND:
            context.set_details("Server suspended")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return pb2.GetValueResponse()
        print(f'RPC[GetValue] Invoked')
        
        global commited_value
        return pb2.GetValueResponse(**{"value": commited_value})

    def Suspend(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        print(f'RPC[Suspend] Invoked')
        SUSPEND = True
        NODE_STATE = NodeState.FOLLOWER
        LeaderID = None  
        stop_timer()
        return pb2.SuspendResponse(**{})
    
    def Resume(self, request, context):
        global NODE_ID, SERVERS_INFO, SUSPEND, NODE_STATE, CURRENT_TERM, commited_value, uncommited_value, timer, LeaderID, Votes, VOTED
        print(f'RPC[Resume] Invoked')
        SUSPEND = False
        return pb2.ResumeResponse(**{})

# ----------------------------- Do not change ----------------------------- 
def serve():
    print(f'NODE {NODE_ID} | {SERVERS_INFO[NODE_ID]}')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RaftNodeServicer_to_server(Handler(), server)
    server.add_insecure_port(SERVERS_INFO[NODE_ID])
    try:
        server.start()
        while True:
            server.wait_for_termination()
    except grpc.RpcError as e:
        print(f"Unexpected Error: {e}")
    except KeyboardInterrupt:
        server.stop(grace=10)
        print("Shutting Down...")


def init(node_id):
    global NODE_ID
    NODE_ID = node_id

    with open("config.conf") as f:
        global SERVERS_INFO
        lines = f.readlines()
        for line in lines:
            parts = line.split()
            id, address = parts[0], parts[1]
            SERVERS_INFO[int(id)] = str(address)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("node_id", type=int)
    args = parser.parse_args()

    init(args.node_id)

    serve()
# ----------------------------- Do not change -----------------------------
