import json, os
import tkinter as tk
from PIL import Image, ImageTk

JSON_FILE="gallery.json"
IMAGE_FOLDER="images"
PREVIEW_SIZE=500

with open(JSON_FILE) as f:
    data=json.load(f)

if not data:
    print("No entries found.")
    exit()

class Editor:

    def __init__(self,root):
        self.root=root
        self.i=0

        self.preview=tk.Label(root)
        self.preview.pack()

        self.file_label=tk.Label(root)
        self.file_label.pack()

        tk.Label(root,text="Caption").pack()
        self.caption=tk.Entry(root,width=50)
        self.caption.pack()

        nav=tk.Frame(root)
        nav.pack(pady=10)

        tk.Button(nav,text="Previous",command=self.prev).pack(side="left")
        tk.Button(nav,text="Next",command=self.next).pack(side="left")
        tk.Button(nav,text="Save",command=self.save).pack(side="left")

        self.load()

    def load(self):
        p=data[self.i]
        path=os.path.join(IMAGE_FOLDER,p["file"])

        img=Image.open(path)
        img.thumbnail((PREVIEW_SIZE,PREVIEW_SIZE))
        self.tkimg=ImageTk.PhotoImage(img)

        self.preview.config(image=self.tkimg)
        self.file_label.config(text=p["file"])

        self.caption.delete(0,"end")
        self.caption.insert(0,p["caption"])

    def save(self):
        data[self.i]["caption"]=self.caption.get()
        with open(JSON_FILE,"w") as f:
            json.dump(data,f,indent=2)

    def next(self):
        self.save()
        self.i=(self.i+1)%len(data)
        self.load()

    def prev(self):
        self.save()
        self.i=(self.i-1)%len(data)
        self.load()

root=tk.Tk()
root.title("Gallery Editor")
Editor(root)
root.mainloop()