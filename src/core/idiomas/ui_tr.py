T = {
    "m_ficheiro": "Dosya", "m_ver": "Görünüm", "m_idioma": "Dil", "m_ajuda": "Yardım",
    "mi_abrir_template": "Şablonu aç…", "mi_abrir_alg": "Rakam dosyasını seç…",
    "mi_destino": "Hedef klasörü seç…", "mi_sair": "Çıkış",
    "mi_zoom_mais": "Yakınlaştır", "mi_zoom_menos": "Uzaklaştır", "mi_ajustar": "Pencereye sığdır",
    "mi_expandir": "Önizlemeyi genişlet", "mi_reduzir": "Önizlemeyi küçült",
    "mi_tema": "Tema", "mi_tema_sistema": "Windows ile aynı", "mi_tema_claro": "Açık", "mi_tema_escuro": "Koyu",
    "mi_tutorial": "Adım adım öğretici", "mi_sobre": "Hakkında…",
    "sobre_texto": ("{app}\nSürüm {versao}\n\nCanva şablonundan numaralı çekiliş biletlerini PDF olarak oluşturur.\n\n"
                    "pypdf, pypdfium2, Pillow ve CustomTkinter kütüphanelerini kullanır (serbest lisanslar)."),
    "tip_tema": "Açık / koyu tema arasında geçiş yap",
    "tut_titulo": "Öğretici", "tut_ant": "Geri", "tut_seg": "İleri",
    "tut_t0": "Genel bakış",
    "tut_b0": ("Bu program Canva’da hazırladığınız çekiliş tasarımını alır ve istediğiniz numaralarla yazdırmaya hazır "
               "PDF’ler oluşturur.\n\n"
               "Soldaki sırayla yalnızca 4 adım var:\n\n"
               "• 1 – şablonu seçin (Canva’dan PDF);\n"
               "• 2 – 0’dan 9’a rakamların bulunduğu dosyayı seçin;\n"
               "• 3 – hangi numaradan hangisine kadar olacağını ve birden çok PDF mi tek PDF mi istediğinizi belirtin;\n"
               "• 4 – klasörü seçin ve dosya adını yazın.\n\n"
               "Sonra bir sayfayı görmek için “{previa}”, ardından “{gerar}” düğmesine tıklayın. "
               "Sonunda her PDF otomatik olarak denetlenir."),
    "tut_b1": ("Canva’da çekilişi tasarlayın ve her bilete 0001, 0002, 0003, … örnek numaralarını yazın "
               "(bilet başına bir tane). Her numara 2 kez geçer: biri koçanda, biri biletin ana bölümünde "
               "(resme bakın).\n\n"
               "PDF olarak indirin ve bu dosyayı 1. adımda seçin.\n\n"
               "• Program, sayfada kaç bilet olduğunu ve koçan metninin yönünü kendisi algılar.\n"
               "• Numaralar resim değil, metin olmalıdır.\n"
               "• Tasarımdaki diğer sayılar (yıl, telefon…) olduğu gibi kalır.\n"
               "• PDF’nin yalnızca 1. sayfası kullanılır."),
    "tut_b3": ("• {de} / {ate}: oluşturulacak ilk ve son numara (örneğin 1’den 1000’e).\n"
               "• {algarismos}: kaç basamakla yazılacağı (4 → 0001). Varsayılan, şablondaki basamak sayısıdır; "
               "daha fazlasını isterseniz numaralar sığması için küçülür.\n"
               "• {varios}: en fazla belirttiğiniz sayıda numara içeren dosyalara böler (sayfa başına bilet sayısının katı).\n"
               "• {unico}: her şey tek dosyada.\n\n"
               "Aşağıda özeti görürsünüz: kaç numara, dosya ve sayfa oluşturulacak."),
    "tut_b4": ("PDF’lerin kaydedileceği klasörü seçin ve dosya adını yazın (zorunlu; program asla ad önermez). "
               "Dosyalar “AD - 0001 - 0300.pdf”, “AD - 0301 - 0600.pdf”, … ya da tek PDF’de yalnızca "
               "“AD - 0001 - 1000.pdf” olarak kaydedilir.\n\n"
               "Bu adlarda dosyalar zaten varsa program, değiştirmeden önce sorar."),
    "tut_t5": "Önizleme ve oluşturma",
    "tut_b5": ("“{previa}” 1. sayfayı gerçek numaralarla gösterir; böylece her şeyi oluşturmadan önce yazı tipini, "
               "boyutu ve konumu kontrol edebilirsiniz.\n\n"
               "Görüntüleyicide:\n"
               "• − / + veya Ctrl + fare tekerleği: yakınlaştırma;\n"
               "• taşımak için sürükleyin; çift tıklama veya “{ajustar}”: tüm sayfayı gör;\n"
               "• genişlet düğmesi tüm pencereyi önizlemeye verir; geri dönmek için yeniden tıklayın;\n"
               "• ayarlar ile görüntüleyici arasındaki ayırıcı da sürüklenebilir.\n\n"
               "“{gerar}” düğmesine tıklayın. Çubuk ilerlemeyi gösterir (iptal edebilirsiniz). Sonunda her PDF "
               "otomatik olarak denetlenir (sayfalar ve numaralar) ve “{pasta}” düğmesi görünür."),
    "tut_t6": "İpuçları ve sorunlar",
    "tut_b6": ("• “Örnek numaralar bulunamadı”: Canva’da numaralar metin olmalı ve 0001, 0002, … biçiminde yazılmalı "
               "(her biri 2 kez).\n"
               "• Numaralar başka yazı tipiyle çıkıyor: rakam dosyası, şablonla tam olarak aynı yazı tipini "
               "kullanmalı. Önizlemede kontrol edin.\n"
               "• Numaralar çok küçük ya da tuhaf: PNG/JPG ile büyük bir resim kullanın (≥ 100 px yükseklik); PDF her zaman daha iyidir.\n"
               "• “Kaydedilemedi”: PDF başka bir programda açıksa kapatın.\n"
               "• Tasarımdan fazla basamak: boyut otomatik küçülür (günlükte uyarı görünür).\n"
               "• Dili ve temayı (açık/koyu) menülerden değiştirebilirsiniz; renkler Windows’u izler."),
    'err_folha_varias': 'Sayfada yalnızca tek biletli bir şablon çoğaltılabilir.',
    'err_rifa_grande': 'Bilet ({w} × {h} mm), {margem} mm kenar boşluklu bir {papel} kâğıdına sığmıyor.\n\nDaha büyük bir kâğıt seçin, kenar boşluğunu küçültün veya daha küçük bir bilet tasarlayın.',
    'log_folha': '{papel} kâğıdı: sayfa başına {n} bilet (her biri {w} × {h} mm).',
    'aviso_muitas': '⚠ Sayfa başına {n} bilet: çok küçük olacaklar ve kesmesi zor. Bilet boyutunu kontrol edin.',
    'c1_ok_uma': '✔ 1 biletli şablon · örnek numara {primeiro}',
    'lay_info': 'Şablonda tek bilet var: program sayfayı sığabildiği kadar kopyayla doldurur.',
    'lay_papel': 'Kâğıt',
    'lay_margem': 'Kenar boşluğu (mm)',
    'lay_por_folha': 'Sayfa başına bilet',
    'lay_resultado': '{w} × {h} mm bilet → {papel} sayfasında {n} adet (en çok {max})',
    'lay_recortada': ' · tasarıma göre kırpıldı',
    'lay_rodadas': ' · {r} adedi 90° döndürüldü',
    'lay_acima': 'Bir sayfaya en çok {max} sığar.',
    'conf_muitas': 'Sayfa başına {n} bilet üretmek üzeresiniz (her biri {w} × {h} mm). Bu çok fazla: küçük olacaklar ve kesmesi zor.\n\nDevam edilsin mi?',
    'mi_video': 'Video eğitim',
    'video_falta': 'Video bulunamadı ({nome}).',
    'tut_t_uma': 'Şablonda tek bilet',
    'tut_b_uma': 'Tüm sayfayı tasarlamanız gerekmez. Canva’da bir bilet boyutunda sayfa oluşturun (“Özel boyut”, örneğin 19 × 5,5 cm) ve yalnızca bir örnek numara yazın, 0001 (koçanda ve ana kısımda ya da yalnızca bir yerde).\n\nBu PDF’yi seçtiğinizde program tek bilet olduğunu görür ve “{papel}”, “{margem}” ve “{porfolha}” alanlarını gösterir: sayfayı biletin kopyalarıyla doldurur, sığabildiği kadar (böyle daha çok sığıyorsa 90° döndürerek) ve sırayla numaralandırır. Önizleme sayfayı basılacağı gibi gösterir.\n\n• Kâğıt (A4, A3, A5, Letter, Legal) ve kenar boşluğu (yazıcılar kenara kadar basmaz) değiştirilebilir.\n• PDF sayfası biletten büyükse program çizilen alanı kırpar.\n• “{porfolha}” en üst değerle başlar; daha azını isteyebilirsiniz.\n• Çok sayıda bilet sığıyorsa (24’ten fazla) program uyarır: küçüktürler ve kesmesi zordur.\n• PDF’nizde zaten sayfa başına birkaç bilet varsa (0001, 0002, …) her şey eskisi gibi çalışır.',
    'tut_video': 'Video mu tercih edersiniz? “{ajuda}” menüsünü açın › “{video}”.',
    'limpar': 'Hepsini temizle',
    'tut_limpar': 'İş bitince “{limpar}” (veya “{ficheiro}” menüsü › “{limpar}”) her şeyi sıfırlar — şablon, rakamlar, klasör, ad, numaralar ve önizleme — böylece yeni bir çekiliş başlatabilirsiniz.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'İndir',
    'web_demasiado_grande': 'Dosya sınırdan büyük ({mb} MB).',
    'web_ocupado': 'Zaten bir oluşturma işlemi sürüyor. Birazdan tekrar deneyin.',
    'web_voltar': 'Geri',
    'web_ficheiros_gerados': "Oluşturulan PDF'ler",
    'web_nova_janela': 'Yeni pencerede aç',
    'web_tema_auto': 'Otomatik',
    'web_sessao_expirada': 'Oturum sona erdi (veya sunucu yeniden başlatıldı). Dosyalarınızı yeniden yükleyin.',
    'web_erro_rede': 'Sunucuya ulaşılamadı. Bağlantınızı kontrol edip yeniden deneyin.',
})
T.update({'web_demasiados': 'Her istekte en fazla {max} numara.'})
