"""Ketentuan, privasi dan kontak dalam bahasa Indonesia: terjemahan `pt.py` (halaman, bagian, paragraf dan {penanda} yang sama). Belum ditinjau penutur asli; versi Portugis yang berlaku."""
FRASES = {
    "responsavel_com": "Layanan ini dikelola oleh {nome}.",
    "responsavel_sem": "Layanan ini dikelola oleh pembuatnya, orang yang menyediakannya secara daring.",
    "contacto_com": "Anda dapat menghubungi kami di {email}.",
    "contacto_sem": "Saat ini belum ada kontak publik.",
    "contacto_pagina_com": "Untuk pertanyaan, kesalahan atau saran, tulis ke {email}.",
    "contacto_pagina_sem": "Saat ini belum ada kontak publik. Silakan kembali ke halaman ini nanti.",
    "atualizado": "21 November 2026",
}

AVISO = ("Versi sementara, yang masih perlu ditinjau dengan dukungan hukum. Jika ada yang di sini berbeda dari yang dilakukan layanan, mohon beri tahu kami agar kami perbaiki. "
         "Ini adalah terjemahan tanpa tinjauan penutur asli: jika versinya berbeda, versi Portugis yang berlaku.")

TEXTOS = {
    "termos": {
        "titulo": "Ketentuan penggunaan",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Layanan apa ini",
             "paragrafos": ["Pembuat Undian membuat, dari templat PDF, tiket undian bernomor yang siap dicetak. Hanya itu yang dilakukannya: layanan ini tidak menjual tiket, "
                            "tidak menerima uang, tidak menyimpan daftar peserta dan tidak menyelenggarakan pengundian yang bernilai hukum.",
                            "{responsavel}"]},
            {"titulo": "Penyelenggara undian bertanggung jawab atasnya",
             "paragrafos": ["Undian, tombola dan pengundian tunduk pada aturan hukum (misalnya izin dari pemerintah daerah dan aturan untuk organisasi) yang berbeda-beda "
                            "menurut kasusnya. Penyelenggara undian bertanggung jawab sepenuhnya untuk mematuhi hukum, menagih pembayaran dan menyerahkan hadiah. "
                            "Layanan ini tidak memberikan nasihat hukum."]},
            {"titulo": "Penggunaan yang diizinkan",
             "paragrafos": ["Layanan ini gratis dan untuk penggunaan yang wajar. Layanan tidak boleh dipakai untuk membuat tiket penipuan atau membebani server: ada batas ukuran berkas, "
                            "jumlah nomor per permintaan ({max_numeros}) dan permintaan per menit, serta hanya satu pembuatan dalam satu waktu."]},
            {"titulo": "Berkas Anda",
             "paragrafos": ["Templat dan angka hanya dipakai untuk membuat tiket Anda dan dihapus dari server setelah {validade} menit tanpa aktivitas, "
                            "atau saat Anda menekan “Bersihkan semua”. Kami tidak memakainya untuk hal lain. Berkas tetap milik Anda: Anda hanya perlu memiliki hak untuk memakai apa yang Anda unggah "
                            "(gambar, font, logo)."]},
            {"titulo": "Tanpa jaminan",
             "paragrafos": ["Layanan ini disediakan “apa adanya”, tanpa jaminan selalu tersedia atau bebas kesalahan. Selalu periksa PDF sebelum mencetak (layanan "
                            "memverifikasi nomor yang dibuat, tetapi pemeriksaan akhir ada pada Anda). Sejauh diizinkan hukum, kami tidak bertanggung jawab atas kerugian yang terkait dengan penggunaan layanan."]},
            {"titulo": "Perubahan",
             "paragrafos": ["Ketentuan ini dapat berubah; tanggal pembaruan terakhir adalah {atualizado}. Jika layanan ini suatu saat berbayar, hal itu akan dinyatakan dengan jelas sebelum ada penagihan."]},
            {"titulo": "Kontak", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Kebijakan privasi",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Ringkasan",
             "paragrafos": ["Tidak ada akun, tidak ada iklan dan tidak ada alat pelacak pihak ketiga. Berkas Anda dihapus dari server dalam {validade} menit. "
                            "Statistik penggunaan hanya berupa angka agregat."]},
            {"titulo": "Data apa yang kami proses",
             "paragrafos": ["Berkas yang Anda unggah (templat dan angka) hanya diproses untuk membuat tiket, berada di folder sementara di server dan dihapus "
                            "setelah {validade} menit tanpa aktivitas atau saat Anda menekan “Bersihkan semua”.",
                            "Untuk mengetahui bagaimana layanan dipakai, kami mencatat hitungan: berapa kunjungan, pembuatan dan unduhan, bahasa dan tema yang dipilih serta jenis layar. "
                            "Kami juga mencatat negara kunjungan (hanya kodenya, misalnya «PT»), yang disimpulkan jaringan hosting dari alamat IP; IP itu sendiri tidak kami simpan. Kami tidak pernah mencatat alamat IP, nama berkas, isi berkas atau identitas lengkap browser.",
                            "Alamat IP hanya dipakai di memori, sesaat, untuk membatasi jumlah permintaan per menit, dan tidak kami simpan. Penyedia hosting "
                            "(Render, di Frankfurt, Uni Eropa) dapat mencatat alamat IP dalam log teknisnya."]},
            {"titulo": "Di browser Anda",
             "paragrafos": ["Kami menyimpan preferensi Anda di browser (penyimpanan lokal): bahasa, tema visual, mode terang atau gelap, dan nilai formulir terakhir. Agar Anda tidak "
                            "mengulang pekerjaan dari tahun ke tahun, berkas angka juga dapat disimpan di browser Anda (tidak pernah di server kami); “Bersihkan semua” menghapusnya. "
                            "Kami tidak memakai cookie iklan atau pelacakan."]},
            {"titulo": "Dasar hukum dan retensi",
             "paragrafos": ["Kami memproses data ini berdasarkan kepentingan sah kami untuk menyediakan layanan dan menjaganya tetap aman (GDPR, Pasal 6(1)(f)). "
                            "Berkas hanya bertahan beberapa menit; hitungan agregat tidak mengidentifikasi siapa pun."]},
            {"titulo": "Hak Anda",
             "paragrafos": ["Anda berhak atas akses, perbaikan, penghapusan dan keberatan, serta mengajukan pengaduan ke otoritas perlindungan data Anda (di Portugal, "
                            "CNPD, cnpd.pt). Karena kami tidak menyimpan data yang mengidentifikasi Anda, dalam praktiknya hanya sedikit yang dapat diakses atau dihapus; jika ragu, hubungi kami."]},
            {"titulo": "Siapa yang bertanggung jawab", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Pembaruan", "paragrafos": ["Terakhir diperbarui: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Kontak",
        "aviso": "",
        "seccoes": [
            {"titulo": "Hubungi kami",
             "paragrafos": ["{contacto_pagina}",
                            "Jika Anda menemukan kesalahan, beri tahu kami apa yang Anda lakukan dan apa yang Anda harapkan; jangan kirim templat Anda jika berisi data pribadi."]},
        ],
    },
}

