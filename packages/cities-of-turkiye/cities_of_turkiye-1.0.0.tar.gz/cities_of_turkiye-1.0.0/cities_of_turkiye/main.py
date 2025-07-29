from .veriler import iller

class Iller:

    def get(self, plaka):
        return iller.get(str(plaka).zfill(2))

    def yazdir(self, plaka):
        veri = self.get(plaka)
        if not veri:
            print(f"{plaka} kodlu il bulunamadı.")
            return
        print(f"Ad: {veri['ad']}")
        print(f"Bölge: {veri['bolge']}")
        print(f"Yapılar: {', '.join(veri['yapilar'])}")
        print(f"Ürünler: {', '.join(veri['urunler'])}")

    def tumu(self):
        """Tüm illeri döner"""
        return iller
