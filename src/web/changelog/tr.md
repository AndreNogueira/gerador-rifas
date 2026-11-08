# Changelog (Türkçe özet)

`../CHANGELOG.md` dosyasının çevrilmiş özeti: aynı sürümler, bölümler ve maddeler, daha kısa. Tam metin Portekizcedir.

## 3.25.0 — 2026-11-08

### Yeni
- **Arama motorları için dil başına bir adres:** her dilin kendi adresi (/en, /ja/tutorial…) ve o dilde başlık, açıklama ve metni var; site Google'a hangi sürümlerin eşdeğer olduğunu bildirir (hreflang). Portekizce / adresinde kalır. Seçilen dil artık adres çubuğunda görünür.

## 3.24.1 — 2026-11-08

### İyileştirildi
- **Onay kutuları hizalandı:** «Seri başına bir renk» ve diğer kutular artık kartın öbür ucunda değil, metinlerinin yanında.

## 3.24.0 — 2026-11-08

### İyileştirildi
- **Siteden ekran görüntüleriyle eğitim:** eğitimin temel konuları artık Windows uygulaması yerine sitenin kendisini, 18 dilin hepsinde gösteriyor.

## 3.23.0 — 2026-11-08

### Yeni
- **Her özellik için eğitim ve video:** eğitimde her özellik için bir konu var (seriler, liste ve kontrol çizelgesi, kesim işaretleri, galeri, kendi markanız, QR, çekiliş, kaydetme ve paylaşma, uygulama olarak yükleme, temalar); her birinin arayüzün kendisinde kaydedilmiş kısa bir videosu var, Portekizce ve İngilizce.
- **Changelog, Koşullar, Gizlilik ve İletişim 18 dilde:** metin seçilen dilde görünür. Changelog'da her sürümün çevrilmiş bir özeti var (tamamı Portekizce); hukuki metinler anadili konuşanlarca denetlenmemiş çevirilerdir ve fark olursa Portekizce sürüm geçerlidir.
- **Windows uygulaması 2.4:** sitenin 3.10'dan beri kazandıklarıyla — seriler, önekler ve seri başına renk, atlanan numaralar, numara rengi, logo, kesim işaretleri, şablon galerisi, doğrulanabilir çekiliş ve listenin (CSV) ve kontrol çizelgesinin dışa aktarılması içeren «Ekstralar» menüsü; ayrıca Aralık'ta otomatik Noel görünümü. Doğrulama QR'ı ve uygulama olarak yükleme yalnızca sitede kalır.

## 3.22.0 — 2026-11-08

### İyileştirildi
- **9 temanın kontrastı gerçekten ölçüldü:** bir tarayıcı testi metni gerçek arka plan piksellerine karşı, açık ve koyu modda ölçer (WCAG AA); geçmeyenler düzeltildi.
- Adımların büyük süs numaraları artık ekran okuyucularca okunmuyor.

## 3.21.0 — 2026-11-08

### Yeni
- **Doğrulanabilir çekiliş** («Çekiliş» sayfası): herkesin tekrarlayıp aynı sonucu bulabileceği şekilde, herkese açık bir tohumla, bir aralıktan (atlanacak numaralarla) numara çeker. Hepsi tarayıcıda olur ve «Bağlantıyı kopyala» aynı çekilişi paylaşır.
- Yöntem adım adım belgelenmiştir; site ile aynı numaraları veren bir referans uygulaması vardır.

## 3.20.0 — 2026-11-08

### Yeni
- **Her bilette QR:** her biletin bir köşesinde doğrulama QR kodu (tek biletli şablonlar), köşe ve boyut seçimiyle. Okutunca, bu hizmetin kodu o bilet için verdiğini doğrulayan bir sayfa açılır. Yalnızca sunucuda bulunan bir anahtarla imzalanır; veritabanı yoktur. Ödemeyi ya da kazanmayı kanıtlamaz.
- Yalnızca hizmet sahibi anahtarı ayarlayınca görünür. QR'lı isteklerde üst sınır 10.000 numaradır.

## 3.19.0 — 2026-11-08

