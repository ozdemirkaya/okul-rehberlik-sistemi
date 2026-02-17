import flet as ft
from datetime import datetime
import json
import os

def main(page: ft.Page):
    page.title = "Rehberlik Sistemi"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # --- VERİ YÖNETİMİ ---
    def verileri_yukle():
        try:
            veriler = page.client_storage.get("rehberlik_verisi")
            if veriler:
                return json.loads(veriler)
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
    sinif_in = ft.TextField(label="Sınıf") # Sınıf kutusu geri eklendi
    no_in = ft.TextField(label="Okul No")
    
    ogrenci_secici = ft.Dropdown(label="Öğrenci Seçin", expand=True)
    kat_in = ft.Dropdown(
        label="Görüşme Tipi",
        options=[ft.dropdown.Option("Öğrenci"), ft.dropdown.Option("Veli"), ft.dropdown.Option("Öğretmen")],
        value="Öğrenci"
    )
    tarih_in = ft.TextField(label="Tarih", value=datetime.now().strftime("%d-%m-%Y"))
    not_txt = ft.TextField(label="Not", multiline=True, min_lines=3)
    not_listesi = ft.Column(spacing=10)

    # --- FONKSİYONLAR ---
    def listeyi_doldur():
        data = verileri_yukle()
        ogrenciler = data.get("ogrenciler", [])
        # Dropdown'u temizle ve yeniden oluştur
        ogrenci_secici.options = [ft.dropdown.Option(key=str(o["no"]), text=f"{o['ad']} - {o.get('sinif', '')}") for o in ogrenciler]
        page.update()

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
            listeyi_doldur()
            page.snack_bar = ft.SnackBar(ft.Text("Kayıt Başarılı!"))
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
                            ft.Text(f"{n['
