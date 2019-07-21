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
projet_title = Label(text="Youtube Automation")


# Channel Url Field Label
channel_url_label = Label(text="Channel URL")

# Channel Url Field Creation
channel_url_var = tk.StringVar()
channel_url_entry = tk.Entry(root, textvariable=channel_url_var)


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
        chromedriver = os.path.join(dir_path, "chromedriver")
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
    projet_title.grid(column=0, row=row, sticky=N + S + W + E, columnspan=2)
    row += 1
    channel_url_label.grid(column=0, row=row, sticky=N + S + W + E)
    output_box_label.grid(column=1, row=row, sticky=N + S + W + E)
    row += 1
    channel_url_entry.grid(column=0, row=row, sticky=N + S + W + E)
    output_box.grid(column=1, row=row, sticky=N + S + W + E, rowspan=5)
    root.grid_rowconfigure(row, weight=1)
    row += 1
    # submit_button = tk.Button(root, text='Submit', bg="green", fg='white', activebackground="#001C7C")
    submit_button = tk.Button(root, text='Submit')
    submit_button['command'] = lambda: submit()
    submit_button.grid(column=0, row=row, sticky=N + S + W + E)
    row += 1
    video_list_label.grid(column=0, row=row, sticky=N + S + W + E)
    row += 1
    video_list.grid(column=0, row=row, sticky=N + S + W + E)
    root.grid_rowconfigure(row, weight=10)
    row += 1
    root.grid_columnconfigure(0, weight=4)
    root.grid_columnconfigure(1, weight=2)


def start_like_process(videos_url):
    try:
        driver.maximize_window()
        urls = [videos_url[idx] for idx in video_list.curselection()]
        for url in urls:
            like_count = 0
            output_box.insert(END, "Opning URL %s for auto like" % url)
            driver.get(url)
            delay(5)
            previous_buttons = []
            scroll_to = 600
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
                        else:
                            ActionChains(driver).move_to_element(button).perform()
                    except Exception as ex:
                        pass
                    delay(2, fixed=True)
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
    try:
        start_automation()
        output_box.insert(END, "Fetching Video URL for youtube channel: %s" % channel_url)
        driver.get(channel_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "video-title")))
        links = driver.find_elements_by_id("video-title")
        videos_url = []
        video_list.delete(0, END)
        for i, x in enumerate(links):
            text = x.get_attribute("text")
            href = x.get_attribute("href")
            videos_url.append(href)
            video_list.insert(END, str(i+1)+": "+text)
        # start_auto_like = tk.Button(root, text='Start Auto Like', bg="green", fg='white', activebackground="#001C7C")
        start_auto_like = tk.Button(root, text='Start Auto Like')
        start_auto_like['command'] = lambda: start_auto_like_method(videos_url)
        start_auto_like.grid(column=0, row=6, sticky=N + S + W + E)
        output_box.insert(END, "Fetching Video Completed.")
    except Exception as ex:
        output_box.insert(END, str(ex))


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
        root.geometry("1000x700")
        # root.resizable(False, False)
        root.winfo_toplevel().title("Youtube Automation")
        # root["bg"] = "#292B39"
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