__author__ = 'Snilton'
version="VERSION: ALPHA 0.5"

from tkinter import *
from tkinter import font
from tkinter import filedialog
import configparser
import atexit

root = Tk()
root.geometry("800x480")
root.title("Hultungs QuickStop  " + version)
cursor_visible = 1
root.wm_resizable(0,0);

inputframe = Frame(root)
settingsframe = Frame(root, bg="#34373c")
mainframe = Frame(root)
mode = "none"
homed = False
steplengtharray = [0.1,0.5,1,2,5]

#--------------------------------settings-------------------------------------------------
imagefolder = "images/"
maxvalue = 4500
steplength = 1
defaultdir = "C:\\"
homed = 0
fastrate = 100
opensans_big = font.Font(family="Open Sans Semibold", size=17)
opensans_small = font.Font(family="Open Sans Semibold", size=16)
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Open Sans Semibold", size=16)
digital_big = font.Font(family="Digital-7", size=100)
digital_small = font.Font(family="Digital-7", size=58)

def writeConfig():
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"Maxvalue": maxvalue,
                         "Steplength": steplength,
                         "Defaultdir": defaultdir,
                         "Fastrate": fastrate}
    with open("config.INI", "w") as configfile:
        config.write(configfile)
atexit.register(writeConfig)                                #Write config at exit

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.INI")
    global maxvalue
    global steplength
    global defaultdir
    global fastrate
    maxvalue = config["DEFAULT"]["Maxvalue"]
    steplength = int(config["DEFAULT"]["Steplength"])
    defaultdir = config["DEFAULT"]["Defaultdir"]
    fastrate = config["DEFAULT"]["Fastrate"]
c = readConfig()                                            # Read config at start
steplengthvalue = steplengtharray[int(steplength)]


def mainWindow(mode1):
    settingsframe.place_forget()
    inputframe.place_forget()
    mainframe.place(x=0,y=0,width=800,height=480)
    if mode1=="none":
        pass
    elif mode1 == "input":
        mainvaluelabel.value = inputvaluelabel.value
        mainvaluelabel.update()
    elif mode1 == "edit":
        lista.insert(inputvaluelabel.value)

    lista.draw()
    mode = "none"
def inputWindow(mode1):
    global mode
    mode = mode1
    if mode == "input":
        inputvaluelabel.value = mainvaluelabel.value
    elif mode == "edit":
        inputvaluelabel.value = lista.content[lista.selectedrow].value
    inputvaluelabel.update()
    mainframe.place_forget()
    inputframe.place(x=0,y=0,width=800,height=480)
def settingsWindow():
    mainframe.place_forget()
    settingsframe.place(x=0,y=0,width=800,height=480)

def moverel(pos):
    print("rel:" + str(pos))
def moveabs(pos):
    print("abs:" + str(pos))
def sendspeed():
    print(str(fastrate))

def home():
    print("home")

class DrawingObject:
    def __init__(self,frame,name,x1,y1,w,h):
        self.name = name
        self.image = PhotoImage(file=imagefolder + name + ".gif")
        self.label = Label(frame, image=self.image, bd=0)
        self.label.place(x=x1, y=y1, width=w, height=h)

class ButtonObject:
    def __init__(self,frame,name,x1,y1,w,h):
        self.name = name
        self.image = PhotoImage(file=imagefolder + name + ".gif")
        self.downimage = PhotoImage(file=imagefolder + name + "_d.gif")
        self.label = Label(frame, image=self.image, bd=0)
        self.label.place(x=x1, y=y1, width=w, height=h)
        self.label.bind("<Button-1>", self.clickdown)
        self.label.bind("<ButtonRelease-1>", self.clickup)
    def do(self):
        pass
    def clickdown(self, event):
        self.label.config(image=self.downimage)
    def clickup(self, event):
        self.label.config(image=self.image)
        self.do()
class BackspaceObject(ButtonObject):
    def do(self):
        inputvaluelabel.subtract()
class InputExitObject(ButtonObject):
    def do(self):
        if inputvaluelabel.value != "":
            inputvaluelabel.clear()
        else:
            mainWindow("exit")
class UpButtonObject(ButtonObject):
    def do(self):
        lista.moveup()
class DownButtonObject(ButtonObject):
    def do(self):
        lista.movedown()
class OpenButtonObject(ButtonObject):
    def do(self):
        file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('Cut list', '.txt')]
        options['initialdir'] = defaultdir
        #options['parent'] = root
        options['title'] = 'Open cutlist'
        filename = filedialog.askopenfilename(**file_opt)
        inFile = open(filename)
        buffer = []
        lista.reset()
        for line in inFile:
            buffer.append(line)
        inFile.close()
        for x in range(0, len(buffer)):
            lista.addrow(str(buffer[x]).rstrip('\n'))

