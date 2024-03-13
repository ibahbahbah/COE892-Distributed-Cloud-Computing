import hashlib, logging, sys, requests, os, json, random, string
import numpy as np
import grpc, rovers_pb2, rovers_pb2_grpc
from concurrent import futures

global path 
path = "./paths"

# Compute the hashed key using sha256
def key(pin: str, serial: str) -> str:

    # Concatenate strings (Temporary Key)
    tmpkey = pin + serial

    # Hash Temporary Key
    h = hashlib.sha256()
    h.update(tmpkey.encode())

    # Hashed value
    hashkey = h.hexdigest()

    return hashkey

# Brute Forces to find a valid pin for the given serial number
def validpin(serialnum, n=500000) -> bool:

    logging.info(f'ValidPin\t: Mine Serial Number = {serialnum}')

    # Brute force arbitrary pins
    for i in range(n):
        # Select a random 6 digit number
        pin = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        logging.debug(f'Temporary Key\t= {pin} {serialnum}')

        # Hash Temporary key
        val = key(pin, serialnum)
        logging.debug(f'Hashed Key[0:5]\t= {val[0:5]}')

        # Check if hash has at least five leading zeros
        if (val[0:4] == "0000"):
            logging.info(f'ValidPin\t: Valid Pin = {pin}')

            # Alert ground control of valid pin
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = rovers_pb2_grpc.roversStub(channel)
                response = stub.sendPin(rovers_pb2.pinRequest(id=id, serialNum=serialnum, pin=pin))

            return True

    logging.info(f'ValidPin\t: Valid Pin not found')
    return False

# Rover Pathing Program
def run(id : str, cmd: str, rows: int, cols: int, matrix):
    logging.info(f'Rover {id}\t: Running rover...')

    # Rover Variables
    onMine  : bool  = False
    facing  : str   = "DOWN"
    cur_i   : int   = 0
    cur_j   : int   = 0

    # Initialize rover position
    matrix[0][0] = id

    # Other Variables
    index   : int   = 0
    running : bool  = True
    
    while (running):

        # print(f"i = {cur_i}, j = {cur_j}, facing = {facing}")
        # for row in range(rows):
        #     print(matrix[row])
        # print('-----------------------')

        if (onMine == True and cmd[index] != "D"):
            logging.info(f'Rover {id}\t: Command ({cmd[index]}) -- Rover did not dig mine: closing')
            matrix[cur_i][cur_j] = "x"

            # Alert Ground control, failed to defuse
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = rovers_pb2_grpc.roversStub(channel)
                response = stub.completedCommands(rovers_pb2.completedRequest(id=id, code=1))

            running = False
        else:
            try: 
                match cmd[index]:
                    case 'R':
                        # Turn rover to the right
                        logging.info(f'Rover {id}\t: Command ({cmd[index]}) = Turn right')
                        if (facing == "DOWN"):
                            facing = "LEFT"
                        elif (facing == "LEFT"):
                            facing = "UP"
                        elif (facing == "UP"):
                            facing = "RIGHT"
                        elif (facing == "RIGHT"):
                            facing = "DOWN"
                    case 'L':
                        # Turn rover to the left
                        logging.info(f'Rover {id}\t: Command ({cmd[index]}) = Turn left')
                        if (facing == "DOWN"):
                            facing = "RIGHT"
                        elif (facing == "RIGHT"):
                            facing = "UP"
                        elif (facing == "UP"):
                            facing = "LEFT"
                        elif (facing == "LEFT"):
                            facing = "DOWN"
                    case 'M':
                        # Move rover forward 1 space
                        logging.info(f'Rover {id}\t: Command ({cmd[index]}): Move forward')
                        matrix[cur_i][cur_j] = "*"  # Set trail on map

                        # Change Rover Position
                        if ((facing == "DOWN") and (0 <= cur_i + 1 < rows)):
                            cur_i += 1
                        elif ((facing == "RIGHT") and (0 <= cur_j + 1 < cols)):
                            cur_j += 1
                        elif ((facing == "UP") and (0 <= cur_i - 1 < rows)):
                            cur_i -= 1
                        elif ((facing == "LEFT")  and (0 <= cur_j - 1 < cols)):
                            cur_j -= 1

                        # Check if rover is on a mine (1)
                        if (matrix[cur_i][cur_j] == "1"):
                            logging.info(f'Rover {id}\t: Rover is currently on a mine!')
                            onMine = True
                        matrix[cur_i][cur_j] = id   # Set rover on map 
                    case 'D':
                        logging.info(f'Rover {id}\t: Command ({cmd[index]}): Dig')
                        if (onMine == True):
                            # Request mine serial number and disarm
                            with grpc.insecure_channel('localhost:50051') as channel:
                                stub = rovers_pb2_grpc.roversStub(channel)
                                response = stub.getMineSerial(rovers_pb2.serialNumRequest(id=id, i=cur_i, j=cur_j))
                            if (validpin(response.serialNum)):
                                logging.info(f'Rover {id}\t: Successfully disarmed mine')
                                onMine = False
                            else:
                                logging.info(f'Rover {id}\t: Rover did not disarm mine: closing')
                                matrix[cur_i][cur_j] = "X"

                                # Alert Ground control, failed to defuse
                                with grpc.insecure_channel('localhost:50051') as channel:
                                    stub = rovers_pb2_grpc.roversStub(channel)
                                    response = stub.completedCommands(rovers_pb2.completedRequest(id=id, code=2))

                                running = False
                    case _:
                        pass
                index += 1
            except IndexError:
                logging.info(f'Rover {id}\t: All Commands executed : closing')

                # Alert Ground control, completed commands
                with grpc.insecure_channel('localhost:50051') as channel:
                    stub = rovers_pb2_grpc.roversStub(channel)
                    response = stub.completedCommands(rovers_pb2.completedRequest(id=id, code=0))


                running = False
    
    # Save Rover Path
    np.savetxt(f'{path}/path_{id}.txt', matrix, fmt='%s')

def main() -> int:
    global id 

    # CLI Rover Number
    id = input("Enter rover number: ")

    logging.info(f'Rover {id}\t: Setting up rover...')

    # Retrive Map
    logging.info(f'Rover {id}\t: Retriving map...')

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = rovers_pb2_grpc.roversStub(channel)
        response = stub.getMap(rovers_pb2.mapRequest(id=id))
    matrix = np.array(response.map, dtype='U21').reshape(response.rows, response.cols)
    rows = response.rows
    cols = response.cols

    logging.info(f'Rover {id}\t: rows = {response.rows}, cols = {response.cols}')
    logging.info(f'Rover {id}\t: map_list = {response.map}')


    # Get Commands
    logging.info(f'Rover {id}\t: Retriving commands...')

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = rovers_pb2_grpc.roversStub(channel)
        response = stub.getCommandStream(rovers_pb2.commandStreamRequest(id=id))
    cmd = response.cmds

    logging.debug(f'Rover {id}\t: cmds = {response.cmds}')

    # Create paths subfolder if not exists
    os.makedirs(path, exist_ok=True)

    # Run Program
    print("")
    run(id=id, cmd=cmd, rows=rows, cols=cols, matrix=matrix)

    logging.info(f'Rover {id}\t: closing rover...')
    return 0

if __name__ == '__main__':
    FORMAT = "%(asctime)s: %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt="%H:%M:%S")
    logging.disable(logging.DEBUG)
    sys.exit(main())