ANUNCIOS = {
    "resumo": "Tidak ada akun. Situs ini menampilkan iklan Google (AdSense), yang dapat memakai cookie; selain itu, kami tidak memakai alat pelacak pihak ketiga.",
    "cookies": "Satu-satunya cookie iklan adalah cookie dari iklan tersebut (lihat “Iklan”).",
    "seccao": {
        "titulo": "Iklan",
        "paragrafos": [
            "Situs ini menampilkan iklan Google (AdSense) untuk membiayai dirinya sendiri. Google dan mitranya dapat memakai cookie dan pengenal untuk menampilkan iklan, yang dipersonalisasi atau tidak, serta mengukur hasilnya; kami tidak menerima data tersebut dan tidak mengaitkannya dengan berkas Anda.",
            "Iklan hanya muncul setelah Anda memilih pada pesan persetujuan yang ditampilkan Google saat Anda membuka situs (wajib di Wilayah Ekonomi Eropa dan Britania Raya); dasar hukum cookie iklan adalah persetujuan Anda (GDPR, Pasal 6(1)(a)), dan Anda dapat meninjau pilihan Anda pada opsi privasi pesan tersebut. Iklan tidak pernah muncul di berkas yang dibuat, di dasbor atau di aplikasi Windows.",
            "Pelajari cara Google menggunakan data di policies.google.com/technologies/partner-sites dan kelola iklan yang dipersonalisasi di adssettings.google.com.",
        ],
    },
}

PARTILHAS = {"titulo": "Desain yang dibagikan", "paragrafos": [
    "Jika Anda menekan “Bagikan lewat tautan” di Editor templat, desain (bentuk, teks dan warna, tanpa gambar) disimpan di server kami, dengan alamat yang sulit ditebak, selama 90 hari setelah akses terakhir, dan siapa pun yang memiliki tautan dapat membukanya. Kami tidak menyimpan alamat IP Anda atau data lain tentang siapa yang membagikan: jangan menulis data pribadi atau rahasia di desain. Desain yang tidak Anda bagikan hanya dikirim ke server untuk membuat templat dan dihapus bersama sesi."]}

OPINIAO = {"titulo": "Komentar dan masalah yang dilaporkan", "paragrafos": [
    "Jika Anda meninggalkan komentar di halaman «Komentar», kami menyimpan teks, tanggal, negara asal pengiriman (misalnya PT, diberikan oleh jaringan hosting; kami tidak menyimpan alamat IP) dan nama yang Anda pilih untuk ditampilkan (tidak ada, jika Anda ingin anonim; jika Anda meminta nama ditampilkan tetapi mengosongkannya, tampil «Pengunjung no. …»). Teks dan nama terlihat oleh semua orang; negara hanya dilihat pengelola situs. Untuk mencegah penyalahgunaan, server menghitung di memori, selama satu jam, berapa komentar yang datang dari setiap alamat, tanpa menyimpannya. Jangan menulis data pribadi di komentar; untuk menghapusnya, hubungi kami (lihat Kontak).",
    "Jika Anda melaporkan masalah, teks yang Anda tulis (dan, jika Anda mencentang opsi itu, versi aplikasi, bahasa, peramban, dan layar) dikirim ke GitHub proyek, tempat teks itu dicatat dan terlihat oleh tim. Alamat IP Anda tidak dikirim. Jangan menulis data pribadi atau kata sandi.",
]}
