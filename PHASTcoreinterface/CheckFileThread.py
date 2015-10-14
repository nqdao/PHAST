import json, os, subprocess, threading


class CheckFileThread(threading.Thread):
    def __init__(self, file_check_callback):
        threading.Thread.__init__(self)
        self.file_check_callback = file_check_callback

    def run(self):
        self.file_check_callback()