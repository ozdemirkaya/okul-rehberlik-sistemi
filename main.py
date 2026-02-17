import flet as ft
from datetime import datetime
import json
import os

def main(page: ft.Page):
    page.title = "Rehberlik"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # --- VERİ YÖNETİMİ ---
    def verileri_yukle():
        try:
            # Client storage yerine daha basit bir erişim deniyoruz
            res = page.client_storage.get("rehberlik_verisi")
            if res:
                return json.loads(res)
        except:
            pass
        return {"ogrenciler": [], "notlar": []}

    def veri_kaydet(data):
        try:
            page.client_storage.set("rehberlik_verisi", json.dumps(data))
        except:
            pass

    # --- ELEMANLAR ---
    ad_in = ft.TextField(label="Öğrenci Ad Soyad")
    sinif_in = ft.TextField(label="Sınıf")
    no_in = ft.TextField(label="Okul No")
    
    # Dropdown'un içini her seferinde dolduran fonksiyon
    def dropdown_doldur(e=None):
        data = verileri_yukle()
        ogrenciler = data.get("ogrenciler", [])
        ogrenci_secici.options = [] # Temizle
        for o in ogrenciler:
            ogrenci_secici.options.append(
                ft.dropdown.Option(key=str(o["no"]), text=f"{o['ad']} ({o['sinif']})")
            )
        page.update()

    ogrenci_secici = ft.Dropdown(
        label="Öğrenci Seçin", 
        expand=True,
        on_focus=dropdown_doldur # Kutucuğa her tıklandığında listeyi tazeler!
    )
    
    kat_in = ft.Dropdown(
        label="Görüşme Tipi",
        options=[ft.dropdown.Option("Öğrenci"), ft.dropdown.Option("Veli"), ft.dropdown.Option("Öğretmen")],
        value="Öğrenci"
    )
    tarih_in = ft.TextField(label="Tarih", value=datetime.now().strftime("%d-%m-%Y"))
    not_txt = ft.TextField(label="Not", multiline=True, min_lines=3)
    not_listesi = ft.Column(spacing=10)

    # --- FONKSİYONLAR ---
    def ogrenci_kaydet(e):
        if ad_in.value and no_in.value:
            data = verileri_yukle()
            data["ogrenciler"].append({
                "ad": ad_in.value, 
                "no": no_in.value, 
                "sinif": sinif_in.value
            })
            veri_kaydet(data)
            ad_in.value = ""; no_in.value = ""; sinif_in.value = ""
            dropdown_doldur()
            page.snack_bar = ft.SnackBar(ft.Text("Başarıyla Kaydedildi!"))
            page.snack_bar.open = True
            page.update()

    def notu_kaydet(e):
        if ogrenci_secici.value and not_txt.value:
            data = verileri_yukle()
            yeni_not = {
                "id": str(datetime.now().timestamp()),
                "ogrenci_no": ogrenci_secici.value,
                "kat": kat_in.value,
                "not": not_txt.value,
                "tarih": tarih_in.value
            }
            data["notlar"].append(yeni_not)
            veri_kaydet(data)
            not_txt.value = ""
            notlari_getir(None)
        page.update()

    def notlari_getir(e):
        not_listesi.controls.clear()
        data = verileri_yukle()
        for n in reversed(data.get("notlar", [])):
            if n["ogrenci_no"] == ogrenci_secici.value:
                not_listesi.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{n['tarih']} | {n['kat']}", weight="bold"),
                            ft.Text(n['not'])
                        ]),
                        padding=10, bgcolor="#eeeeee", border_radius=10
                    )
                )
        page.update()

    # --- TASARIM ---
    kayit_ekrani = ft.Column([
        ft.Text("Öğrenci Kaydı", size=20, weight="bold"),
        ad_in, sinif_in, no_in,
        ft.ElevatedButton("Öğrenciyi Kaydet", on_click=ogrenci_kaydet),
        ft.Divider()
    ])

    not_ekrani = ft.Column([
        ft.Text("Görüşme Notları", size=20, weight="bold"),
        ft.Row([ogrenci_secici, ft.ElevatedButton("Tazele", on_click=dropdown_doldur)]),
        ft.ElevatedButton("Notları Getir", on_click=notlari_getir),
        tarih_in, kat_in, not_txt,
        ft.ElevatedButton("Notu Kaydet", on_click=notu_kaydet),
        not_listesi
    ], visible=False)

    def ekran_degis(e):
        kayit_ekrani.visible = not kayit_ekrani.visible
        not_ekrani.visible = not not_ekrani.visible
        btn_nav.text = "Öğrenci Paneli" if not_ekrani.visible else "Not İşlemlerine Geç"
        dropdown_doldur()
        page.update()

    btn_nav = ft.OutlinedButton("Not İşlemlerine Geç", on_click=ekran_degis)
    
    page.add(
        ft.Container(content=ft.Text("REHBERLİK PANELİ", color="white", size=22), bgcolor="blue", padding=15),
        btn_nav,
        kayit_ekrani,
        not_ekrani
    )
    dropdown_doldur()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.getenv("PORT", 8080)))
