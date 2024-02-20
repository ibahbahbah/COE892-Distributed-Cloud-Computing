import hashlib, logging, sys, requests, os, json, random, string
import numpy as np

def key(pin: str, serial: str) -> str:

    # Concatenate strings (Temporary Key)
    tmpkey = pin + serial

    # Hash Temporary Key
    h = hashlib.sha256()
    h.update(tmpkey.encode())

    # Hashed value
    hashkey = h.hexdigest()

    return hashkey

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
        if (val[0:5] == "00000"):
            logging.info(f'ValidPin\t: Valid Pin = {pin}')
            return True

    logging.info(f'ValidPin\t: Valid Pin not found')
    return False

# Rover Pathing Calculation
def run(id: int, cmd: str, rows: int, cols: int, matrix, path: str):
    logging.info(f'Rover {id}\t: Running rover')

    # Rover Variables
    onMine = False
    facing = "DOWN"
    cur_i = 0
    cur_j = 0

    # Initialize rover position
    matrix[0][0] = id

    # Other Variables
    index = 0
    running = True

    # Initilize mines serial numbers
    with open("mines.txt", "r") as f:
        json_data: dict = json.load(f)
    
    
    while (running):

        # print(f"i = {cur_i}, j = {cur_j}, facing = {facing}")
        # for row in range(rows):
        #     print(matrix[row])
        # print('-----------------------')

        if (onMine == True and cmd[index] != "D"):
            logging.info(f'Rover {id}\t: Command ({cmd[index]}) -- Rover did not dig mine: closing')
            matrix[cur_i][cur_j] = "x"
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
                            # Find mine serial number and disarm
                            for serial, location in json_data.items():
                                if (location == [cur_i, cur_j]):
                                    if (validpin(serial)):
                                        logging.info(f'Rover {id}\t: Successfully disarmed mine')
                                        onMine = False
                                    else:
                                        logging.info(f'Rover {id}\t: Rover did not disarm mine: closing')
                                        matrix[cur_i][cur_j] = "X"
                                        running = False
                    case _:
                        pass
                index += 1
            except IndexError:
                logging.info(f'Rover {id}\t: All Commands executed : closing')
                running = False
    
    # Save Rover Path
    np.savetxt(f'{path}/path_{id}.txt', matrix, fmt='%s')

def main():
    id = 2
    path = "./paths_serial_testing"

    # Retrieve map info from map.txt
    with open("map.txt", "r") as file:
        rows, cols = map(int, file.readline().split())
        matrix = np.empty((rows, cols), dtype='U21')
        for i in range(rows):
            row = list(map(int, file.readline().split()))
            matrix[i] = row

    # Initilize mines serials and location
    mines: dict = {}
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == '1':
                # Select arbitrary serial number
                serialnum = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                mines[serialnum] = [i, j]   # Assign serial to mines location
                
    # Save to temporary file
    with open("mines.txt", "w") as f:
        f.write(json.dumps(mines, indent=4))

    # Create paths subfolder if not exists
    os.makedirs(path, exist_ok=True)

    # Get data from URL
    res = requests.get(f'https://coe892.reev.dev/lab1/rover/{id}')

    # Parse json data
    cmd = json.loads(f'{res.text}')["data"]["moves"]

    # Run rover program
    run(id, cmd, rows, cols, matrix, path)

if __name__ == '__main__':
    FORMAT = "%(asctime)s: %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%H:%M:%S")
    logging.disable(logging.DEBUG)
    sys.exit(main())