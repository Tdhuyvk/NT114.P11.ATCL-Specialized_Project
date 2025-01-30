import threading
import time
import random
import psutil  # Thư viện để lấy thông tin hệ thống
import pandas as pd  # Thư viện để ghi dữ liệu ra Excel
from datetime import datetime  # Time

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.state = "follower"  # Trạng thái của node: "follower", "candidate", hoặc "leader"
        self.current_term = 0  # Nhiệm kỳ hiện tại
        self.voted_for = None  # Node đã bầu cho ai trong nhiệm kỳ này
        self.election_timeout = random.uniform(0.15, 0.3)  # Thời gian Timeout ngẫu nhiên (0.15 - 0.3 giây)
        self.leader_id = None  # ID của leader hiện tại
        self.votes_received = 0  # Số phiếu nhận được
        self.alive = True  # Node có đang hoạt động không
        self.last_heartbeat_time = time.time()  # Thời điểm nhận heartbeat cuối cùng
        self.metrics = []  # Lưu thông tin thống kê

    def run(self):
        while self.alive:
            if self.state == "follower":
                self.follower_loop()
            elif self.state == "candidate":
                self.candidate_loop()
            elif self.state == "leader":
                self.leader_loop()

    def follower_loop(self):
        self.log_event("State", f"Node {self.node_id}: Đang là follower.")
        timeout_start = time.time()
        while time.time() - timeout_start < self.election_timeout:
            if time.time() - self.last_heartbeat_time > self.election_timeout:
                # Khi không nhận được heartbeat, bắt đầu bầu cử
                self.log_event("Election", f"Node {self.node_id}: Timeout, bắt đầu bầu cử.")
                self.state = "candidate"
                break
            time.sleep(0.1)

    def candidate_loop(self):
        self.current_term += 1
        self.votes_received = 1  # Bầu cho chính mình
        self.voted_for = self.node_id

        election_start_time = time.time()
        self.log_event("Candidate", f"Node {self.node_id}: Đang là candidate trong nhiệm kỳ {self.current_term}.")

        for node in nodes:
            if node.node_id != self.node_id:
                self.request_vote(node)

        time.sleep(1)  # Chờ nhận phiếu
        election_end_time = time.time()

        if self.votes_received > len(nodes) // 2:
            self.log_event("Leader", f"Node {self.node_id}: Trở thành leader trong nhiệm kỳ {self.current_term}.")
            self.state = "leader"
            self.leader_id = self.node_id
        else:
            self.log_event("Election", f"Node {self.node_id}: Không đắc cử, trở về follower.")
            self.state = "follower"

        # Ghi nhận thông số
        self.collect_metrics(election_start_time, election_end_time)

    def leader_loop(self):
        self.log_event("Heartbeat", f"Node {self.node_id}: Đang là leader, gửi heartbeat.")
        for node in nodes:
            if node.node_id != self.node_id:
                self.send_heartbeat(node)
        self.last_heartbeat_time = time.time()  # Cập nhật thời gian heartbeat
        time.sleep(2)  # Gửi heartbeat định kỳ

    def request_vote(self, other_node):
        if other_node.state == "follower" and (other_node.voted_for is None or other_node.voted_for == self.node_id):
            self.log_event("Vote", f"Node {self.node_id} nhận được phiếu từ Node {other_node.node_id}.")
            self.votes_received += 1
            other_node.voted_for = self.node_id

    def send_heartbeat(self, other_node):
        self.log_event("Heartbeat", f"Node {self.node_id} gửi heartbeat đến Node {other_node.node_id}.")
        other_node.last_heartbeat_time = time.time()  # Cập nhật thời gian nhận heartbeat của follower

    @staticmethod
    def log_event(event, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        print(f"{timestamp} Event={event} Message={message}")

    def collect_metrics(self, start_time, end_time):
        # Lấy thông tin CPU, RAM và Network
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        network_info = psutil.net_io_counters()

        self.metrics.append({
            "node_id": self.node_id,
            "term": self.current_term,
            "start_time": start_time,
            "end_time": end_time,
            "time_elected": end_time - start_time,  # Thời gian bầu chọn leader
            "cpu_percent": cpu_usage,
            "ram_used": memory_info.used,
            "network_in": network_info.bytes_recv,
            "network_out": network_info.bytes_sent,
        })

def simulate_raft(nodes):
    threads = []
    for node in nodes:
        t = threading.Thread(target=node.run)
        threads.append(t)
        t.start()

    time.sleep(12)  # Chạy mô phỏng trong 12 giây
    for node in nodes:
        node.alive = False

    for t in threads:
        t.join()

    # Xuất kết quả ra Excel
    export_to_excel(nodes)

def export_to_excel(nodes):
    all_metrics = []
    for node in nodes:
        all_metrics.extend(node.metrics)

    df = pd.DataFrame(all_metrics)
    df.to_excel("raft_metrics_9_node.xlsx", index=False)
    print("Kết quả đã được lưu vào file 'raft_metrics_9_node.xlsx'.")

if __name__ == "__main__":
    # Tạo 9 node
    nodes = [Node(node_id=i) for i in range(9)]
    simulate_raft(nodes)

