import customtkinter as ctk
import sqlite3
from tkinter import messagebox

conn=sqlite3.connect("hakistok.hb")
cursor=conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,marka TEXT,kalite TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS sizes(id INTEGER PRIMARY KEY AUTOINCREMENT,en INTEGER,boy INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS stock(products_id INTEGER,sizes_id INTEGER,adet INTEGER DEFAULT 0,PRIMARY KEY (products_id,sizes_id))")

sizes_list = [(200, 290),(170, 250),(160, 230),(120, 180),(100, 300),(100, 200),(80, 300),(80, 150)]
for en, boy in sizes_list:
    cursor.execute("SELECT id FROM sizes WHERE en=? AND boy=?", (en, boy))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO sizes (en, boy) VALUES (?, ?)", (en, boy))
conn.commit()   #burada program ilk çalıştığında gerçekten altyapıda bir şey yok.o yüzden if not çalışıyor ve program sizes verilerini altyapıya ekliyor.program ikinci üçüncü kez çalıştığında soruyor bu sizes var mı yok mu diye böylece tekrar tekrar altyapıya eklenmesini engelliyor


class ProductFrame(ctk.CTkFrame): #bu oluşturduğu kutu şudur marka,kalite isimlerinin sil butonu olan içinde numaraları tutacak olan framedir
    def __init__(self, master, products_id, marka, kalite, **kwargs): #burası ilk bu frame çalıştığında çalışacak ilk kısımdır.self bu kutu kendisine aitdir ve bu terimlerde başına self geldimi kutunun kendisine ait olacağını belirtir
        super().__init__(master, **kwargs) #burası diyorki benim ne haddime kutu oluşturmak sen üst makam yani kutuyu oluştur (ctk.CTkFrame) den bahsediyorum.ben ise ona kendim bazı nacizane bir kaç özellik ekleyeceğim onları buradan eklerim
        self.products_id = products_id #birazdan + butonuna bastığımızda,kutunun içindeki id numarasını arttırsın diye bunu buraya tanımladık
        self.configure(border_width=2, border_color="#3a7ebf")

        header = ctk.CTkFrame(self, fg_color="#3a7ebf", height=30)
        header.pack(fill="x") #buradaki self var ya işte o anlatıyor ana frame in elemanı olduğunu onun üstüne geleceğini.ve ilk olarak pack yapıyını burada kullandığımız kutunun (YANİ FRAME nin başına) bu gelri.fill doldur manasına gelir.fill=x x yönünde ,fill=y y yönünde,fill=both ise her iki yöndede doldur demektir
        
        info_label = ctk.CTkLabel(header, text=f"{marka.upper()} - {kalite.upper()}", text_color="white", font=("Arial", 13, "bold"))
        info_label.pack(side="left", padx=10)

        del_btn = ctk.CTkButton(header, text="SİL", width=40, height=20, fg_color="#c0392b", hover_color="#e74c3c", command=self.delete_product)
        del_btn.pack(side="right", padx=5)

        grid_container=ctk.CTkFrame(self)
        grid_container.pack(pady=5,padx=5,fill="both")

        cursor.execute("SELECT id,en,boy FROM sizes")
        all_sizes=cursor.fetchall()

        for index,(sid,en,boy) in enumerate(all_sizes):
            row,column=divmod(index,4) #burada row satır yani bölüm kısmına denk geliyor,column satır kısmına yani kalan kısmına denk geliyor.divmod bize bölme işleminde bölüm ve kalanı veren bir python formülüdür.mesela index numarası 4 e bölündüğünde (diyelim index 3 olsun) kalan 0 yani satır 0 kalan ise 3 yani sütün 3 oluyor böylelikle sıralanmış oluyor
            s_frame=ctk.CTkFrame(grid_container,width=120,height=60,border_width=1)
            s_frame.grid(row=row,column=column,padx=5,pady=5)

            ctk.CTkLabel(s_frame, text=f"{en}x{boy}",font=("Arial",10)).pack()

            btn_frame=ctk.CTkFrame(s_frame,fg_color="transparent")
            btn_frame.pack() #burası küçük kutu olan s_frame nin içinde butonlar bir hizada olsun diye bir frame daha oluşturduk renk transparent de şeffaf renktir ve görünmez yani hayali bir framedir

            lbl_miktar = ctk.CTkLabel(btn_frame, text=self.get_qty(sid), font=("Arial", 12, "bold"))

            m_btn = ctk.CTkButton(btn_frame, text="-", width=25, height=25, command=lambda s=sid, l=lbl_miktar: self.update_stock(s, l, -1))
            m_btn.pack(side="left", padx=2) #burada lambda şu demek bu butona basıldığında çalıştır otomatik olarak çalıştırma.
            
            lbl_miktar.pack(side="left", padx=5)
            
            p_btn = ctk.CTkButton(btn_frame, text="+", width=25, height=25, command=lambda s=sid, l=lbl_miktar: self.update_stock(s, l, 1))
            p_btn.pack(side="left", padx=2)

    def get_qty(self,size_id):
        cursor.execute("SELECT adet FROM stock WHERE products_id=? AND sizes_id=?", (self.products_id, size_id))
        res = cursor.fetchone()
        return res[0] if res else 0
    def update_stock(self,size_id,label,delta):
        current = int(label.cget("text"))
        new_val = max(0, current + delta) #burada label.cget ekrandaki text yazısını al oku demek.bu satır ise current e ekle delta değerii ve 0 ve diyer sayıdan hangisi büyükse onu al(yani sıfırın altına inmesini engelliyoruz burada)
        cursor.execute("INSERT OR REPLACE INTO stock (products_id, sizes_id, adet) VALUES (?, ?, ?)", (self.products_id, size_id, new_val))
        conn.commit()
        label.configure(text=str(new_val))
    def delete_product(self):
        if messagebox.askyesno("ONAY","Bu halı modelini ve TÜM stoklarını silmek istediğine emin misin?"):
            cursor.execute("DELETE FROM products WHERE id=?",(self.products_id,))
            cursor.execute("DELETE FROM stock WHERE products_id=?",(self.products_id,))
            conn.commit()
            self.destroy() #bu zamana kadar veri tabanından sildik ama ekrandan silmedik bu kod ile ekrandan da silmiş oluyorz
def add_new_product():
    m=entry_marka.get().strip()
    k=entry_kalite.get().strip()
    if m and k:
        cursor.execute("INSERT INTO products (marka,kalite) VALUES (?,?)",(m,k))
        conn.commit()
        p_id=cursor.lastrowid
        new_card=ProductFrame(scrollable_frame,p_id,m,k)
        new_card.pack(pady=10,padx=10,fill="x")
        entry_marka.delete(0,'end')
        entry_kalite.delete(0,'end')
def kayıtları_getirme(): #burası programı ilk çalıştırdığımızda veri tabanından bilgileri alır ve her şeyi yerine koyar
    cursor.execute("SELECT id,marka,kalite FROM products")
    for p_id,m,k in cursor.fetchall():
        ProductFrame(scrollable_frame,p_id,m,k).pack(pady=10,padx=10,fill="x")

app=ctk.CTk()
app.title("KARACA HALI                                                                                                                                                        by_emirhanberber")
app.geometry("800x700")

ilk_panel = ctk.CTkFrame(app)
ilk_panel.pack(pady=10, padx=10, fill="x")

entry_marka = ctk.CTkEntry(ilk_panel, placeholder_text="Marka (Örn: İPEK)")
entry_marka.pack(side="left", padx=5, pady=10, expand=True, fill="x")

entry_kalite = ctk.CTkEntry(ilk_panel, placeholder_text="Kalite (Örn: BLOSSOM)")
entry_kalite.pack(side="left", padx=5, pady=10, expand=True, fill="x")

btn_ekle = ctk.CTkButton(ilk_panel, text="ÜRÜN EKLE", fg_color="#27ae60", command=add_new_product)
btn_ekle.pack(side="left", padx=5)

scrollable_frame = ctk.CTkScrollableFrame(app)
scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True) #burada expand ana pencere büyürse frame de büyüsün diye yazılan bir koddur

kayıtları_getirme()
app.mainloop()
        