import tkinter as tk

import sys

import sounddevice as sd
import soundfile
import pynput


import array


from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk



height = 10
width = 100

single_height = 1
single_width = 60

sample_rate = 44100

difort_divice = "Voicemeeter AUX Input (VB-Audio Voicemeeter VAIO)"


class MyException(Exception):
    """
    自定义的异常类
    """

    def __init__(self, *args):
        self.args = args


class controler:

    def __init__(self, device: str = difort_divice):
        self.isplay = False
        self.device = device
        self.device_id = self.get_output_device_id_by_name(device)
        self.volme = 1.0
        self.loop = False

    def changevol(self, vol):
        self.volme = float(vol) / 100

    def preliminary_instruction(self):
        devices_list = sd.query_devices()
        return [i["name"] for i in devices_list]

    def preliminary_instruction_output(self):
        result = list()
        devices_list = sd.query_devices()
        for index, device_msg_dict in enumerate(devices_list):
            if device_msg_dict["max_output_channels"] > 0:
                result.append(device_msg_dict["name"])
        return result

    def get_device_obj_by_id(self, id):
        devices_list = sd.query_devices()
        for index, device_msg_dict in enumerate(devices_list):
            if id == index:
                print("找到设备：", index, id, device_msg_dict["name"])
                return device_msg_dict
        else:
            raise MyException("找不到该设备!!!")

    def get_input_device_id_by_name(self, channel_name):

        devices_list = sd.query_devices()
        for index, device_msg_dict in enumerate(devices_list):
            if (
                channel_name == device_msg_dict["name"]
                and device_msg_dict["max_input_channels"] > 0
            ):
                print("找到设备：", index, channel_name)
                return index
        else:
            raise MyException("找不到该设备!!!")

    def get_output_device_id_by_name(self, channel_name):
        devices_list = sd.query_devices()
        for index, device_msg_dict in enumerate(devices_list):
            if (
                channel_name == device_msg_dict["name"]
                and device_msg_dict["max_output_channels"] > 0
            ):
                print("找到设备：", index, device_msg_dict["name"])
                return index
        else:
            raise MyException("找不到该设备!!!")

    def read_data(self, audio_file_path, audio_channels):
        if audio_file_path.endswith(".wav") or audio_file_path.endswith(".WAV"):
            data_array, sample_rate = soundfile.read(audio_file_path, dtype="float32")
            return data_array * self.volme
        elif audio_file_path.endswith(".pcm") or audio_file_path.endswith(".raw"):
            data_array = array.array("h")
            with open(audio_file_path, "rb") as f:
                data_array.frombytes(f.read())
            data_array = data_array[::audio_channels]
            return data_array

    def play_audio_files(
        self, audio_file_path, channel_id, audio_channels=2, sample_rate=sample_rate
    ):
        try:
            if self.isplay == False:
                sd.default.device[1] = channel_id
                self.isplay = True
                data_array = self.read_data(audio_file_path, audio_channels)
                k = sd.play(data_array, sample_rate, loop=self.loop)
                self.isplay = False
            else:
                raise RuntimeError

        except sd.PortAudioError:
            print("端口出错")
            raise RuntimeError

    def play(self, path):
        self.play_audio_files(audio_file_path=path, channel_id=self.device_id)

    def busy(self):
        return self.isplay

    def changedevice(self, device):
        self.device = device
        self.device_id = self.get_output_device_id_by_name(device)

    def stop(self):
        if self.isplay:
            sd.stop()
            self.isplay = False
        else:
            try:
                sd.stop()
            except:
                messagebox.showerror("", "stop error")


class single:

    def __init__(self, top, path, gui):
        self.gui = gui
        self.frame = tk.Frame(top)
        self.button_start = tk.Button(
            self.frame, text="o", height=single_height, command=self.add_or_play
        )
        self.text = tk.Text(self.frame, height=single_height, width=single_width)
        self.text.insert("insert", str(path))
        self.button_stop = tk.Button(
            self.frame, text="x", height=single_height, command=self.stop_or_die
        )
        self.button_start.pack(side="left")
        self.text.pack(side="left", expand=True, fill="x")
        self.button_stop.pack(side="right")
        self.frame.pack(side="top", expand=True, fill="x")

    def getpath(self):
        return self.text.get("1.0", tk.END).strip()

    def choosefile(self):
        p = filedialog.askopenfilename()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", p)

    def play(self, path):
        try:
            self.gui.control.play(path)
            self.button_stop.config(bg="red")
        except:
            messagebox.showwarning("error", "cant paly")
            raise

    def add_or_play(self):
        p = self.getpath()
        if p:
            self.play(p)
        else:
            self.choosefile()

    def stop(self):
        self.gui.control.stop()
        self.button_stop.configure(bg="white")

    def die(self):
        self.gui.delt(self)
        self.gui.update()

    def stop_or_die(self):
        if self.button_stop.cget("bg") == "red":
            self.stop()
        else:
            if self.getpath():
                self.text.delete("1.0", "end")
            else:
                self.die()


