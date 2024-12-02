import threading
import subprocess

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    detection_script = threading.Thread(target=run_script, args=("ALPR/detect.py",))
    db_save_script = threading.Thread(target=run_script, args=("ALPR/save.py",))

    detection_script.start()
    db_save_script.start()

    detection_script.join()
    db_save_script.join()

    print("Both scripts have finished executing.")