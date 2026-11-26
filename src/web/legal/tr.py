"""Koşullar, gizlilik ve iletişim Türkçe: `pt.py` çevirisi (aynı sayfalar, bölümler, paragraflar ve {yer tutucular}). Anadili konuşanlarca denetlenmedi; Portekizce geçerlidir."""
FRASES = {
    "responsavel_com": "Hizmeti {nome} yönetir.",
    "responsavel_sem": "Hizmeti yazarı, yani onu çevrimiçi sunan kişi yönetir.",
    "contacto_com": "Bize {email} adresinden ulaşabilirsiniz.",
    "contacto_sem": "Şu anda herkese açık bir iletişim yok.",
    "contacto_pagina_com": "Sorular, hatalar ya da öneriler için {email} adresine yazın.",
    "contacto_pagina_sem": "Şu anda herkese açık bir iletişim yok. Bu sayfaya daha sonra tekrar bakın.",
    "atualizado": "21 Kasım 2026",
}

AVISO = ("Geçici sürüm; hukuki destekle gözden geçirilmelidir. Burada bir şey hizmetin yaptığından farklıysa düzeltmemizi isteyin. "
         "Bu, anadili konuşanlarca denetlenmemiş bir çeviridir: sürümler farklıysa Portekizce sürüm geçerlidir.")

TEXTOS = {
    "termos": {
        "titulo": "Kullanım koşulları",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Bu hizmet nedir",
             "paragrafos": ["Bilet Üreticisi, bir PDF şablondan yazdırmaya hazır, numaralı çekiliş biletleri oluşturur. Yalnızca bunu yapar: bilet satmaz, "
                            "para almaz, katılımcı listesi tutmaz ve hukuki değeri olan çekiliş yapmaz.",
                            "{responsavel}"]},
            {"titulo": "Çekilişi düzenleyen ondan sorumludur",
             "paragrafos": ["Çekilişler, tombalalar ve piyangolar duruma göre değişen yasal kurallara tabidir (örneğin belediye izinleri ve dernekler için kurallar). "
                            "Çekilişi düzenleyen, yasaya uymaktan, ücret tahsil etmekten ve ödülleri teslim etmekten tek başına sorumludur. Bu hizmet hukuki danışmanlık vermez."]},
            {"titulo": "İzin verilen kullanım",
             "paragrafos": ["Hizmet ücretsizdir ve makul kullanım içindir. Sahtekârlık biletleri üretmek ya da sunucuyu aşırı yüklemek için kullanılamaz: dosya boyutuna, "
                            "istek başına numaraya ({max_numeros}) ve dakikada isteğe sınırlar vardır; aynı anda yalnızca bir üretim yapılır."]},
            {"titulo": "Dosyalarınız",
             "paragrafos": ["Şablon ve rakamlar yalnızca biletlerinizi üretmeye yarar ve {validade} dakika etkinlik olmazsa ya da «Hepsini temizle»ye bastığınızda sunucudan silinir. "
                            "Başka hiçbir şey için kullanmayız. Sizin kalırlar: yalnızca yüklediklerinizi kullanma hakkınız olmalıdır (görseller, yazı tipleri, logolar)."]},
            {"titulo": "Garanti yok",
             "paragrafos": ["Hizmet «olduğu gibi» sunulur; her zaman erişilebilir ya da hatasız olacağına dair garanti yoktur. Yazdırmadan önce PDF'leri her zaman kontrol edin (hizmet "
                            "üretilen numaraları doğrular, ancak son kontrol size aittir). Yasanın izin verdiği ölçüde, hizmetin kullanımına bağlı zararlardan sorumlu değiliz."]},
            {"titulo": "Değişiklikler",
             "paragrafos": ["Bu koşullar değişebilir; son güncelleme tarihi {atualizado}. Hizmet bir gün ücretli olursa, ücret almadan önce bu açıkça söylenecektir."]},
            {"titulo": "İletişim", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Gizlilik politikası",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Özet",
             "paragrafos": ["Hesap, reklam ve üçüncü taraf izleme aracı yoktur. Dosyalarınız {validade} dakika içinde sunucudan silinir. "
                            "Kullanım istatistikleri yalnızca toplu sayılardır."]},
            {"titulo": "Hangi verileri işleriz",
             "paragrafos": ["Yüklediğiniz dosyalar (şablon ve rakamlar) yalnızca biletleri üretmek için işlenir, sunucuda geçici bir klasörde durur ve {validade} dakika etkinlik olmazsa "
                            "ya da «Hepsini temizle»ye bastığınızda silinir.",
                            "Hizmetin nasıl kullanıldığını bilmek için sayımlar kaydederiz: kaç ziyaret, üretim ve indirme, seçilen dil ve tema ile ekran türü. "
                            "Ziyaretin ülkesini de kaydederiz (yalnızca kodu, örneğin «PT»); bunu barındırma ağı IP adresinden çıkarır, IP'nin kendisini saklamayız. IP adreslerini, dosya adlarını, dosya içeriğini ve tarayıcının tam kimliğini asla kaydetmeyiz.",
                            "IP adresi yalnızca bellekte, bir an için, dakikadaki istek sayısını sınırlamak amacıyla kullanılır ve bizce saklanmaz. Barındırma sağlayıcısı "
                            "(Frankfurt'taki Render, Avrupa Birliği) teknik kayıtlarında IP adreslerini tutabilir."]},
            {"titulo": "Tarayıcınızda",
             "paragrafos": ["Tarayıcınızda (yerel depolama) tercihlerinizi saklarız: dil, görsel tema, açık veya koyu mod ve formun son değerleri. "
                            "Yıldan yıla işi tekrarlamamanız için rakam dosyası da tarayıcınızda kalabilir (asla sunucumuzda değil); «Hepsini temizle» onu siler. "
                            "Reklam ya da izleme çerezleri kullanmayız."]},
            {"titulo": "Hukuki dayanak ve saklama",
             "paragrafos": ["Bu verileri, hizmeti sunma ve güvenli tutma konusundaki meşru menfaat temelinde işleriz (GDPR, madde 6/1-f). Dosyalar dakikalarca durur; "
                            "toplu sayımlar kimseyi tanımlamaz."]},
            {"titulo": "Haklarınız",
             "paragrafos": ["Erişim, düzeltme, silme ve itiraz hakkınız ile veri koruma otoritenize şikâyet hakkınız vardır (Portekiz'de CNPD, cnpd.pt). "
                            "Sizi tanımlayan veri saklamadığımız için pratikte erişilecek ya da silinecek az şey vardır; sorunuz varsa bize ulaşın."]},
            {"titulo": "Kim sorumludur", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Güncelleme", "paragrafos": ["Son güncelleme: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "İletişim",
        "aviso": "",
        "seccoes": [
            {"titulo": "Bize yazın",
             "paragrafos": ["{contacto_pagina}",
                            "Bir hata bulursanız ne yaptığınızı ve ne beklediğinizi yazın; kişisel veri içeriyorsa şablonunuzu göndermeyin."]},
        ],
    },
}
