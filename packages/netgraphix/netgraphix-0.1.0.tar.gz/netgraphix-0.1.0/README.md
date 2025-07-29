# NetGraphix

**NetGraphix** is a powerful real-time local network connection analyzer built in Python. It shows all active socket connections, live statistics using NumPy, colorful terminal output using Colorama, and interactive graphs via Matplotlib — all in one CLI tool.

![Banner](https://via.placeholder.com/800x200?text=NetGraphix) <!-- Replace with real if hosted -->

---

## 🔧 Installation

```bash
pip install netgraphix

Or clone and run:

git clone https://github.com/EdenGithhub/netgraphix
cd netgraphix
pip install .

## 🛠 Usages

🚀 Usage
Basic usage:

bash

python -m netgraphix.core
With diagnostics:


python -m netgraphix.core --diagnostic
Installed as CLI:

netgraphix --diagnostic

📘 Sample Output

  PID    Status        Local Addr        Remote Addr
  1234   ESTABLISHED   192.168.1.10:52000  142.250.4.110:443
  4567   ESTABLISHED   192.168.1.10:52001  104.244.42.1:443

[~] Simulated Packet Loss: 1.25%
[~] Simulated Jitter: 22.5 ms
📊 Connection Stats:
  Mean     : 5.42
  Std Dev  : 1.14
  Max      : 8
  Min      : 3

✅ Features
Real-time connection monitoring (via psutil)

NumPy-based connection statistics

Live graph plotting with matplotlib

Colorful CLI using colorama

Public IP detection via requests

System info (CPU, network interfaces)

Fancy terminal banners (pyfiglet)

CLI mode with click

Progress bars with tqdm

Tabulated connection info with tabulate and pandas

🧠 Requirements
Python 3.6+

Works on Windows (Linux/Mac support coming soon)

📜 License
MIT License © 2025 Adam Alcander et Eden

🌐 Author
Eden Simamora
    aeden6877@gmail.com
    Github = EdenGithhub