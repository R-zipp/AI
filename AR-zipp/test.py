import multiprocessing
from multiprocessing import Queue

class BlenderProcess:
    def __init__(self):
        pass

    def run(self, data):
        # print(f"Processing data: {data}")
        
        return data+5


def process_wrapper(blender_process, data, queue):
    result = blender_process.run(data)
    queue.put(result)

if __name__ == "__main__":
    # 데이터 예시
    data_list = [1, 2, 3, 4, 5]

    
    queue = Queue()
    
    # 프로세스 목록 생성
    processes = []

    for data in data_list:
        blender_process = BlenderProcess()
        p = multiprocessing.Process(target=process_wrapper, args=(blender_process, data, queue))
        processes.append(p)
        p.start()
        print(p)

    # 모든 프로세스가 완료될 때까지 기다림
    for p in processes:
        p.join()
        
    results = [queue.get() for _ in processes]

    print("모든 프로세스가 완료되었습니다.")
    print("결과:", results)
