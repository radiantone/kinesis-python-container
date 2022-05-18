import multiprocessing
from dotenv import load_dotenv
load_dotenv()

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
