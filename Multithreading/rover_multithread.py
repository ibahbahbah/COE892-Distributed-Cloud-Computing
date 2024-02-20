import sys, requests, json, os, logging, time, pathing
import numpy as np
from threading import Thread

class RoverThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # super(): Gives access to methods/properties of a parent class
        self.start_time = None
        self.end_time = None
        self.duration = None

    def run(self):
        self.start_time = time.time()
        super().run() # 
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

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
    path = "./paths_threaded"
    os.makedirs(path, exist_ok=True)

    threads = []
    for i in range(1, 11):
        # Temporary matrix
        matrix0 = np.copy(matrix)

        # Get data from URL
        res = requests.get(f'https://coe892.reev.dev/lab1/rover/{i}')
        
        # Parse json data
        cmd = json.loads(f'{res.text}')["data"]["moves"]

        # Create and start thread [run(...) in pathing.py]
        logging.info(f'Main\t\t: Creating Thread {i}')
        x = RoverThread(target=pathing.run, name=f'rover {i}', args=(i, cmd, rows, cols, matrix0, path))
        threads.append(x)
        x.start()
    
    for i, thread in enumerate(threads):
        thread.join()   # Wait until all running threads are done
        logging.info(f'Main\t\t: Thread {i+1} completed in {np.round(thread.duration, 5)} seconds')

    return 0

if __name__ == '__main__':
    FORMAT = "%(asctime)s: %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%H:%M:%S")
    sys.exit(main())