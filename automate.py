from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchWindowException
import tkinter as tk
from tkinter import messagebox
from tkinter import *
import threading
import os, inspect
import time
from random import randint
import requests
import platform
import socket
import uuid
import pickle
from cryptography.fernet import Fernet

ACTIVATION_STATUS = False
TRIAL_RUN_TIME = 0
YACT_ENC = None

if os.path.exists("yacfile"):
    pkl_file = open("yacfile", "rb")
    data = dict(pickle.load(pkl_file))
    yck = data.get("yck", "").decode("utf-8")[::-1]
    cipher_suite = Fernet(yck)
    status = cipher_suite.decrypt(data.get("ycs")).decode("utf-8")
    hardware_id = cipher_suite.decrypt(data.get("ycid")).decode("utf-8")
    if status == "activated" and hardware_id == str(uuid.getnode()):
        ACTIVATION_STATUS = True
    pkl_file.close()

if os.path.exists("yactfile"):
    pkl_file = open("yactfile", "rb")
    data = dict(pickle.load(pkl_file))
    yctk = data.get("yctk", "").decode("utf-8")[::-1]
    cipher_suite = Fernet(yctk)
    TRIAL_RUN_TIME = int((cipher_suite.decrypt(data.get("trt")).decode("utf-8")))
    YACT_ENC = yctk
    pkl_file.close()

root = tk.Tk()

dir_path = os.getcwd()
# Project Title Creation
projet_title = Label(text="YOUTUBE COMMENT LIKER", bg="WHITE")

# Channel Url Field Label
channel_url_label = Label(text="ENTER CHANNEL URL", bg="white")

# Channel Url Field Creation
channel_url_var = tk.StringVar()
channel_url_entry = tk.Entry(root, textvariable=channel_url_var, width=40, highlightcolor="black", highlightthickness=1)

# Activate Button
activate_button = tk.Button(root, text="ACTIVATE")

# VideoList Label
video_list_label = tk.Label(text="Video List")

# Video List
scrollbar = Scrollbar(root)
video_list = Listbox(root, selectmode=MULTIPLE)
video_list.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=video_list.yview)

# OutputBox Label
output_box_label = tk.Label(text="Program Output")

# Program Output Box
scrollbar = Scrollbar(root)
output_box = Listbox(root)
output_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_box.yview)

start_auto_like = tk.Button(root, text='Start Auto Like', bg="green", activebackground="#001C7C")

driver = None

SERVER_URL = "http://ytubecommentliker.com/api/api.php"


def delay(n, fixed=False):
    if fixed:
        time.sleep(n)
    else:
        time.sleep(randint(2, n))


def start_automation(re_initialize=False):
    try:
        global driver
        # Selenium Driver Initilization Work
        if os.path.isfile(os.path.join(dir_path, "chromedriver.exe")):
            chromedriver = os.path.join(dir_path, "chromedriver.exe")
        else:
            try:
                chromedriver = os.path.join(sys._MEIPASS, "chromedriver.exe")
            except:
                chromedriver = os.path.join(dir_path, "chromedriver.exe")
        if re_initialize or driver is None:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--mute-audio")
            driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_options)
        try:
            driver.get("https://www.youtube.com/")
        except NoSuchWindowException:
            start_automation(re_initialize=True)
        delay(5)
        # click SIGN IN button
        item = driver.find_element_by_css_selector("ytd-masthead div#buttons ytd-button-renderer a")
        item.click()
        driver.maximize_window()
        delay(5, fixed=True)
        while True:
            url = str(driver.current_url)
            if url.startswith("https://www.youtube"):
                driver.minimize_window()
                break
            else:
                delay(2)
    except Exception as ex:
        output_box.insert(END, str(ex))


def submit():
    channel_url = channel_url_var.get()
    if len(channel_url) == 0:
        messagebox.showerror("Required Field", "Please enter the channel url.")
        return
    if channel_url.endswith("/"):
        channel_url = channel_url + "videos"
    else:
        channel_url = channel_url + "/videos"

    th = threading.Thread(target=fetch_video_urls, args=(channel_url,))
    th.start()


def getpcname():
    n1 = platform.node()
    n2 = socket.gethostname()
    try:
        n3 = os.environ["COMPUTERNAME"]
    except:
        n3 = None
    if n3:
        return n3
    elif n2:
        return n2
    elif n1:
        return n1
    else:
        return ''


