from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchWindowException
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import threading
import os, inspect
import time
from random import randint

root = tk.Tk()

dir_path = "/".join(sys.argv[0].split("/")[:-1])
if not dir_path:
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


def delay(n, fixed=False):
    if fixed:
        time.sleep(n)
    else:
        time.sleep(randint(2, n))

def start_automation(re_initialize=False):
    try:
        global driver
        # Selenium Driver Initilization Work
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
        import traceback
        traceback.print_exc()
        print(str(ex))


def submit():
    channel_url = channel_url_var.get()
    if len(channel_url) == 0:
        messagebox.showerror("Required Field", "Please enter the channel url.")
        return
    if channel_url.endswith("/"):
        channel_url = channel_url+"videos"
    else:
        channel_url = channel_url+"/videos"

    th = threading.Thread(target=fetch_video_urls, args=(channel_url,))
    th.start()


def create_initial_screen():
    row = 0
    projet_title.grid(column=1, row=row, sticky=N + S + W + E, padx=20, pady=10)
    activate_button.grid(column=2, row=row, sticky=N + S + W + E, padx=20, pady=10)
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


def start_like_process(videos_url):
    try:
        driver.maximize_window()
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
            output_box.insert(END, "Process completed for URL %s" %url)
    except Exception as ex:
        output_box.insert(END, str(ex))


def start_auto_like_method(videos_url):
    th = threading.Thread(target=start_like_process, args=(videos_url,))
    th.start()


def stop_auto_like(th):
    th.stop()


def fetch_video_urls(channel_url):
    videos_url = []
    try:
        start_automation()
        output_box.insert(END, "Fetching Video URL for youtube channel: %s" % channel_url)
        driver.get(channel_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "video-title")))
        links = driver.find_elements_by_id("video-title")
        video_list.delete(0, END)
        for i, x in enumerate(links):
            text = x.get_attribute("text")
            href = x.get_attribute("href")
            videos_url.append(href)
            video_list.insert(END, str(i+1)+": "+text)
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
        import traceback
        traceback.print_exc()
        print(str(ex))
        output_box.insert(END, str(ex))


if __name__ == "__main__":
    main()
