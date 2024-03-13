import logging, sys, requests, json
import numpy as np
import grpc, rovers_pb2, rovers_pb2_grpc
from concurrent import futures

class groundController(rovers_pb2_grpc.roversServicer):
    # Retrieves  map data from map.txt file
    def getMap(self, request, context):
        logging.info(f'Ground Control <- Rover {request.id}\t: Map Request...')

        # Retrieve map info from map.txt
        with open("map.txt", "r") as file:
            rows, cols = map(int, file.readline().split())
            matrix = np.empty((rows, cols), dtype='U21')
            for i in range(rows):
                row = list(map(int, file.readline().split()))
                matrix[i] = row

        # Convert array to string stream (list)
        matrix_list = matrix.flatten().tolist()
        
        logging.info(f'Ground Control -> Rover {request.id}\t: Sending map={matrix_list}')
        return rovers_pb2.mapReply(map=matrix_list, rows=rows, cols=cols)
    
    # Retrieve commands string from API
    def getCommandStream(self, request, context):
        logging.info(f'Ground Control <- Rover {request.id}\t: Command Request...')

        # Get data from URL
        res = requests.get(f'https://coe892.reev.dev/lab1/rover/{request.id}')
        
        # Parse json data
        cmds = json.loads(f'{res.text}')["data"]["moves"]

        logging.info(f'Ground Control -> Rover {request.id}\t: Sending CMD={cmds}')
        return rovers_pb2.commandStreamReply(cmds=cmds)
    
    # Retrieves mines serial number at given coordinates (mines.txt)
    def getMineSerial(self, request, context):
        logging.info(f'Ground Control <- Rover {request.id}\t: Serial Request - i={request.i}, j={request.j}')

        # Initialize  mines serial numbers
        with open("mines.txt", "r") as f:
            json_data : dict = json.load(f)

        for serial, location in json_data.items():
            if (location == [request.i, request.j]):
                logging.info(f'Ground Control -> Rover {request.id}\t: Sending serial={serial}')
                return rovers_pb2.serialNumReply(serialNum=serial)
    
    # Rover completion alert
    def completedCommands(self, request, context):
        if (request.code == 0):
            logging.info(f'Ground Control\t: rover {request.id} has succesfully executed all commands')
        elif (request.code == 1):
            logging.info(f'Ground Control\t: rover {request.id} failed to dig a mine')
        elif (request.code == 2):
            logging.info(f'Ground Control\t: rover {request.id} failed to defuse a mine')
        return rovers_pb2.completedReply(ack="ACK")
    
    # Rover valid pin found alert
    def sendPin(self, request, context):
        logging.info(f'Ground Control\t: rover {request.id} has found valid pin ({request.pin}) for serial num -> {request.serialNum}')
        return rovers_pb2.pinReply(ack="ACK")


def serve() -> int: 
    logging.info("Ground Control\t: Starting server......")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rovers_pb2_grpc.add_roversServicer_to_server(groundController(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info(f"Ground Control\t: Server running")
    server.wait_for_termination()
    return 0


if __name__ == '__main__':
    FORMAT = "%(asctime)s: %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%H:%M:%S")
    logging.disable(logging.DEBUG)
    sys.exit(serve())