def get_computer_information():
    try:
        computer_name = getpcname()
        platform_info = platform.platform()
        os_info = str(platform.uname())
        return {"computer_name": computer_name, "platform_info": platform_info, "os_info": os_info,
                "hardware_id": uuid.getnode()}
    except Exception as ex:
        return {}


def save_activation_info(hardware_id):
    global ACTIVATION_STATUS
    ACTIVATION_STATUS = True
    try:
        hardware_id = str(hardware_id)
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        hardware_id = cipher_suite.encrypt(bytes(hardware_id, "utf8"))
        status = cipher_suite.encrypt(b'activated')
        activation_info = {'ycid': hardware_id, 'ycs': status, 'yck': key[::-1]}
        f = open("yacfile", "wb")
        pickle.dump(activation_info, f)
        f.close()
    except:
        pass


def request_server(serial_key, top):
    try:
        params = {"sn": serial_key, "requestType": "snActivation"}
        params.update(get_computer_information())
        response = requests.post(url=SERVER_URL, data=params)
        activate_button["state"] = "normal"
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("success", False):
                save_activation_info(params.get("hardware_id"))
                messagebox.showinfo("Success", response_json.get("message"))
                activate_button.destroy()
            else:
                messagebox.showerror("Error", response_json.get("message"))
        else:
            messagebox.showerror("Error", "Server returned: {}".format(str(response.reason)))
        top.destroy()
    except Exception as ex:
        activate_button["state"] = "normal"
        messagebox.showerror("Error", str(ex))


class ActivateWindow(object):
    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.serial_key = ''
        self.l = Label(top, text="Serial Key")
        self.l.grid(column=0, row=0, padx=10, pady=10)
        self.e = Entry(top, width=40)
        self.e.grid(column=1, row=0, padx=10, pady=10)
        self.b = Button(top, text='Ok', command=self.validate_serial_key, width=10)
        self.b.grid(column=1, row=2, padx=(0, 10))

    def validate_serial_key(self):
        self.serial_key = str(self.e.get())
        if len(self.serial_key) == 0:
            messagebox.showerror("Required Field", "Please enter the serial key.")
            return
        th = threading.Thread(target=request_server, args=(self.serial_key, self.top,))
        th.start()


def activate():
    w = ActivateWindow(root)
    activate_button["state"] = "disabled"
    root.wait_window(w.top)
    try:
        activate_button["state"] = "normal"
    except:
        pass


def create_initial_screen():
    row = 0
    projet_title.grid(column=1, row=row, sticky=N + S + W + E, padx=20, pady=10)
    if not ACTIVATION_STATUS:
        activate_button.grid(column=2, row=row, sticky=N + S + W + E, padx=20, pady=10)
        activate_button['command'] = lambda: activate()
    row += 1
    channel_url_label.grid(column=0, row=row, sticky=N + S + W + E, padx=20, pady=(20, 10))
    channel_url_entry.grid(column=1, row=row, sticky=N + S + W + E, pady=(20, 10))
    submit_button = tk.Button(root, text='IMPORT VIDEOS', bg="green", fg='white', activebackground="#001C7C")
    submit_button['command'] = lambda: submit()
    submit_button.grid(column=2, row=row, sticky=N + S + W + E, padx=20, pady=(20, 10))
    row += 1
    video_list.grid(column=0, row=row, sticky=N + S + W + E, rowspan=5, columnspan=2, padx=(20, 0), pady=(10, 20))
    output_box.grid(column=2, row=row, sticky=N + S + W + E, rowspan=6, padx=(0, 20), pady=(10, 20))
    start_auto_like.grid(column=0, row=7, sticky=N + S + W + E, pady=(0, 20), columnspan=2, padx=(20, 0))
    for r in range(7):
        root.grid_rowconfigure(row, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=2)
    # root.grid_columnconfigure(1, weight=2)


def save_increment_trial_run_time():
    global YACT_ENC, TRIAL_RUN_TIME
    TRIAL_RUN_TIME += 1
    if YACT_ENC is None:
        YACT_ENC = Fernet.generate_key()
    cipher_suite = Fernet(YACT_ENC)
    trt = cipher_suite.encrypt(bytes(str(TRIAL_RUN_TIME), "utf8"))
    data = {"trt": trt, "yctk": YACT_ENC[::-1]}
    f = open("yactfile", "wb")
    pickle.dump(data, f)
    f.close()


