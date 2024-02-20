import time, unittest
import numpy as np
import rover_serial_sequential as rs
import rover_serial_multithread as rt

class TestPath(unittest.TestCase):
    def test_runtimes(self):     # Compare Runtimes
        # Test Sequential Runtime
        start = time.time()
        rs.main()
        end = time.time()
        rs_time = np.round((end - start), 4)

        # Test Threaded Runtime
        start = time.time()
        rt.main()
        end = time.time()
        rt_time = np.round((end - start), 4)

        msg = f'Sequential time: {rs_time}\nMulti-Threaded time: {rt_time}'
        print(msg)

        # Test Multi-Threading faster then Sequential
        self.assertLess(rt_time, rs_time)
    

if __name__ == "__main__":
    unittest.main()