import flet as ft
from datetime import datetime
import json
import os

def main(page: ft.Page):
    page.title = "Rehberlik PWA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # --- VERİ YÖNETİMİ (Güvenli Depolama) ---
    def verileri_yukle():
        # client_storage hatasını önlemek için get_storage kullanımı
        veriler = page.client_storage.get("rehberlik_verisi") if hasattr(page, 'client_storage') else None
        return json.loads(veriler) if veriler else {"ogrenciler": [], "notlar": []}

    def veri_kaydet(data):
        if hasattr(page, 'client_storage'):
            page.client_storage.set("rehberlik_verisi", json.dumps(data))

    # --- ELEMANLAR ---
    ad_in = ft.TextField(label="Öğrenci Ad Soyad")
    sinif_in = ft.TextField(label="Sınıf")
    no_in = ft.TextField(label="Okul No")
    
    ogrenci_secici = ft.Dropdown(label="Öğrenci Seçin")
    kat_in = ft.Dropdown(
        label="Görüşme Tipi",
        options=[ft.dropdown.Option("Öğrenci"), ft.dropdown.Option("Veli"), ft.dropdown.Option("Öğretmen")],
        value="Öğrenci"
    )
    tarih_in = ft.TextField(label="Tarih", value=datetime.now().strftime("%d-%m-%Y"))
    not_txt = ft.TextField(label="Not", multiline=True, min_lines=3)
    not_listesi = ft.Column(spacing=10)
    ogrenci_yonetim_listesi = ft.Column(spacing=10)

    # --- FONKSİYONLAR ---
    def listeleri_tazele():
        data = verileri_yukle()
        ogrenciler = sorted(data["ogrenciler"], key=lambda x: x["ad"])
        ogrenci_secici.options = [ft.dropdown.Option(key=str(o["no"]), text=f"{o['ad']} ({o['no']})") for o in ogrenciler]
        
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
            listeleri_tazele()
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
            notlar = [n for n in data["notlar"] if n["ogrenci_no"] == ogrenci_secici.value]
            for n in reversed(notlar):
                not_listesi.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"📅 {n['tarih']} | {n['kat']}", weight="bold", expand=True),
                                ft.TextButton("Sil", style=ft.ButtonStyle(color="red"), on_click=lambda _, i=n['id']: not_sil(i))
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
    kayit_ekrani = ft.Column([ft.Text("Öğrenci Yönetimi", size=22, weight="bold"), ad_in, sinif_in, no_in, ft.ElevatedButton("Öğrenci Kaydet", on_click=ogrenci_kaydet), ft.Divider(), ogrenci_yonetim_listesi])
    not_ekrani = ft.Column([ft.Text("Görüşme Notları", size=22, weight="bold"), ogrenci_secici, ft.ElevatedButton("Notları Getir", on_click=notlari_listele), ft.Divider(), tarih_in, kat_in, not_txt, ft.ElevatedButton("Notu Kaydet", on_click=notu_kaydet), ft.Divider(), not_listesi], visible=False)

    def ekran_degis(e):
        kayit_ekrani.visible = not kayit_ekrani.visible
        not_ekrani.visible = not not_ekrani.visible
        btn_nav.text = "Öğrenci Yönetimi" if not_ekrani.visible else "Not İşlemleri"
        page.update()

    btn_nav = ft.OutlinedButton("Not İşlemlerine Geç", on_click=ekran_degis)
    page.add(ft.Container(content=ft.Text("REHBERLİK", size=25, color="white"), bgcolor="blue", padding=15, border_radius=10), btn_nav, kayit_ekrani, not_ekrani)
    listeleri_tazele()

if __name__ == "__main__":
    # Render PORT ayarı
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