class gui(tk.Tk):

    def __init__(
        self,
        screenName=None,
        baseName=None,
        className="Tk",
        useTk=True,
        sync=False,
        use=None,
    ):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.configure(height=height, width=width)
        self.init_frame()
        self.init_button()
        self.control = controler()
        self.init_menu()
        self.init_sca()

    def init_state(self):
        self.isplay = tk.Button()

    def init_frame(self):
        self.singles = list()
        self.bigframea = tk.Frame()
        self.leftframe = tk.Frame(self.bigframea, bg="#F0F8FF", border=10)
        self.rightframe = tk.Frame(self.bigframea)
        self.leftframe.pack(side="left", expand=True, fill="x")
        self.rightframe.pack(side="right", fill="x")
        self.bigframea.pack(side="top", expand=True, fill="x")

    def init_button(self):
        self.addbt = tk.Button(self.rightframe, text="add", command=self.chosefile_add)
        self.savebt = tk.Button(self.rightframe, text="save", command=self.save)
        self.loadbt = tk.Button(self.rightframe, text="load", command=self.load)
        self.clearbt = tk.Button(self.rightframe, text="clear", command=self.clear)
        self.stopbt = tk.Button(self.rightframe, text="stop", command=self.stop)
        self.loopbt = tk.Button(self.rightframe, text="loop", command=self.loop)

        self.addbt.pack(side="top")
        self.savebt.pack(side="top")
        self.loadbt.pack(side="top")
        self.clearbt.pack(side="top")
        self.stopbt.pack(side="top")
        self.loopbt.pack(side="top")

    def loop(self):
        self.stop()
        state = self.control.loop
        if state == False:
            self.control.loop = True
            self.loopbt.configure(bg="red")
        else:
            self.control.loop = False
            self.loopbt.configure(bg="white")

    def delt(self, sobj: single):
        for i in range(len(self.singles)):
            if self.singles[i] == sobj:
                self.singles[i].frame.destroy()
                del self.singles[i]
                break

    def clear(self):
        p = self.leftframe.winfo_children()
        for i in p:
            i.destroy()
        self.singles.clear()

    def add(self, path):
        self.singles.append(single(self.leftframe, path=path, gui=self))

    def chosefile_add(self):
        p = filedialog.askopenfilenames()
        if p:
            if p[0].endswith(".apl"):
                self.load(p[0])
            else:
                for i in p:
                    self.add(i)

    def stop(self):
        self.control.stop()
        for i in self.singles:
            try:
                i.button_stop.configure(bg="white")
            except:
                pass

    def show_singles(self):
        print(self.singles)

    def save(self):
        paths = [i.getpath() for i in self.singles]
        if all(paths) and len(paths) != 0:
            p = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.apl")])
            if not p.endswith(".apl"):
                p = p + ".apl"
            with open(p, "w") as fp:
                for i in paths:
                    fp.write(i + "\n")

    def load(self, path=None):
        if path == None:
            p = filedialog.askopenfilename(filetypes=[("Text Files", "*.apl")])
            if p:
                try:
                    with open(p, "r") as fp:
                        paths = fp.read().split("\n")
                        self.clear()
                        for i in paths:
                            o = i.strip()
                            if o:
                                self.add(o)
                except:
                    messagebox.showerror("load errror")
        else:
            try:
                with open(path, "r") as fp:
                    paths = fp.read().split("\n")
                    self.clear()
                    for i in paths:
                        o = i.strip()
                        if o:
                            self.add(o)
            except:
                messagebox.showerror("load errror")

    def init_menu(self):
        xVariable = tk.StringVar()  # #创建变量，便于取值
        self.com = ttk.Combobox(self, textvariable=xVariable)  # #创建下拉菜单
        self.com.pack(side="top", fill="x", expand=True)  # #将下拉菜单绑定到窗体
        devices = self.control.preliminary_instruction_output()  # #给下拉菜单设定值
        index = devices.index(difort_divice)
        self.com["value"] = devices
        self.com.current(index)
        self.com.bind("<<ComboboxSelected>>", self.change_device)

    def init_sca(self):
        self.vol = tk.StringVar()
        self.sca = tk.Scale(
            self.bigframea,
            from_=0,
            to=1000,
            resolution=4,
            variable=self.vol,
            command=self.changevol,
        )
        self.vol.set(100)
        self.sca.pack(side="top", expand=True, fill="y")

    def changevol(self, event):
        v = self.vol.get()
        print(v)
        self.control.changevol(v)

    def change_device(self, event):
        nam = self.com.get()
        try:
            self.stop()
            self.control.changedevice(nam)
        except MyException:
            messagebox.showerror("error", "找不到设备")


class lis:

    def __init__(self, app: gui):
        self.app = app
        self.init_play()
        self.run()
        self.p.start()

    def init_play(self):
        self.di = {"<ctrl>+{}".format(i): self.gen_func(i) for i in range(1, 7)}
        self.di["<ctrl>+0"] = self.app.stop
        print(self.di)

    def gen_func(self, number):

        def play():
            try:
                print("press", number)
                self.app.singles[number - 1].add_or_play()
            except:
                print("error")
                pass

        return play

    def run(self):
        print("监听开始")
        self.p = pynput.keyboard.GlobalHotKeys(self.di)


if __name__ == "__main__":
    import pprint

    app = gui()
    l = lis(app)
    tk.mainloop()
    sys.exit()