### Yeni
- **Kendi markanız:** numaraların rengi (her şablon; seri rengi önceliklidir) ve derneğin **logosu** her biletin üzerinde (2 MB'a kadar PNG veya JPG, tek biletli şablonlar), köşe ve boyutla (%10–40). PNG saydamlığını korur.
- Logo yalnızca oturumda kalır (oturumla ve «Hepsini temizle» ile silinir) ve önizlemede görünür.

## 3.18.0 — 2026-11-08

### Yeni
- **Şablon galerisi:** dört tasarımdan birini seçin (Bosque, Quermesse, Natal ve Gala), başlığı, kuruluşu, en çok üç ödülü ve tarihi yazın, önizlemeye bakın ve «Bu şablonu kullan»a basın: şablon ve rakamlar hazırdır. Her tasarım koçanlı bir bilettir.
- Tasarımlar bu projeye özgüdür, özgür Vera yazı tipiyle. Yazı tipinde yalnızca Latin alfabesi vardır: başka harflerde uyarı çıkar.

## 3.17.0 — 2026-11-08

### Yeni
- **Kesim işaretleri:** sayfa panelindeki bir kutu (tek biletli şablonlar), her kesim çizgisini uzatan kısa çizgileri kenar boşluklarına çizer. En az 3 mm kenar boşluğu ister.
- **Koçan** (her biletteki numaranın iki kez yazılması) zaten çalışıyordu: artık test edildi ve belgelendi.
- **Taşma payı** zaten dikkate alınıyor: Canva PDF'sinin TrimBox'ı sayfadan küçükse bilet yalnızca içinde kalan kısımdır.

## 3.16.0 — 2026-11-08

### Yeni
- **Bilet listesini dışa aktarma (CSV):** Excel veya Calc için bir dosya, satır başına bir bilet (seri, numara ve boş Ad, İletişim, Ödendi sütunları); önekleri, serileri ve atlanan numaraları gözetir.
- **Satış kontrol çizelgesi (PDF):** yazdırılıp elle doldurulacak bir A4 tablo (sayfada 36 bilet, «ödendi» kutusuyla). PDF'in harflerini yazamadığı dillerde başlıklar İngilizce çıkar.
- Sunucuda hiçbir şey saklanmaz: liste yalnızca formdan çıkar.

## 3.15.0 — 2026-11-08

### Yeni
- **Seriler ve önekler:** rakamların önüne metin (A- ile A-0001). Virgülle ayrılmış birden çok seride her biri aralığı yineler ve kendi PDF'lerini alır. Önek harf, boşluk, nokta, tire ve eğik çizgi kabul eder (en çok 6 karakter, rakam yok).
- **Numara atlama:** 13, 100-110 bu numaraları diziden çıkarır (özet, dosyalar ve doğrulama yalnızca basılanı sayar).
- **Her seri için bir renk.**
- Bunların hepsi «Bağlantıyı kopyala»ya ve önizlemeye de girer.

## 3.14.0 — 2026-11-08

### Yeni
- **Uygulama olarak yükleme (PWA):** siteyi telefona veya bilgisayara yükleyin; uygulama kabuğu çevrimdışıyken de açılır (üretim hâlâ sunucuyu ister). Basit bir service worker yalnızca sayfayı, uygulama dosyalarını ve arayüz metinlerini saklar; dosyalarınıza ve üretim isteklerine asla dokunmaz.

## 3.13.0 — 2026-11-08

### Yeni
- **Rakam dosyasını hatırlama:** gelecek yıl dönen onu yinelemez. Yalnızca tarayıcınızda kalır (asla sunucuda) ve yeni şablonla yeniden kullanılır; başkasını seçmek onu değiştirir, «Hepsini temizle» siler.
- **Bağlantıyı kopyala:** form değerlerini (başlangıç, bitiş, mod, dosya başına en çok, kâğıt, kenar boşluğu ve ad) içeren bir bağlantıyı kopyalayan düğme. Açan aynı değerleri görür; dosyalar asla bağlantıya girmez.

## 3.12.0 — 2026-11-08

### Yeni
- Alt bilgide bağlantılı **Kullanım koşulları**, **Gizlilik politikası** ve **İletişim** sayfaları. Hizmet ücret almadan önce hukuki destekle gözden geçirilmesi gereken geçici sürümlerdir.
- Alt bilgide **bağış düğmesi**: yalnızca sahibi bağlantıyı ayarlayınca görünür. İletişim e-postası ve sorumlunun adı da koddan değil, sunucu yapılandırmasından gelir.

## 3.11.0 — 2026-11-08

### Yeni
- Yönetim panelinde **kullanım hunisi**: her aşamada kaç olay var (oturum, şablon, rakamlar, önizleme, üretim, indirme) ve önceki aşamanın ne kadarı sonrakine ulaştı. İnsanların nerede bıraktığını gösterir. Kişileri değil, olayları sayar.

## 3.10.0 — 2026-11-08

### Yeni
- Bu sayfa: değişen her şeyin sürüm sürüm yer aldığı **Changelog**.
- **Aralık** ayında otomatik görsel tema **Noel**'dir (hiç tema seçmemiş olanlar için). Başka tema seçmek yine hatırlanır.

### İyileştirildi
- Sunucuda bir bağımlılık daha az (`python-multipart` artık kullanılmıyordu: dosyalar ham gövde olarak gelir).

## 3.9.0 — 2026-11-08

### Yeni
- **Büyük ekranlar** (4K, ultra geniş) ve **yeni telefonlar** için düzen: kompakt başlık ve 44 px düğmeler.
- Tarayıcı sayfa içinde PDF gösteremediğinde önizleme bir görüntü gösterir (Android'de Chrome).
- Yönetim paneli kişisel hiçbir şey saklamadan **ekran türünü** (sınıf, boyut, aile) kaydeder.
- Hizmet uyumasın diye kendini her 10 dakikada bir çağırır.

## 3.8.0 — 2026-11-08

### Yeni
- **Yönetim paneli** (yalnızca sahibi için, parolalı): sistem ve kullanıma ilişkin grafikler ve açıklamalar; yalnızca toplamlar, asla kişisel veri.

## 3.7.0 — 2026-11-08

### Yeni
- **SEO**: sayfa başına başlık, açıklama ve metin, `robots.txt`, `sitemap.xml` ve var olmayan sayfalar için gerçek 404.

## 3.6.0 — 2026-11-08

### İyileştirildi
- Site **tek bir JavaScript dosyası** sunar, karartılmış ve önceden sıkıştırılmış: iletilen miktar eskisinden çok daha küçük.

## 3.5.0 — 2026-11-08

### Yeni
- **Matrix Gamer** görsel teması: yağan yeşil karakterler ve neon parıltı.

## 3.4.0 — 2026-11-08

### İyileştirildi
- Stiller **Sass**'a geçti ve **tek bir CSS** olarak çıkıyor. Sayfa yapısı her temada aynıdır: tema yalnızca renkleri ve biçimlendirmeyi değiştirir.

## 3.3.0 — 2026-11-07

### Yeni
- **Görsel temalar**: Premiado (yeni varsayılan görünüm) ve yedi tane daha (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala ve Natal), her biri açık ve koyu.
- Yeni uygulama simgesi.
