import os, json
from PIL import Image, ExifTags, ImageTk
import tkinter as tk
from tkinter import ttk

IMAGE_FOLDER = "images"
THUMB_FOLDER = "thumbnails"
JSON_FILE = "gallery.json"

THUMB_SIZE = 600
PREVIEW_SIZE = 500

os.makedirs(THUMB_FOLDER, exist_ok=True)

types = ["Landscape","Animals","Sports","Architecture","Flowers",
"Sunsets","Night","Nature","Art","Urban","Road"]

countries_by_continent = {
"Europe":["Spain","France","Germany","Switzerland","Poland","Czechia","Belgium","Netherlands","Luxembourg","Lichtenstein","Austria","Slovenia","Slovakia","Denmark","Sweden","Finland","Croatia","Portugal"],
"SouthAmerica":["Uruguay","Argentina"],
"Asia":["Taiwan","Singapore","Nepal","India","Turkey"],
"NorthAmerica":["UnitedStates"],
"Africa":["Namibia"]
}

country_to_continent = {c:cont for cont,vals in countries_by_continent.items() for c in vals}

def load_json():

    # If file doesn't exist → create it
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w") as f:
            json.dump([], f, indent=2)
        return []

    # If file exists but is empty → reset it
    if os.path.getsize(JSON_FILE) == 0:
        with open(JSON_FILE, "w") as f:
            json.dump([], f, indent=2)
        return []

    # Try to load JSON safely
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)

            # Ensure it's a list (expected format)
            if not isinstance(data, list):
                raise ValueError("JSON is not a list")

            return data

    except Exception as e:
        print("⚠️ gallery.json is corrupted or invalid. Resetting file.")
        
        # Backup the broken file just in case
        backup_name = "gallery_backup.json"
        os.rename(JSON_FILE, backup_name)
        print(f"Backup saved as {backup_name}")

        # Create fresh file
        with open(JSON_FILE, "w") as f:
            json.dump([], f, indent=2)

        return []

def save_json(data):
    with open(JSON_FILE,"w") as f: json.dump(data,f,indent=2)

def make_thumbnail(file):
    ip = os.path.join(IMAGE_FOLDER,file)
    tp = os.path.join(THUMB_FOLDER,file)
    if os.path.exists(tp): return
    with Image.open(ip) as img:
        w,h = img.size
        scale = THUMB_SIZE/max(w,h)
        img.resize((int(w*scale),int(h*scale)),Image.LANCZOS).save(tp,quality=85)

def get_year(path):
    try:
        img=Image.open(path)
        exif=img._getexif()
        if exif:
            for tag,val in exif.items():
                if ExifTags.TAGS.get(tag)=="DateTimeOriginal":
                    return val[:4]
    except: pass
    return ""

existing = load_json()
existing_files = {p["file"] for p in existing}

# ONLY NEW FILES
new_photos = [f for f in os.listdir(IMAGE_FOLDER)
              if f.lower().endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff"))
              and f not in existing_files]

if not new_photos:
    print("All new photos have been added to the gallery.")
    print('To edit entries, run "gallery_editor.py"')
    exit()

class Builder:

    def __init__(self,root):
        self.root=root
        self.i=0

        self.preview=tk.Label(root)
        self.preview.pack(pady=10)

        self.file_label=tk.Label(root,font=("Arial",12))
        self.file_label.pack()

        tk.Label(root,text="enter photo description:").pack()
        self.caption=tk.Entry(root,width=50)
        self.caption.pack()

        tk.Label(root,text="Country").pack()
        self.country=ttk.Combobox(root)
        self.country.pack()

        vals=[]
        for cont,countries in countries_by_continent.items():
            vals.append(f"--- {cont} ---")
            vals.extend(countries)
        self.country["values"]=vals

        type_frame=tk.LabelFrame(root,text="Type")
        type_frame.pack()

        self.type_vars={}
        for t in types:
            v=tk.BooleanVar()
            tk.Checkbutton(type_frame,text=t,variable=v).pack(side="left")
            self.type_vars[t]=v

        nav=tk.Frame(root)
        nav.pack(pady=10)

        tk.Button(nav,text="Skip",command=self.skip).pack(side="left")
        tk.Button(nav,text="Save & Continue",command=self.save).pack(side="left")

        self.load()

    def load(self):
        if self.i >= len(new_photos):
            self.done()
            return

        file=new_photos[self.i]
        path=os.path.join(IMAGE_FOLDER,file)

        img=Image.open(path)
        img.thumbnail((PREVIEW_SIZE,PREVIEW_SIZE))
        self.tkimg=ImageTk.PhotoImage(img)

        self.preview.config(image=self.tkimg)
        self.file_label.config(text=f"file: {file}")

        self.caption.delete(0,"end")
        self.country.set("")
        for v in self.type_vars.values(): v.set(False)

    def collect_tags(self):
        tags=[]
        c=self.country.get()
        if c and not c.startswith("---"):
            tags.append(c)
            cont=country_to_continent.get(c)
            if cont: tags.append(cont)
        for t,v in self.type_vars.items():
            if v.get(): tags.append(t)
        return tags

    def save(self):
        file=new_photos[self.i]

        make_thumbnail(file)

        entry={
            "file":file,
            "tags":self.collect_tags(),
            "caption":self.caption.get(),
            "year":get_year(os.path.join(IMAGE_FOLDER,file))
        }

        existing.append(entry)
        save_json(existing)

        self.i+=1
        self.load()

    def skip(self):
        self.i+=1
        self.load()

    def done(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root,text="All new photos have been added to the gallery.\nRun gallery_editor.py to edit entries.",font=("Arial",14)).pack(pady=50)

root=tk.Tk()
root.title("Gallery Builder")
Builder(root)
root.mainloop()