class NumberButtonObject(ButtonObject):
    def __init__(self,frame,name,x1,y1,w,h,value):
        self.name = name
        self.image = PhotoImage(file=imagefolder + name + ".gif")
        self.downimage = PhotoImage(file=imagefolder + name + "_d.gif")
        self.label = Label(frame, image=self.image, bd=0)
        self.label.place(x=x1, y=y1, width=w, height=h)
        self.label.bind("<Button-1>", self.clickdown)
        self.label.bind("<ButtonRelease-1>", self.clickup)
        self.value = value
    def do(self):
        inputvaluelabel.add(self.value)
class InputPlayButtonObject(ButtonObject):
    def do(self):
        mainWindow(mode)
class EditButtonObject(ButtonObject):
    def do(self):
        inputWindow("edit")
class PlayButtonObject(ButtonObject):
    def do(self):
        if homed == True:
            if lista.content[lista.selectedrow].value != "":
                if float(lista.content[lista.selectedrow].value) > float(maxvalue):
                    lista.content[lista.selectedrow].value = maxvalue
                mainvaluelabel.change(lista.content[lista.selectedrow].value)
                moveabs(mainvaluelabel.value)
class SaveButtonObject(ButtonObject):
    def do(self):
        file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('Cut list', '.txt')]
        options['initialdir'] = defaultdir
        #options['parent'] = root
        options['title'] = 'Save cutlist'
        filename = filedialog.asksaveasfilename(**file_opt)
        outFile = open(filename, "w")
        for x in range(0,len(lista.content)-1):
            outFile.write(lista.content[x].value)
            outFile.write("\n")
        outFile.close()
class RemoveButtonObject(ButtonObject):
    def do(self):
        lista.delrow(lista.selectedrow)
class LenButtonObject(ButtonObject):
    def do(self):
        lenlabel.timecanvas.move("timelabel",-5,-5)
        global steplength
        global steplengthvalue
        steplength += 1
        if steplength == 5:
            steplength = 0
        steplengthvalue = steplengtharray[steplength]
        lenlabel.timecanvas.itemconfig("timelabel", text=str(steplengthvalue))
    def clickdown(self, event):
        self.label.config(image=self.downimage)
        lenlabel.timecanvas.move("timelabel",5,5)
class ParkButtonObject(ButtonObject):
    def do(self):
        if homed == True:
            moveabs(maxvalue)
            mainvaluelabel.change(maxvalue)
class HomeButtonObject(ButtonObject):
    def do(self):
        home()
        global homed
        homed = True
        mainvaluelabel.change("0")
class LeftButtonObject(ButtonObject):
    def do(self):
        if homed == True:
            mainvaluelabel.change(str(round((float(mainvaluelabel.value) + float(steplengtharray[steplength])),1)))
            moveabs(mainvaluelabel.value)
class RightButtonObject(ButtonObject):
    def do(self):
        if homed == True:
            mainvaluelabel.change(str(round((float(mainvaluelabel.value) - float(steplengtharray[steplength])),1)))
            moveabs(mainvaluelabel.value)
class SettingsButtonObject(ButtonObject):
    def do(self):
        settingsWindow()

class LenLabelObject():
    def __init__(self):
        self.timecanvas =Canvas(mainframe, width=44, height=30,background="#E29A00", bd=0, highlightthickness=0, relief='ridge')
        self.timecanvas.place(anchor=W, x=610, y=340)
        self.timecanvas.create_text(25,0, anchor=N, text=str(steplengtharray[steplength]), font=("opensans_small",17), fill="white", tags="timelabel")

class ValueObject:
    def __init__(self,frame,x1,y1,w,h,font1):
        self.name = ""
        self.value = "HOME"
        self.label = Label(frame,  pady=-10, justify=RIGHT, anchor=E, font=font1, text=self.value, background="#48525C", fg="white")
        self.label.place(x=x1,y=y1, width=w, height=h)
        self.label.bind("<Button-1>", self.clickdown)
    def add(self,value):
        if self.value == "0" and value != ".":
            self.value = ""
        if '.' in self.value:
            if len(self.value)-self.value.index('.')<2 and float(self.value+value) <10000 and len(self.value) < 6:
                self.value += value
        elif float(self.value+value) <10000 and len(self.value) < 6:
            self.value += value
        if float(self.value) > float(maxvalue) or self.value == str(maxvalue)+".":
            self.value = str(maxvalue)
        self.update()
    def subtract(self):
        if self.value != "":
            self.value = self.value[:-1]
            self.update()
    def clear(self):
        self.value = ""
        self.update()
    def change(self,value):
        self.value = str(value)
        if self.value == "0.0":
            self.value = "0"

        if float(self.value) < 0 and self.value != "":
            self.value = "0"
        self.update()
    def update(self):
        self.label.config(text=self.value)
    def clickdown(self, event):
        pass
