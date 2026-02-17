import flet as ft
from datetime import datetime
import json
import os

def main(page: ft.Page):
    page.title = "Rehberlik PWA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # --- VERİ YÖNETİMİ ---
    def verileri_yukle():
        veriler = page.client_storage.get("rehberlik_verisi")
        if veriler:
            return json.loads(veriler)
        return {"ogrenciler": [], "notlar": []}

    def veri_kaydet(data):
        page.client_storage.set("rehberlik_verisi", json.dumps(data))

    # --- ELEMANLAR ---
    ad_in = ft.TextField(label="Öğrenci Ad Soyad", autofocus=True)
    sinif_in = ft.TextField(label="Sınıf")
    no_in = ft.TextField(label="Okul No")
    
    ogrenci_secici = ft.Dropdown(
        label="Öğrenci Seçin",
        hint_text="Kayıtlı öğrenci bulunamadı",
        expand=True
    )
    
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
        
        # Dropdown seçeneklerini temizle ve yeniden doldur
        ogrenci_secici.options = []
        for o in ogrenciler:
            ogrenci_secici.options.append(
                ft.dropdown.Option(key=str(o["no"]), text=f"{o['ad']} ({o['no']})")
            )
        
        # Yönetim listesini tazele
        ogrenci_yonetim_listesi.controls.clear()
        for o in ogrenciler:
            ogrenci_yonetim_listesi.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([ft.Text(o["ad"], weight="bold"), ft.Text(f"No: {o['no']}", size=12)], expand=True),
                        ft.IconButton(icon=ft.icons.DELETE, icon_color="red", on_click=lambda _, n=o["no"]: ogrenci_sil(n))
                    ]),
                    padding=10, bgcolor="#F0F4F8", border_radius=8
                )
            )
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
            
            # Başarı mesajı
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ {ad_in.value} başarıyla kaydedildi!"))
            page.snack_bar.open = True
            
            # Formu temizle ve listeleri zorla tazele
            ad_in.value = ""; no_in.value = ""; sinif_in.value = ""
            listeleri_tazele()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Lütfen isim ve numara girin!"))
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
            page.snack_bar = ft.SnackBar(ft.Text("✅ Not başarıyla eklendi!"))
            page.snack_bar.open = True
            notlari_listele(None)
        page.update()

    def notlari_listele(e):
        not_listesi.controls.clear()
        data = verileri_yukle()
        if ogrenci_secici.value:
            filtrelenmis = [n for n in data["notlar"] if n["ogrenci_no"] == ogrenci_secici.value]
            for n in reversed(filtrelenmis):
                not_listesi.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"📅 {n['tarih']} | {n['kat']}", weight="bold", expand=True),
                                ft.IconButton(icon=ft.icons.DELETE, icon_color="red", scale=0.8, on_click=lambda _, i=n['id']: not_sil(i))
                            ]),
                            ft.Text(n['not'])
                        ]),
                        padding=10, bgcolor="#F5F5F5", border_radius=10
                    )
                )
        page.update()

    def ogrenci_sil(no):
        data = verileri_yukle()
        data["ogrenciler"] = [o for o in data["ogrenciler"] if o["no"] != no]
        data["notlar"] = [n for n in data["notlar"] if n["ogrenci_no"] != no]
        veri_kaydet(data)
        listeleri_tazele()

    def not_sil(not_id):
        data = verileri_yukle()
        data["notlar"] = [n for n in data["notlar"] if n["id"] != not_id]
        veri_kaydet(data)
        notlari_listele(None)

    # --- TASARIM ---
    kayit_ekrani = ft.Column([
        ft.Text("Öğrenci Yönetimi", size=22, weight="bold"),
        ad_in, sinif_in, no_in,
        ft.ElevatedButton("Öğrenciyi Kaydet", on_click=ogrenci_kaydet, icon=ft.icons.SAVE),
        ft.Divider(),
        ft.Text("Kayıtlı Öğrenciler:", size=18, weight="bold"),
        ogrenci_yonetim_listesi
    ])

    not_ekrani = ft.Column([
        ft.Text("Görüşme Notları", size=22, weight="bold"),
        ft.Row([ogrenci_secici, ft.IconButton(icon=ft.icons.REFRESH, on_click=lambda _: listeleri_tazele())]),
        ft.ElevatedButton("Notları Getir", on_click=notlari_listele, icon=ft.icons.LIST),
        ft.Divider(),
        tarih_in, kat_in, not_txt,
        ft.ElevatedButton("Notu Kaydet", on_click=notu_kaydet, icon=ft.icons.ADD),
        ft.Divider(),
        not_listesi
    ], visible=False)

    def ekran_degis(e):
        kayit_ekrani.visible = not kayit_ekrani.visible
        not_ekrani.visible = not not_ekrani.visible
        btn_nav.text = "Öğrenci Yönetimi" if not_ekrani.visible else "Not İşlemleri"
        if not_ekrani.visible:
            listeleri_tazele()
        page.update()

    btn_nav = ft.OutlinedButton("Not İşlemlerine Geç", on_click=ekran_degis)
    page.add(
        ft.Container(content=ft.Text("REHBERLİK", size=25, color="white", weight="bold"), bgcolor="blue", padding=15, border_radius=10),
        btn_nav, 
        ft.Divider(),
        kayit_ekrani, 
        not_ekrani
    )
    listeleri_tazele()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
