import grpc
import sys
import zlib
from concurrent import futures
import chord_pb2_grpc as pb2_grpc
import chord_pb2 as pb2

node_index = int(sys.argv[1])

CHORD = [0, 2, 16, 24, 25, 26, 31]

CHANNELS = [
    "127.0.0.1:5000",
    "127.0.0.1:5001",
    "127.0.0.1:5002",
    "127.0.0.1:5003",
    "127.0.0.1:5004",
    "127.0.0.1:5005",
    "127.0.0.1:5006",
]

data = {}
finger_table = []

M = 5
id = CHORD[node_index]
succ = CHORD[(node_index + 1) % len(CHORD)]
pred = CHORD[(node_index - 1 + len(CHORD)) % len(CHORD)]

def find_successor(target):
        for node_id in CHORD:
            if node_id >= target:
                return node_id
        return CHORD[0]
    
def find_predecessor(target):
    for i in range(len(CHORD)-1, -1, -1):
        if CHORD[i] < target:
            return CHORD[i]
    return CHORD[-1]

def populate_finger_table(id): 
    for i in range(M):
        start = (id + 2**i) % (2**M)
        finger_table.append(find_successor(start))
    print(f"Node {id}\t finger table {finger_table}")
    return finger_table

def get_stub(channel):
    channel = grpc.insecure_channel(channel)
    return pb2_grpc.ChordStub(channel)

def get_target_id(key):
    hash_value = zlib.adler32(key.encode())
    target_id = hash_value % (2**M)
    return target_id

def save(key, text):
    target_id = get_target_id(key)
    if pred < target_id <= id or (id == min(CHORD) and target_id <= id) or (id == min(CHORD) and pred < target_id):
        data[target_id] = text
        print(f"Node {id} says: Saved {key}")
        return id, target_id
    elif id < target_id <= succ or (succ == min(CHORD) and id < target_id) or (succ == min(CHORD) and target_id > max(CHORD)):
        # Forward the save request to the successor node
        succ_stub = get_stub(CHANNELS[CHORD.index(succ)])
        print(f"Node {id} says: Save from {id} to {succ}")
        res = succ_stub.SaveData(pb2.SaveDataMessage(key=key, text=text))
        return res.node_id, target_id
    else:
        # Find the node in the finger table that satisfies FT[j] <= target_id < FT[j + 1]
        for i in range(len(finger_table) - 1):
            if finger_table[i] <= target_id < finger_table[i + 1]:
                node_id = finger_table[i]
                break
        else:
            # Handle the wrap-around case
            if target_id < min(finger_table):
                node_id = max(finger_table)
            else:
                node_id = min((node for node in finger_table if node > target_id), default=max(finger_table))
            
        print(f"Node {id} says: Save from {id} to {node_id}")
        # Forward the save request to the node in the finger table
        node_stub = get_stub(CHANNELS[CHORD.index(node_id)])
        res = node_stub.SaveData(pb2.SaveDataMessage(key=key, text=text))
        return res.node_id, target_id

def remove(key):
    target_id = get_target_id(key)
    if pred < target_id <= id or (id == min(CHORD) and target_id <= id) or (id == min(CHORD) and pred < target_id):
        del data[target_id]
        print(f"Node {id} says: Removed {key}")
        return id, target_id
    elif id < target_id <= succ or (succ == min(CHORD) and id < target_id) or (succ == min(CHORD) and target_id > max(CHORD)):
        # Forward the remove request to the successor node
        succ_stub = get_stub(CHANNELS[CHORD.index(succ)])
        print(f"Node {id} says: Remove from {id} to {succ}")
        res = succ_stub.RemoveData(pb2.RemoveDataMessage(key=key))
        return res.node_id, target_id
    else:
        # Find the node in the finger table that satisfies FT[j] <= target_id < FT[j + 1]
        for i in range(len(finger_table) - 1):
            if finger_table[i] <= target_id < finger_table[i + 1]:
                node_id = finger_table[i]
                break
        else:
            # Handle the wrap-around case
            if target_id < min(finger_table):
                node_id = max(finger_table)
            else:
                node_id = min((node for node in finger_table if node > target_id), default=max(finger_table))
        
        print(f"Node {id} says: Remove from {id} to {node_id}")
        # Forward the remove request to the node in the finger table
        node_stub = get_stub(CHANNELS[CHORD.index(node_id)])
        res = node_stub.RemoveData(pb2.RemoveDataMessage(key=key))
        return res.node_id, target_id

def find(key):
    target_id = get_target_id(key)
    if pred < target_id <= id or (id == min(CHORD) and target_id <= id) or (id == min(CHORD) and pred < target_id):
        print(f"Node {id} says: Found {key}")
        return id, data.get(target_id)
    elif id < target_id <= succ or (succ == min(CHORD) and id < target_id) or (succ == min(CHORD) and target_id > max(CHORD)):
        # Forward the find request to the successor node
        succ_stub = get_stub(CHANNELS[CHORD.index(succ)])
        print(f"Node {id} says: Find from {id} to {succ}")
        res = succ_stub.FindData(pb2.FindDataMessage(key=key))
        return res.node_id, res.data
    else:
        # Find the node in the finger table that satisfies FT[j] <= target_id < FT[j + 1]
        for i in range(len(finger_table) - 1):
            if finger_table[i] <= target_id < finger_table[i + 1]:
                node_id = finger_table[i]
                break
        else:
            # Handle the wrap-around case
            if target_id < min(finger_table):
                node_id = max(finger_table)
            else:
                node_id = min((node for node in finger_table if node > target_id), default=max(finger_table))
        
        print(f"Node {id} says: Find from {id} to {node_id}")
        # Forward the find request to the node in the finger table
        node_stub = get_stub(CHANNELS[CHORD.index(node_id)])
        res = node_stub.FindData(pb2.FindDataMessage(key=key))
        return res.node_id, res.data
    
class NodeHandler(pb2_grpc.ChordServicer):
    def SaveData(self, request, context):
        node_id, key = save(request.key, request.text)
        return pb2.DataResponse(status=node_id!=-1, node_id=node_id, key=key)

    def RemoveData(self, request, context):
        node_id, key = remove(request.key)
        return pb2.DataResponse(status=node_id!=-1, node_id=node_id)

    def FindData(self, request, context):
        node_id, text = find(request.key)
        return pb2.FindDataResponse(data=text, node_id=node_id)

    def GetFingerTable(self, request, context):
        return pb2.FingerTableResponse(finger_table=finger_table)

if __name__ == "__main__":
    populate_finger_table(id)
    node_port = str(5000 + node_index)
    node = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ChordServicer_to_server(NodeHandler(), node)
    node.add_insecure_port("127.0.0.1:" + node_port)
    node.start()

    try:
        node.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down")