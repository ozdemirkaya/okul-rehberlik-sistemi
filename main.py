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
        veriler = page.client_storage.get("rehberlik_verisi")
        if veriler:
            try:
                return json.loads(veriler)
            except:
                return {"ogrenciler": [], "notlar": []}
        return {"ogrenciler": [], "notlar": []}

    def veri_kaydet(data):
        page.client_storage.set("rehberlik_verisi", json.dumps(data))

    # --- ELEMANLAR ---
    ad_in = ft.TextField(label="Öğrenci Ad Soyad")
    sinif_in = ft.TextField(label="Sınıf")
    no_in = ft.TextField(label="Okul No")
    
    ogrenci_secici = ft.Dropdown(label="Öğrenci Seçin", expand=True)
    kat_in = ft.Dropdown(
        label="Görüşme Tipi",
        options=[ft.dropdown.Option("Öğrenci"), ft.dropdown.Option("Veli"), ft.dropdown.Option("Öğretmen")],
        value="Öğrenci"
    )
    tarih_in = ft.TextField(label="Tarih", value=datetime.now().strftime("%d-%m-%Y"))
    not_txt = ft.TextField(label="Görüşme Notu", multiline=True, min_lines=3)
    not_listesi = ft.Column(spacing=10)
    ogrenci_yonetim_listesi = ft.Column(spacing=10)

    # --- FONKSİYONLAR ---
    def listeleri_tazele():
        data = verileri_yukle()
        ogrenciler = sorted(data["ogrenciler"], key=lambda x: x["ad"])
        
        # Dropdown'u temizle ve en baştan doldur
        secenekler = []
        for o in ogrenciler:
            secenekler.append(ft.dropdown.Option(key=str(o["no"]), text=f"{o['ad']} ({o['no']})"))
        
        ogrenci_secici.options = secenekler
        
        # Yönetim listesini güncelle
        ogrenci_yonetim_listesi.controls.clear()
        for o in ogrenciler:
            ogrenci_yonetim_listesi.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([ft.Text(o["ad"], weight="bold"), ft.Text(f"No: {o['no']}", size=12)], expand=True),
                        ft.TextButton("Sil", style=ft.ButtonStyle(color="red"), on_click=lambda _, n=o["no"]: ogrenci_sil(n))
                    ]),
                    padding=10, bgcolor="#F0F4F8", border_radius=8
                )
            )
        page.update()

    def ogrenci_kaydet(e):
        if ad_in.value and no_in.value:
            data = verileri_yukle()
            data["ogrenciler"].append({"ad": ad_in.value, "no": no_in.value, "sinif": sinif_in.value})
            veri_kaydet(data)
            
            ad_in.value = ""; no_in.value = ""; sinif_in.value = ""
            listeleri_tazele() # Hemen listeyi yenile
            page.snack_bar = ft.SnackBar(ft.Text("Kayıt Başarılı!"))
            page.snack_bar.open = True
        page.update()

    def notu_kaydet(e):
        if ogrenci_secici.value and not_txt.value:
            data = verileri_yukle()
            yeni_not = {
                "id": datetime.now().timestamp(),
                "ogrenci_no": ogrenci_secici.value,
                "kat": kat_in.value,
                "not": not_txt.value,
                "tarih": tarih_in.value
            }
            data["notlar"].append(yeni_not)
            veri_kaydet(data)
            not_txt.value = ""
            notlari_listele(None)
        page.update()

    def notlari_listele(e):
        not_listesi.controls.clear()
        data = verileri_yukle()
        if ogrenci_secici.value:
            filtrelenmis =