class MainValueObject(ValueObject):
    def clickdown(self, event):
        if homed == True:
            inputWindow("input")
    def update(self):
        if round(float(self.value),1) % 1 == 0:
            self.value = str(round(float(self.value)))
        self.label.config(text=self.value)

class RowObject():
    def __init__(self,frame,font1,value):
        self.name = 0
        self.value = value
        self.label = Label(frame, pady=-10, justify=RIGHT, anchor=E, font=font1, text=self.value, background="#A7B1BA", fg="white")
        self.label.bind("<Button-1>", self.clickdown)
    def select(self):
        self.label.config(background="#48525C")
        self.selected = True
    def deselect(self):
        self.label.config(background="#A7B1BA")
        self.selected = False
    def clickdown(self,event):
        lista.selectedrow = self.name
        lista.draw()

class MyList():
    def __init__(self):
        self.content = [RowObject(mainframe,digital_small,"")]
        self.numberofrows = 1
        self.scroll = 0
        self.selectedrow = 0
        self.draw()
    def addrow(self,value):
        #if self.content[len(self.content)-1] == "":
        del self.content[len(self.content)-1]
        self.content.append(RowObject(mainframe,digital_small,value))
        self.content.append(RowObject(mainframe,digital_small,""))
        self.numberofrows += 1
        self.draw()
    def delrow(self, index):
        if self.content[index].value != "":
            if len(self.content) - index == 2:
                pass
            self.content[index].label.place_forget()
            self.content[index].label.destroy()
            del self.content[index]
            if self.scroll > 0 and self.selectedrow != 0:
                self.scroll -= 1
            if self.selectedrow == 0:
                self.movedown()
            self.moveup()
            self.numberofrows -= 1
    def reset(self):
        for item in self.content:
            item.label.place_forget()
            item.label.destroy()
        del self.content
        self.content = [RowObject(mainframe,digital_small,"")]
        self.numberofrows = 1
        self.selectedrow = 0
        self.scroll = 0
        self.draw()
    def draw(self):
        if self.selectedrow - self.scroll == 5 and self.content[self.selectedrow].value != "":
            self.scroll += 1
        for item in self.content:
            item.label.place_forget()
            item.deselect()
            item.label.config(text=item.value)
        if self.content[len(self.content)-1].value != "":
            self.content.append(RowObject(mainframe,digital_small,""))
            self.numberofrows += 1
            self.selectedrow += 1
        for i in range(0,min(6,len(self.content))):
            self.content[i+self.scroll].label.place(x=42,y=45+65*(i),width=216,height=65)
        self.content[self.selectedrow].select()
        i = 0
        for item in self.content:
            item.name = i
            i += 1
    def scrolldown(self):
        self.scroll += 1
    def scrollup(self):
        if self.scroll > 0:
            self.scroll -= 1
    def moveup(self):
        if self.selectedrow > 0:
            if self.selectedrow == self.scroll:
                self.scrollup()
            self.selectedrow -= 1
            self.draw()
    def insert(self,value):
        self.content[self.selectedrow].value = value
        self.draw()
    def movedown(self):
        if self.selectedrow < len(self.content)-1:
            self.selectedrow += 1
            if self.selectedrow - self.scroll > 5:
                self.scrolldown()
            self.draw()

#-----------------------------------------place main frame -------------------------------------
mainbackground = DrawingObject(mainframe,"bak_green",0,0,800,480)
mainvaluelabel = MainValueObject(mainframe,410,35,345,110,digital_big)
lista = MyList()
versionlabel = Label(mainframe, background="#33363B", fg="#999999", anchor=W, font=(opensans_small,9), text=version)
versionlabel.place(x=29, y=9, width=300, height=14)

