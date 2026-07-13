## Yeni doküman içeriği (İş Emri ve Muayene Yönetimi / Temel Ayarlar)

- İş emri yöneticisi ile iş emri sorumlusu arasındaki fark nedir?
  Beklenen: yönetici tüm iş emirlerini görür, sorumlu sadece kendi
  oluşturduğu/atandığı iş emirlerini. Doğrulandı.
- İSG Katip sözleşmesi olmadan muayene onaya gönderilebilir mi?
  Beklenen: hayır, ama bu muayene yapmayı/kaydetmeyi engellemez, sadece
  onaya göndermeyi engeller. Doğrulandı.
- Muayene onay personeli kendi yaptığı muayeneyi onaylayabilir mi?
  Beklenen: evet. k=3'te bulunamadı, k=5'e
  çıkardık ama yine olmadı chunkları daha iyi ayırmak lazım olabilir.
- Değişken kare kod ile sabit kare kod arasındaki fark nedir?
  Doğrulandı.
- Taşıt takvimini kim görebilir?
  Beklenen: admin yetkisi, herkes sadece kendi kaydını görür. Doğrulandı.

## Yeni kavramlar (e_imza_cihazi, kalibrasyon)

- E-imza cihazım bilgisayarda tanınmıyor, ne yapmalıyım?
  Ölçüm cihazıyla karışmamalı. Doğrulandı.
- Multimetrenin kalibrasyon periyodu nasıl belirlenir?
  Kaynakta net yöntem yok, sistem bunu dürüstçe söyleyip genel takip
  mekanizmasını anlattı. Doğrulandı.
- Cihazın periyodik kontrolü ile ekipmanın periyodik kontrolü aynı mı?
  Burada resolver'daki top_k kesme bug'ını bulduk, düzelttik, tekrar
  test edip doğruladık.
- Kalibrasyon sertifikası nereden yüklenir?
  Doğrulandı.

## Regresyon

- Muayene raporu nasıl hazırlanır? (baseline) — Doğrulandı.
- Ekipman ile cihaz farklı şeyler mi? — Doğrulandı.
- Bugün dolar kaç TL? — Doğrulandı.

## Eski dokümanlar ve çapraz doküman tutarlılığı

- Rapor hazırlama rehberinde geçen ${C_sgkSicilNo} parametresi ne işe yarar?
  Orijinal (bugün dokunmadığımız) dokümandan, gerçek ${...} parametresi
  içeriyor — f-string fix'inin regresyon testi. Doğrulandı.
- Muayene kapsamı ile muayene hizmeti arasındaki fark nedir?
  Orijinal iso_17020_konfigurasyonlari.pdf'den, concepts.json'daki
  distinguish_from'un eski içerikte de çalıştığını doğruluyor. Doğrulandı.
- SGK sicil numarası firma bilgisinden mi geliyor, yoksa şubeden mi?
  En zor test: firmalar.pdf (firma-merkezli) ile Temel Ayarlar dokümanı
  (şube-merkezli) birbirini tamamlıyor gibi görünse de yüzeysel bakınca
  çelişkili duruyordu. Sistem ikisini doğru sentezledi, çelişki çıkarmadı.
  Doğrulandı.
- Yeni bir ölçüm cihazını sisteme nasıl eklerim?
  olcum_cihazlari.pdf ve Temel Ayarlar dokümanı aynı konuyu anlatıyor,
  ikisinden de kaynak geldi ama cevap tutarlı, tekrarsız. Doğrulandı.
- Teklif ile iş emri arasındaki ilişki nedir? 
  İş Hijyeni Süreç Yönetimi Kılavuzu'ndan geldi. Cevaptaki her madde 
  kaynağa neredeyse birebir sadık,uydurma yok. Doğrulandı

## Bilinen belirsizlikler (bug değil)

- "Cihaz tanınmıyor" (hiçbir ek bilgi olmadan) üç farklı anlama gelebilir
  (tanımsız / ölçüm cihazı sorunu / e-imza cihazı sorunu). Sistem birini
  seçip kendinden emin cevapladı, sormadı. Yanlış bilgi vermedi ama ideal
  de değil. page-context bunu büyük ölçüde çözecek.

## Bulunan doküman boşlukları (bug değil, içerik eksikliği)

- Muayeneleri onaylayan kişi otomatik olarak nasıl değiştirilir?
  Sistem doğru şekilde "bulunamadı" dedi, uydurmadı. En yakın konu
  (ekipman eşleştirmesi) var ama bu soruya açıkça bağlanmamış. Ya
  doğrudan sorup ekleriz ya da Faz 3'teki destek-talebi RAG'ine bırakırız.