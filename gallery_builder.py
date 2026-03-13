
import os,json
from PIL import Image,ExifTags,ImageTk
import tkinter as tk
from tkinter import ttk

IMAGE_FOLDER="images"
THUMB_FOLDER="thumbnails"
JSON_FILE="gallery.json"

THUMB_SIZE=600
PREVIEW_SIZE=500

os.makedirs(THUMB_FOLDER,exist_ok=True)

types=["Landscape","Animals","Sports","Architecture","Flowers","Sunsets","Night","Nature","Art","Urban","Road"]

countries_by_continent={
"Europe":["Spain","France","Germany","Switzerland","Poland","Czechia","Belgium","Netherlands","Luxembourg","Lichtenstein","Austria","Slovenia","Slovakia","Denmark","Sweden","Finland","Croatia","Portugal"],
"SouthAmerica":["Uruguay","Argentina"],
"Asia":["Taiwan","Singapore","Nepal","India","Turkey"],
"NorthAmerica":["UnitedStates"],
"Africa":["Namibia"]
}

country_to_continent={}
for c,vals in countries_by_continent.items():
    for v in vals: country_to_continent[v]=c

def make_thumbnail(file):
    ip=os.path.join(IMAGE_FOLDER,file)
    tp=os.path.join(THUMB_FOLDER,file)
    if os.path.exists(tp): return
    with Image.open(ip) as img:
        w,h=img.size
        scale=THUMB_SIZE/max(w,h)
        new=(int(w*scale),int(h*scale))
        img.resize(new,Image.LANCZOS).save(tp,quality=85)

def load_json():
    if not os.path.exists(JSON_FILE): return []
    with open(JSON_FILE) as f: return json.load(f)

def save_json(data):
    with open(JSON_FILE,"w") as f: json.dump(data,f,indent=2)

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

existing=load_json()
lookup={p["file"]:p for p in existing}
new_photos=[]

for f in os.listdir(IMAGE_FOLDER):
    if not f.lower().endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")): continue
    make_thumbnail(f)
    if f not in lookup:
        new_photos.append({"file":f,"tags":[],"caption":"","year":get_year(os.path.join(IMAGE_FOLDER,f))})

if not new_photos:
    print("No new photos."); exit()

class Tagger:
    def __init__(self,root):
        self.root=root
        self.i=0

        self.preview=tk.Label(root); self.preview.pack(pady=10)
        self.file_label=tk.Label(root,text="file:",font=("Arial",12)); self.file_label.pack()
        tk.Label(root,text="enter photo description:").pack()

        self.caption=tk.Entry(root,width=60); self.caption.pack(pady=5)

        tk.Label(root,text="Country").pack()
        self.country=ttk.Combobox(root,width=30); self.country.pack()

        vals=[]
        for cont,countries in countries_by_continent.items():
            vals.append(f"--- {cont} ---")
            vals.extend(countries)
        self.country["values"]=vals

        type_frame=tk.LabelFrame(root,text="Type"); type_frame.pack(pady=10)

        self.type_vars={}
        for t in types:
            v=tk.BooleanVar()
            tk.Checkbutton(type_frame,text=t,variable=v).pack(side="left")
            self.type_vars[t]=v

        nav=tk.Frame(root); nav.pack(pady=10)
        tk.Button(nav,text="Previous",command=self.prev).pack(side="left")
        tk.Button(nav,text="Next",command=self.next).pack(side="left")
        tk.Button(nav,text="Save",command=self.save).pack(side="left")

        root.bind("<Left>",lambda e:self.prev())
        root.bind("<Right>",lambda e:self.next())

        self.load()

    def load(self):
        p=new_photos[self.i]
        path=os.path.join(IMAGE_FOLDER,p["file"])
        img=Image.open(path); img.thumbnail((PREVIEW_SIZE,PREVIEW_SIZE))
        self.tkimg=ImageTk.PhotoImage(img)
        self.preview.config(image=self.tkimg)
        self.file_label.config(text=f"file: {p['file']}")
        self.caption.delete(0,"end")
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
        p=new_photos[self.i]
        p["tags"]=self.collect_tags()
        p["caption"]=self.caption.get()
        existing.append(p)
        save_json(existing)

    def next(self):
        self.save(); self.i=(self.i+1)%len(new_photos); self.load()

    def prev(self):
        self.save(); self.i=(self.i-1)%len(new_photos); self.load()

root=tk.Tk()
root.title("Photo Tagger")
app=Tagger(root)
root.mainloop()