upbutton = UpButtonObject(mainframe,"up",290,20,95,120)
downbutton = DownButtonObject(mainframe,"down",290,145,95,120)
openbutton = OpenButtonObject(mainframe,"open",290,270,95,95)
editbutton = EditButtonObject(mainframe,"edit",290,370,95,95)
playbutton = PlayButtonObject(mainframe,"play",390,170,95,95)
savebutton = SaveButtonObject(mainframe,"save",390,270,95,95)
removebutton = RemoveButtonObject(mainframe,"remove",390,370,95,95)
parkbutton = ParkButtonObject(mainframe,"park",590,170,95,95)
lenbutton = LenButtonObject(mainframe,"len",590,270,95,95)
leftbutton = LeftButtonObject(mainframe,"left",590,370,95,95)
homebutton = HomeButtonObject(mainframe,"home",690,170,95,95)
settingsbutton = SettingsButtonObject(mainframe,"settings",690,270,95,95)
rightbutton = RightButtonObject(mainframe,"right",690,370,95,95)
lenlabel = LenLabelObject()
lenlabel.timecanvas.bind("<Button-1>", lenbutton.clickdown)
lenlabel.timecanvas.bind("<ButtonRelease-1>", lenbutton.clickup)

#-----------------------------------------place input frame -------------------------------------
inputbackground = DrawingObject(inputframe,"bak_input",0,0,800,480)
inputvaluelabel = ValueObject(inputframe,40,35,345,110,digital_big)

backspacebutton = BackspaceObject(inputframe,"back",120,170,95,95)
inputplaybutton = InputPlayButtonObject(inputframe,"play",220,170,95,95)
inputexitbutton = InputExitObject(inputframe,"inputexit",320,170,95,95)

onebutton = NumberButtonObject(inputframe,"one",490,270,95,95,"1")
twobutton = NumberButtonObject(inputframe,"two",590,270,95,95,"2")
threeutton = NumberButtonObject(inputframe,"three",690,270,95,95,"3")
fourbutton = NumberButtonObject(inputframe,"four",490,170,95,95,"4")
fivebutton = NumberButtonObject(inputframe,"five",590,170,95,95,"5")
sixbutton = NumberButtonObject(inputframe,"six",690,170,95,95,"6")
sevenbutton = NumberButtonObject(inputframe,"seven",490,70,95,95,"7")
eightbutton = NumberButtonObject(inputframe,"eight",590,70,95,95,"8")
ninebutton = NumberButtonObject(inputframe,"nine",690,70,95,95,"9")
zerobutton = NumberButtonObject(inputframe,"zero",490,370,195,95,"0")
commabutton = NumberButtonObject(inputframe,"comma",690,370,95,95,".")

def confirmSettings():
    global maxvalue
    global parkvalue
    global fastrate
    global mediumrate
    global slowrate
    global defaultdir
    maxvalue = e1.get()
    parkvalue = e2.get()
    fastrate = e3.get()
    mediumrate = e4.get()
    slowrate = e5.get()
    defaultdir = e6.get()
    writeConfig()
    mainWindow(root)
def settingsBrowse():
    e6.set(re.sub('["]','',filedialog.askdirectory()))
def quit():
    root.quit()
settingsframe2 = Frame(settingsframe, padx=15, bg="#4e535a", bd=5)
settingsframe2.place(width=650,height=330,x=75,y=60)
Button(settingsframe2, text="Quit to Desktop", command=quit,fg="white", bg="#A7B1BA").grid(row=1,column=1,rowspan=1,sticky=E)
Label(settingsframe2,text="",fg="white", bg="#4e535a").grid(row=1)
Label(settingsframe2,text="",fg="white", bg="#4e535a").grid(row=2)
Label(settingsframe2, text="Maxvalue:",fg="white", bg="#4e535a").grid(row=3, sticky=W)
Label(settingsframe2, text="Ratedelay (ms):",fg="white", bg="#4e535a").grid(row=4, sticky=W)
Label(settingsframe2, text="Default directory: ",fg="white", bg="#4e535a").grid(row=7)
[e1, e2, e3, e4, e5, e6]=[StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()]
Entry(settingsframe2, textvariable=e1,width=15, font=default_font,fg="white", bg="#48525C").grid(row=3,column=1,sticky=W, columnspan=2)
Entry(settingsframe2, textvariable=e3,width=15, font=default_font,fg="white", bg="#48525C").grid(row=4,column=1,sticky=W, columnspan=2)
Entry(settingsframe2, textvariable=e6,width=32, font=default_font,fg="white", bg="#48525C").grid(row=7,column=1, sticky=E, columnspan=1)
Button(settingsframe2, text="    ", font=default_font, command=settingsBrowse,fg="white", bg="#A7B1BA", height=1).grid(row=7,column=2,sticky=E)
Label(settingsframe2,text="",fg="white", bg="#4e535a").grid(row=8)
Button(settingsframe2, text="  Save  ", command=confirmSettings,fg="white", bg="#A7B1BA").grid(row=9,column=1,rowspan=1,sticky=E)
e1.set(maxvalue)
e3.set(fastrate)
e6.set(re.sub('["]','',defaultdir))

#inputWindow()
mainWindow("exit")

root.mainloop()


