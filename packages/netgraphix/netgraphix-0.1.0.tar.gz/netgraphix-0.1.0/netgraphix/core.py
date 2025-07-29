import socket
import time
import psutil
import threading
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Style, init
from datetime import datetime
import random
import requests
from tqdm import tqdm
import pyfiglet
from tabulate import tabulate
import pandas as pd
from cpuinfo import get_cpu_info
import click
import socket
import time
import psutil
import threading
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Style, init
from datetime import datetime
import random
import requests
from tqdm import tqdm
import pyfiglet
from tabulate import tabulate
import pandas as pd
from cpuinfo import get_cpu_info
import click


init(autoreset=True)

class NetGraphix:
    def __init__(self):
        self.conn_history = []
        self.max_points = 100
        self.running = False

    def analyze_stats(self):
        if len(self.conn_history) < 5:
            print(Fore.YELLOW + "[!] Not enough data for analysis.")
            return

        data = np.array(self.conn_history)
        print(Fore.GREEN + "\n📊 Connection Stats (NumPy):")
        print(f"  Mean     : {np.mean(data):.2f}")
        print(f"  Std Dev  : {np.std(data):.2f}")
        print(f"  Max      : {np.max(data)}")
        print(f"  Min      : {np.min(data)}")
   

    def show_system_info(self):
        print(Fore.GREEN + "[i] Hostname:", socket.gethostname())
        try:
            ip = socket.gethostbyname(socket.gethostname())
            print(Fore.GREEN + f"[i] Local IP: {ip}")
        except:
            print(Fore.RED + "[!] Could not resolve local IP.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(Fore.BLUE + f"[i] Monitoring started at: {now}")
    

    def get_established_connections(self):
        return [conn for conn in psutil.net_connections() if conn.status == 'ESTABLISHED']

    def print_banner(self):
        banner = pyfiglet.figlet_format("NetGraphix")
        print(Fore.CYAN + banner + Style.RESET_ALL)

    def show_table(self, connections):
        data = []
        for conn in connections:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
            data.append([conn.pid, conn.status, laddr, raddr])
        print(Fore.YELLOW + tabulate(data, headers=["PID", "Status", "Local Addr", "Remote Addr"]))

    def log_connection_data(self):
        while self.running:
            conns = self.get_established_connections()
            self.conn_history.append(len(conns))
            if len(self.conn_history) > self.max_points:
                self.conn_history.pop(0)
            time.sleep(1)

    def export_dataframe(self, connections):
        rows = []
        for conn in connections:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
            rows.append({
                "PID": conn.pid,
                "Status": conn.status,
                "Local Address": laddr,
                "Remote Address": raddr
            })

        df = pd.DataFrame(rows)
        print(Fore.CYAN + "\n📘 Pandas DataFrame Preview:")
        print(df.head(5).to_string(index=False))
       

    def simulate_network_quality(self):
        loss = random.uniform(0, 5)  # 0% to 5% packet loss
        jitter = random.uniform(0, 50)  # 0ms to 50ms jitter
        print(Fore.MAGENTA + f"[~] Simulated Packet Loss: {loss:.2f}%")
        print(Fore.YELLOW + f"[~] Simulated Jitter: {jitter:.2f} ms")
        

    def plot_graph(self):
        plt.ion()
        fig, ax = plt.subplots()
        while self.running:
            ax.clear()
            ax.set_title("Active Network Connections")
            ax.plot(self.conn_history, color='blue')
            ax.set_xlabel("Time")
            ax.set_ylabel("Connections")
            ax.grid(True)
            plt.pause(1)

    def run(self):
        self.print_banner()
        self.show_system_info()
        cpu = get_cpu_info()['brand_raw']
        print(Fore.GREEN + f"[+] Running on CPU: {cpu}")
        print(Fore.MAGENTA + "[*] Tracking connections...")

        self.simulate_network_quality()  # ← Tambahkan ini

        self.running = True
        t1 = threading.Thread(target=self.log_connection_data)
        t2 = threading.Thread(target=self.plot_graph)
        t1.start()
        t2.start()

        try:
            while True:
                conns = self.get_established_connections()
                self.show_table(conns)
                self.export_dataframe(conns)
                self.analyze_stats()
                print(Fore.CYAN + f"[INFO] Total ESTABLISHED: {len(conns)}")
                time.sleep(5)
        except KeyboardInterrupt:
            self.running = False
            print(Fore.RED + "\n[!] Stopped by user.")
            t1.join()
            t2.join()
            




@click.command()
@click.option('--diagnostic', is_flag=True, help='Show network and system diagnostics')
def main(diagnostic):
    app = NetGraphix()
    if diagnostic:
        show_diagnostics()
    else:
        app.run()


def show_diagnostics():
    print(Fore.GREEN + "\n[+] System Diagnostics\n")
    print(Fore.CYAN + "CPU Info:")
    cpu_info = get_cpu_info()
    for k, v in cpu_info.items():
        print(f"  {k}: {v}")

    print(Fore.BLUE + "\nNetwork Interfaces:")
    interfaces = psutil.net_if_addrs()
    for iface, addrs in interfaces.items():
        print(f"  {iface}:")
        for addr in addrs:
            print(f"    {addr.family}: {addr.address}")

    print(Fore.MAGENTA + "\nChecking External IP...")
    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=5)
        print("  Public IP:", r.json().get('ip'))
    except Exception as e:
        print(Fore.RED + f"  Failed to fetch IP: {e}")

    print(Fore.YELLOW + "\nDownloading sample data (fake)...")
    for _ in tqdm(range(30), desc="Simulated Download"):
        time.sleep(0.05)

    print(Fore.GREEN + "\n[✔] Diagnostics complete.")


if __name__ == "__main__":
    main(standalone_mode=False)

