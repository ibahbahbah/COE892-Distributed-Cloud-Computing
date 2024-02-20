import requests, json, os, time, logging, sys, pathing_serial
import numpy as np
   
def main() -> int:
    # # Disable loggings
    # if len(sys.argv) > 1 and sys.argv[1] == 'test':
    #     logging.disable(logging.CRITICAL)

    # Retrieve map info from map.txt
    with open("map.txt", "r") as file:
        rows, cols = map(int, file.readline().split())
        matrix = np.empty((rows, cols), dtype='U21')
        for i in range(rows):
            row = list(map(int, file.readline().split()))
            matrix[i] = row

    # Create paths subfolder if not exists
    path = "./paths_sequential"
    os.makedirs(path, exist_ok=True)

    for i in range(1, 11):
        # Temporary matrix (initialize map)
        matrix0 = np.copy(matrix)

        # Get data from URL
        res = requests.get(f'https://coe892.reev.dev/lab1/rover/{i}')
        
        # Parse json data
        cmd = json.loads(f'{res.text}')["data"]["moves"]
        
        # Run rover program [run(...) in pathing.py]
        pathing_serial.run(i, cmd, rows, cols, matrix0, path)

    return 0

if __name__ == '__main__':
    FORMAT = "%(asctime)s: %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%H:%M:%S")
    sys.exit(main())