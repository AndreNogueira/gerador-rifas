"""Textos acrescentados com a app Windows 2.4 e com as páginas traduzidas (tutoriais, Changelog, Termos): as 18 línguas lado a lado.

Mesmo formato de `web_extra.py` (um teste verifica que todas as chaves têm as 18 línguas e os mesmos {parâmetros}).
Para acrescentar uma chave: um bloco novo em CHAVES e subir as contagens em tests/test_i18n.py e tests/test_web_api.py.
"""
CHAVES: dict[str, dict[str, str]] = {
    "win_m_extras": {
        "pt": "Extras", "en": "Extras", "es": "Extras", "fr": "Extras", "de": "Extras", "it": "Extra", "nl": "Extra's",
        "pl": "Dodatki", "sv": "Extra", "cs": "Doplňky", "ro": "Extra", "el": "Επιπλέον", "ru": "Дополнительно",
        "tr": "Ekstralar", "zh": "附加功能", "ja": "追加機能", "ko": "추가 기능", "hi": "अतिरिक्त",
    },
    "win_opcoes": {
        "pt": "Séries, cor e logótipo…", "en": "Series, color and logo…", "es": "Series, color y logotipo…",
        "fr": "Séries, couleur et logo…", "de": "Serien, Farbe und Logo…", "it": "Serie, colore e logo…",
        "nl": "Series, kleur en logo…", "pl": "Serie, kolor i logo…", "sv": "Serier, färg och logotyp…",
        "cs": "Řady, barva a logo…", "ro": "Serii, culoare și logo…", "el": "Σειρές, χρώμα και λογότυπο…",
        "ru": "Серии, цвет и логотип…", "tr": "Seriler, renk ve logo…", "zh": "系列、颜色和徽标…", "ja": "シリーズ・色・ロゴ…",
        "ko": "시리즈, 색상, 로고…", "hi": "श्रृंखला, रंग और लोगो…",
    },
    "win_galeria": {
        "pt": "Galeria de templates…", "en": "Template gallery…", "es": "Galería de plantillas…", "fr": "Galerie de modèles…",
        "de": "Vorlagengalerie…", "it": "Galleria di modelli…", "nl": "Sjabloongalerij…", "pl": "Galeria szablonów…",
        "sv": "Mallgalleri…", "cs": "Galerie šablon…", "ro": "Galerie de șabloane…", "el": "Συλλογή προτύπων…",
        "ru": "Галерея шаблонов…", "tr": "Şablon galerisi…", "zh": "模板库…", "ja": "テンプレートギャラリー…",
        "ko": "템플릿 갤러리…", "hi": "टेम्पलेट गैलरी…",
    },
    "win_guardar": {
        "pt": "Guardar como", "en": "Save as", "es": "Guardar como", "fr": "Enregistrer sous", "de": "Speichern unter",
        "it": "Salva con nome", "nl": "Opslaan als", "pl": "Zapisz jako", "sv": "Spara som", "cs": "Uložit jako",
        "ro": "Salvează ca", "el": "Αποθήκευση ως", "ru": "Сохранить как", "tr": "Farklı kaydet", "zh": "另存为",
        "ja": "名前を付けて保存", "ko": "다른 이름으로 저장", "hi": "इस रूप में सहेजें",
    },
    "win_guardado": {
        "pt": "Guardado: {nome}", "en": "Saved: {nome}", "es": "Guardado: {nome}", "fr": "Enregistré : {nome}",
        "de": "Gespeichert: {nome}", "it": "Salvato: {nome}", "nl": "Opgeslagen: {nome}", "pl": "Zapisano: {nome}",
        "sv": "Sparat: {nome}", "cs": "Uloženo: {nome}", "ro": "Salvat: {nome}", "el": "Αποθηκεύτηκε: {nome}",
        "ru": "Сохранено: {nome}", "tr": "Kaydedildi: {nome}", "zh": "已保存：{nome}", "ja": "保存しました：{nome}",
        "ko": "저장됨: {nome}", "hi": "सहेजा गया: {nome}",
    },
    "win_visual_auto": {
        "pt": "Automático (Natal em dezembro)", "en": "Automatic (Christmas in December)", "es": "Automático (Navidad en diciembre)",
        "fr": "Automatique (Noël en décembre)", "de": "Automatisch (Weihnachten im Dezember)", "it": "Automatico (Natale a dicembre)",
        "nl": "Automatisch (Kerst in december)", "pl": "Automatycznie (Boże Narodzenie w grudniu)", "sv": "Automatiskt (jul i december)",
        "cs": "Automaticky (Vánoce v prosinci)", "ro": "Automat (Crăciun în decembrie)", "el": "Αυτόματα (Χριστούγεννα τον Δεκέμβριο)",
        "ru": "Автоматически (Рождество в декабре)", "tr": "Otomatik (Aralıkta Noel)", "zh": "自动（12月为圣诞主题）",
        "ja": "自動（12月はクリスマス）", "ko": "자동(12월에는 크리스마스)", "hi": "स्वचालित (दिसंबर में क्रिसमस)",
    },
    "web_changelog_sub": {
        "pt": "O que mudou, versão a versão.", "en": "What changed, version by version.", "es": "Qué ha cambiado, versión a versión.",
        "fr": "Ce qui a changé, version par version.", "de": "Was sich geändert hat, Version für Version.", "it": "Cosa è cambiato, versione per versione.",
        "nl": "Wat er veranderd is, versie per versie.", "pl": "Co się zmieniło, wersja po wersji.", "sv": "Vad som ändrats, version för version.",
        "cs": "Co se změnilo, verze po verzi.", "ro": "Ce s-a schimbat, versiune cu versiune.", "el": "Τι άλλαξε, έκδοση προς έκδοση.",
        "ru": "Что изменилось, версия за версией.", "tr": "Ne değişti, sürüm sürüm.", "zh": "每个版本的更新内容。", "ja": "バージョンごとの変更点。",
        "ko": "버전별 변경 내용.", "hi": "हर संस्करण में क्या बदला।",
    },
    "web_changelog_resumo": {
        "pt": "Resumo", "en": "This is a translated summary: the full history, with every detail, is in Portuguese.",
        "es": "Esto es un resumen traducido: el historial completo, con todos los detalles, está en portugués.",
        "fr": "Ceci est un résumé traduit : l'historique complet, avec tous les détails, est en portugais.",
        "de": "Dies ist eine übersetzte Zusammenfassung: der vollständige Verlauf mit allen Einzelheiten ist auf Portugiesisch.",
        "it": "Questo è un riassunto tradotto: la cronologia completa, con tutti i dettagli, è in portoghese.",
        "nl": "Dit is een vertaalde samenvatting: de volledige geschiedenis met alle details staat in het Portugees.",
        "pl": "To przetłumaczone streszczenie: pełna historia ze wszystkimi szczegółami jest po portugalsku.",
        "sv": "Detta är en översatt sammanfattning: den fullständiga historiken med alla detaljer finns på portugisiska.",
        "cs": "Toto je přeložené shrnutí: úplná historie se všemi podrobnostmi je v portugalštině.",
        "ro": "Acesta este un rezumat tradus: istoricul complet, cu toate detaliile, este în portugheză.",
        "el": "Αυτή είναι μια μεταφρασμένη περίληψη: το πλήρες ιστορικό, με όλες τις λεπτομέρειες, είναι στα πορτογαλικά.",
        "ru": "Это переведённая краткая сводка: полная история со всеми подробностями — на португальском.",
        "tr": "Bu, çevrilmiş bir özettir: tüm ayrıntılarıyla eksiksiz geçmiş Portekizce'dedir.",
        "zh": "这是翻译后的摘要：包含全部细节的完整更新记录为葡萄牙语。", "ja": "これは翻訳した要約です。詳細を含む完全な履歴はポルトガル語です。",
        "ko": "번역된 요약입니다. 모든 세부 내용이 담긴 전체 이력은 포르투갈어로 되어 있습니다.",
        "hi": "यह अनुवादित सार है: सभी विवरणों के साथ पूरा इतिहास पुर्तगाली में है।",
    },
    "web_versao": {
        "pt": "Versão {versao}", "en": "Version {versao}", "es": "Versión {versao}", "fr": "Version {versao}", "de": "Version {versao}",
        "it": "Versione {versao}", "nl": "Versie {versao}", "pl": "Wersja {versao}", "sv": "Version {versao}", "cs": "Verze {versao}",
        "ro": "Versiunea {versao}", "el": "Έκδοση {versao}", "ru": "Версия {versao}", "tr": "Sürüm {versao}", "zh": "版本 {versao}",
        "ja": "バージョン {versao}", "ko": "버전 {versao}", "hi": "संस्करण {versao}",
    },
    "win_fechar": {
        "pt": "Fechar", "en": "Close", "es": "Cerrar", "fr": "Fermer", "de": "Schließen", "it": "Chiudi", "nl": "Sluiten",
        "pl": "Zamknij", "sv": "Stäng", "cs": "Zavřít", "ro": "Închide", "el": "Κλείσιμο", "ru": "Закрыть", "tr": "Kapat",
        "zh": "关闭", "ja": "閉じる", "ko": "닫기", "hi": "बंद करें",
    },
}


def para(lingua: str) -> dict[str, str]:
    """As chaves desta lingua (as que faltarem aparecem como erro no teste, nunca em silencio)."""
    return {k: v[lingua] for k, v in CHAVES.items() if lingua in v}
