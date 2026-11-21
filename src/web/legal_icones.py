"""O que a Política de privacidade diz sobre as imagens dos artigos do preçário: vêm de bibliotecas de ícones livres, duas das quais pedem crédito.

`textos_legais` acrescenta, no fim da página, uma secção «Imagens do preçário» com o crédito às bibliotecas que o exigem (Twemoji, CC BY 4.0; OpenMoji,
CC BY-SA 4.0); o mesmo crédito aparece também no rodapé do PDF gerado, só quando uma imagem dessas é usada de verdade (`core.precario_catalogo.texto_creditos`).
As outras duas (Noto Emoji, Fluent Emoji) não exigem crédito, por isso não são aqui mencionadas por obrigação, só por transparência.
"""
from __future__ import annotations

TEXTOS: dict[str, dict] = {
    "pt": {"titulo": "Imagens do preçário", "paragrafos": [
        "As imagens à escolha para os artigos do preçário vêm de bibliotecas de ícones livres: o Noto Emoji (Google) e o Fluent Emoji (Microsoft), que não exigem crédito, e o Twemoji e o OpenMoji, que exigem. Esse crédito aparece aqui e, quando usa uma dessas imagens, no rodapé do PDF gerado: Twemoji (CC BY 4.0, Copyright Twitter, Inc e colaboradores) e OpenMoji (CC BY-SA 4.0).",
    ]},
    "en": {"titulo": "Price list images", "paragrafos": [
        "The pictures you can choose for price list items come from free icon libraries: Noto Emoji (Google) and Fluent Emoji (Microsoft), which don't require credit, and Twemoji and OpenMoji, which do. That credit appears here and, when you use one of those pictures, in the footer of the generated PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc and contributors) and OpenMoji (CC BY-SA 4.0).",
    ]},
    "es": {"titulo": "Imágenes del preçario", "paragrafos": [
        "Las imágenes a elegir para los artículos del preçario vienen de bibliotecas de iconos libres: Noto Emoji (Google) y Fluent Emoji (Microsoft), que no exigen crédito, y Twemoji y OpenMoji, que sí. Ese crédito aparece aquí y, cuando usa una de esas imágenes, en el pie del PDF generado: Twemoji (CC BY 4.0, Copyright Twitter, Inc y colaboradores) y OpenMoji (CC BY-SA 4.0).",
    ]},
    "fr": {"titulo": "Images du tarif", "paragrafos": [
        "Les images au choix pour les articles du tarif proviennent de bibliothèques d'icônes libres : Noto Emoji (Google) et Fluent Emoji (Microsoft), qui n'exigent pas de crédit, et Twemoji et OpenMoji, qui l'exigent. Ce crédit apparaît ici et, lorsque vous utilisez l'une de ces images, dans le pied de page du PDF généré : Twemoji (CC BY 4.0, Copyright Twitter, Inc et contributeurs) et OpenMoji (CC BY-SA 4.0).",
    ]},
    "de": {"titulo": "Bilder der Preisliste", "paragrafos": [
        "Die zur Auswahl stehenden Bilder für die Artikel der Preisliste stammen aus freien Symbolbibliotheken: Noto Emoji (Google) und Fluent Emoji (Microsoft), die keine Namensnennung verlangen, sowie Twemoji und OpenMoji, die das tun. Diese Nennung erscheint hier und, wenn Sie eines dieser Bilder verwenden, in der Fußzeile des erzeugten PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc und Mitwirkende) und OpenMoji (CC BY-SA 4.0).",
    ]},
    "it": {"titulo": "Immagini del listino", "paragrafos": [
        "Le immagini tra cui scegliere per gli articoli del listino provengono da raccolte di icone libere: Noto Emoji (Google) e Fluent Emoji (Microsoft), che non richiedono credito, e Twemoji e OpenMoji, che lo richiedono. Questo credito compare qui e, quando usi una di queste immagini, nel piè di pagina del PDF generato: Twemoji (CC BY 4.0, Copyright Twitter, Inc e collaboratori) e OpenMoji (CC BY-SA 4.0).",
    ]},
    "nl": {"titulo": "Afbeeldingen van de prijslijst", "paragrafos": [
        "De afbeeldingen om te kiezen voor de artikelen van de prijslijst komen uit vrije pictogramverzamelingen: Noto Emoji (Google) en Fluent Emoji (Microsoft), die geen vermelding vereisen, en Twemoji en OpenMoji, die dat wel doen. Die vermelding staat hier en, als u een van die afbeeldingen gebruikt, in de voettekst van de gegenereerde PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc en bijdragers) en OpenMoji (CC BY-SA 4.0).",
    ]},
    "pl": {"titulo": "Obrazki cennika", "paragrafos": [
        "Obrazki do wyboru dla pozycji cennika pochodzą z wolnych bibliotek ikon: Noto Emoji (Google) i Fluent Emoji (Microsoft), które nie wymagają podania autora, oraz Twemoji i OpenMoji, które tego wymagają. To wskazanie autora pojawia się tutaj oraz, gdy użyjesz jednego z tych obrazków, w stopce wygenerowanego PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc i współtwórcy) oraz OpenMoji (CC BY-SA 4.0).",
    ]},
    "sv": {"titulo": "Bilder i prislistan", "paragrafos": [
        "Bilderna att välja mellan för prislistans artiklar kommer från fria ikonbibliotek: Noto Emoji (Google) och Fluent Emoji (Microsoft), som inte kräver kreditering, samt Twemoji och OpenMoji, som gör det. Den krediteringen visas här och, när du använder en av dessa bilder, i sidfoten på den genererade PDF-filen: Twemoji (CC BY 4.0, Copyright Twitter, Inc och bidragsgivare) och OpenMoji (CC BY-SA 4.0).",
    ]},
    "cs": {"titulo": "Obrázky ceníku", "paragrafos": [
        "Obrázky na výběr pro položky ceníku pocházejí ze svobodných knihoven ikon: Noto Emoji (Google) a Fluent Emoji (Microsoft), které nevyžadují uvedení autora, a Twemoji a OpenMoji, které ho vyžadují. Toto uvedení se zobrazuje zde a, když použijete jeden z těchto obrázků, v zápatí vygenerovaného PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc a přispěvatelé) a OpenMoji (CC BY-SA 4.0).",
    ]},
    "ro": {"titulo": "Imaginile listei de prețuri", "paragrafos": [
        "Imaginile de ales pentru articolele din lista de prețuri provin din biblioteci libere de pictograme: Noto Emoji (Google) și Fluent Emoji (Microsoft), care nu cer mențiune, și Twemoji și OpenMoji, care cer. Această mențiune apare aici și, când folosești una dintre aceste imagini, în subsolul PDF-ului generat: Twemoji (CC BY 4.0, Copyright Twitter, Inc și colaboratori) și OpenMoji (CC BY-SA 4.0).",
    ]},
    "el": {"titulo": "Εικόνες τιμοκαταλόγου", "paragrafos": [
        "Οι εικόνες προς επιλογή για τα είδη του τιμοκαταλόγου προέρχονται από ελεύθερες βιβλιοθήκες εικονιδίων: το Noto Emoji (Google) και το Fluent Emoji (Microsoft), που δεν απαιτούν αναφορά, και το Twemoji και το OpenMoji, που απαιτούν. Αυτή η αναφορά εμφανίζεται εδώ και, όταν χρησιμοποιείτε μία από αυτές τις εικόνες, στο υποσέλιδο του PDF που δημιουργείται: Twemoji (CC BY 4.0, Copyright Twitter, Inc και συνεισφέροντες) και OpenMoji (CC BY-SA 4.0).",
    ]},
    "ru": {"titulo": "Изображения прайс-листа", "paragrafos": [
        "Изображения на выбор для позиций прайс-листа взяты из свободных библиотек значков: Noto Emoji (Google) и Fluent Emoji (Microsoft), не требующих указания авторства, а также Twemoji и OpenMoji, которые его требуют. Это указание появляется здесь и, если вы используете одно из этих изображений, в нижнем колонтитуле созданного PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc и авторы) и OpenMoji (CC BY-SA 4.0).",
    ]},
    "tr": {"titulo": "Fiyat listesi görselleri", "paragrafos": [
        "Fiyat listesi ürünleri için seçilebilecek görseller özgür simge kitaplıklarından gelir: atıf gerektirmeyen Noto Emoji (Google) ve Fluent Emoji (Microsoft) ile atıf gerektiren Twemoji ve OpenMoji. Bu atıf burada ve bu görsellerden birini kullandığınızda oluşturulan PDF'nin alt bilgisinde görünür: Twemoji (CC BY 4.0, Telif Hakkı Twitter, Inc ve katkıda bulunanlar) ve OpenMoji (CC BY-SA 4.0).",
    ]},
    "zh": {"titulo": "价目表图片", "paragrafos": [
        "价目表项目可选的图片来自免费图标库：Noto Emoji（谷歌）和 Fluent Emoji（微软）不要求署名，而 Twemoji 和 OpenMoji 要求署名。该署名会显示在这里，并且在您使用这些图片之一时，也会显示在生成的 PDF 页脚：Twemoji（CC BY 4.0，版权归 Twitter, Inc 及贡献者所有）和 OpenMoji（CC BY-SA 4.0）。",
    ]},
    "ja": {"titulo": "価格表の画像について", "paragrafos": [
        "価格表の品目で選べる画像は、無料のアイコンライブラリから提供されています：クレジット表記が不要な Noto Emoji（Google）と Fluent Emoji（Microsoft）、そしてクレジット表記が必要な Twemoji と OpenMoji です。そのクレジットはここに、また実際にその画像を使った場合は生成された PDF のフッターにも表示されます：Twemoji（CC BY 4.0、Copyright Twitter, Inc and contributors）と OpenMoji（CC BY-SA 4.0）。",
    ]},
    "ko": {"titulo": "가격표 이미지", "paragrafos": [
        "가격표 품목에서 고를 수 있는 이미지는 무료 아이콘 라이브러리에서 제공됩니다: 저작권 표시가 필요 없는 Noto Emoji(Google)와 Fluent Emoji(Microsoft), 그리고 저작권 표시가 필요한 Twemoji와 OpenMoji입니다. 이 저작권 표시는 여기에, 그리고 해당 이미지를 실제로 사용할 경우 생성된 PDF의 바닥글에도 표시됩니다: Twemoji(CC BY 4.0, Copyright Twitter, Inc and contributors)와 OpenMoji(CC BY-SA 4.0).",
    ]},
    "hi": {"titulo": "प्राइस-लिस्ट की तस्वीरें", "paragrafos": [
        "प्राइस-लिस्ट की वस्तुओं के लिए चुनी जा सकने वाली तस्वीरें मुफ़्त आइकन लाइब्रेरी से आती हैं: Noto Emoji (Google) और Fluent Emoji (Microsoft), जिन्हें श्रेय देना ज़रूरी नहीं है, और Twemoji और OpenMoji, जिन्हें ज़रूरी है। यह श्रेय यहाँ और, जब आप इनमें से कोई तस्वीर इस्तेमाल करते हैं, तो बने हुए PDF के फ़ुटर में भी दिखता है: Twemoji (CC BY 4.0, Copyright Twitter, Inc and contributors) और OpenMoji (CC BY-SA 4.0)।",
    ]},
    "ca": {"titulo": "Imatges del preçari", "paragrafos": [
        "Les imatges a triar per als articles del preçari vénen de biblioteques d'icones lliures: Noto Emoji (Google) i Fluent Emoji (Microsoft), que no exigeixen crèdit, i Twemoji i OpenMoji, que sí. Aquest crèdit apareix aquí i, quan useu una d'aquestes imatges, al peu del PDF generat: Twemoji (CC BY 4.0, Copyright Twitter, Inc i col·laboradors) i OpenMoji (CC BY-SA 4.0).",
    ]},
    "uk": {"titulo": "Зображення прайс-листа", "paragrafos": [
        "Зображення на вибір для позицій прайс-листа походять із вільних бібліотек значків: Noto Emoji (Google) і Fluent Emoji (Microsoft), які не вимагають зазначення авторства, та Twemoji і OpenMoji, які вимагають. Це зазначення з'являється тут і, коли ви використовуєте одне з цих зображень, у нижньому колонтитулі створеного PDF: Twemoji (CC BY 4.0, Copyright Twitter, Inc і автори) та OpenMoji (CC BY-SA 4.0).",
    ]},
    "id": {"titulo": "Gambar daftar harga", "paragrafos": [
        "Gambar yang bisa dipilih untuk item daftar harga berasal dari pustaka ikon bebas: Noto Emoji (Google) dan Fluent Emoji (Microsoft), yang tidak memerlukan kredit, serta Twemoji dan OpenMoji, yang memerlukannya. Kredit itu muncul di sini dan, saat Anda memakai salah satu gambar tersebut, di footer PDF yang dihasilkan: Twemoji (CC BY 4.0, Copyright Twitter, Inc dan kontributor) dan OpenMoji (CC BY-SA 4.0).",
    ]},
    "vi": {"titulo": "Hình ảnh bảng giá", "paragrafos": [
        "Những hình ảnh có thể chọn cho các mặt hàng trong bảng giá đến từ các thư viện biểu tượng miễn phí: Noto Emoji (Google) và Fluent Emoji (Microsoft) không yêu cầu ghi công, còn Twemoji và OpenMoji thì có. Phần ghi công này xuất hiện ở đây và, khi bạn dùng một trong các hình đó, ở chân trang của PDF được tạo ra: Twemoji (CC BY 4.0, Copyright Twitter, Inc và những người đóng góp) và OpenMoji (CC BY-SA 4.0).",
    ]},
}
from core import ptbr  # noqa: E402

TEXTOS["pt-br"] = ptbr.derivar_tudo(TEXTOS["pt"])       # o português do Brasil deriva-se do de Portugal (core/ptbr.py)


def aplicar(pagina: dict, lingua: str) -> dict:
    """A página de privacidade com a secção das imagens do preçário, no fim (`pagina` já copiada e preenchida)."""
    d = TEXTOS.get(lingua, TEXTOS["pt"])
    pagina["seccoes"].append({"titulo": d["titulo"], "paragrafos": list(d["paragrafos"])})
    return pagina