def start_like_process(videos_url):
    try:
        if TRIAL_RUN_TIME >= 3 and not ACTIVATION_STATUS:
            messagebox.showerror("Trial Version",
                                 "Please upgrade to pro version for unlimited auto likes. Please visit: {}".
                                 format("http://ytubecommentliker.com/activate"))
            return
        if not ACTIVATION_STATUS:
            save_increment_trial_run_time()
        try:
            driver.maximize_window()
        except NoSuchWindowException:
            start_automation(re_initialize=True)
        driver.set_window_position(0, 0)
        driver.set_window_size(400, 400)
        urls = [videos_url[idx] for idx in video_list.curselection()]
        for url in urls:
            like_count = 0
            output_box.insert(END, "Opening URL %s for auto like" % url)
            driver.get(url)
            delay(5)
            previous_buttons = []
            scroll_to = 3600
            driver.execute_script("window.scrollTo(0, %s);" % str(scroll_to))
            iter_check = 0
            while True:
                delay(5, fixed=True)
                buttons = driver.find_elements_by_xpath('//*[@id="like-button"]')
                for button in buttons:
                    try:
                        classes = button.get_attribute("class")
                        if "style-default-active" not in classes:
                            ActionChains(driver).move_to_element(button).click(button).perform()
                            like_count += 1
                            output_box.delete(END)
                            output_box.insert(END, "Like Count: {}".format(like_count))
                            delay(5)
                            if like_count >= 10 and not ACTIVATION_STATUS:
                                messagebox.showerror("Trial Version",
                                                    "Please upgrade to pro version for unlimited auto likes. Please visit: {}".
                                                    format("http://ytubecommentliker.com/activate"))
                                return
                        else:
                            ActionChains(driver).move_to_element(button).perform()
                    except Exception as ex:
                        pass
                if iter_check % 2 == 0 and previous_buttons == buttons:
                    break
                body = driver.find_element_by_tag_name('body')
                body.send_keys(Keys.END)
                previous_buttons = buttons
                iter_check += 1
            output_box.insert(END, "Process completed for URL %s" % url)
    except Exception as ex:
        output_box.insert(END, str(ex))


def start_auto_like_method(videos_url):
    th = threading.Thread(target=start_like_process, args=(videos_url,))
    th.start()


def stop_auto_like(th):
    th.stop()


def get_safe_text(text):
    char_list = [text[j] for j in range(len(text)) if ord(text[j]) in range(65536)]
    safe_text = ''
    for j in char_list:
        safe_text = safe_text + j
    return safe_text


def fetch_video_urls(channel_url):
    videos_url = []
    if TRIAL_RUN_TIME >= 3 and not ACTIVATION_STATUS:
        messagebox.showerror("Trial Version",
                             "Please upgrade to pro version for unlimited auto likes. Please visit: {}".
                             format("http://ytubecommentliker.com/activate"))
        return
    try:
        start_automation()
        output_box.insert(END, "Fetching Video URL for youtube channel: %s" % channel_url)
        driver.get(channel_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "video-title")))
        links = driver.find_elements_by_id("video-title")
        video_list.delete(0, END)
        for i, x in enumerate(links):
            text = get_safe_text(x.get_attribute("text"))
            href = get_safe_text(x.get_attribute("href"))
            videos_url.append(href)
            video_list.insert(END, str(i + 1) + ": " + text)
        output_box.insert(END, "Fetching Video Completed.")
    except Exception as ex:
        output_box.insert(END, str(ex))
    start_auto_like['command'] = lambda: start_auto_like_method(videos_url)


def on_closing():
    if messagebox.askokcancel("Exit", "Are you sure you want to quit?"):
        # os.system("taskkill /f /im  YoutubeAutomate.exe")
        root.destroy()
        try:
            driver.quit()
        except:
            pass
        sys.exit()


def main():
    try:
        # Set window size to 480x640
        root.geometry("800x500")
        # root.resizable(False, False)
        root.winfo_toplevel().title("YOUTUBE COMMENT LIKER")
        root["bg"] = "#ffffff"
        create_initial_screen()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except Exception as ex:
        output_box.insert(END, str(ex))


if __name__ == "__main__":
    main()
