"""Điều khoản, quyền riêng tư và liên hệ bằng tiếng Việt: bản dịch của `pt.py` (cùng các trang, mục, đoạn và {ký hiệu}). Chưa được người bản ngữ kiểm tra; bản tiếng Bồ Đào Nha được ưu tiên."""
FRASES = {
    "responsavel_com": "Dịch vụ do {nome} vận hành.",
    "responsavel_sem": "Dịch vụ do chính tác giả vận hành, người đưa nó lên mạng.",
    "contacto_com": "Bạn có thể liên hệ với chúng tôi tại {email}.",
    "contacto_sem": "Hiện chưa có thông tin liên hệ công khai.",
    "contacto_pagina_com": "Nếu có câu hỏi, lỗi hoặc góp ý, hãy viết đến {email}.",
    "contacto_pagina_sem": "Hiện chưa có thông tin liên hệ công khai. Vui lòng quay lại trang này sau.",
    "atualizado": "8 tháng 11 năm 2026",
}

AVISO = ("Phiên bản tạm thời, cần được xem xét lại với sự hỗ trợ pháp lý. Nếu có điều gì ở đây khác với những gì dịch vụ làm, xin hãy báo để chúng tôi sửa. "
         "Đây là bản dịch chưa được người bản ngữ kiểm tra: nếu các phiên bản khác nhau, bản tiếng Bồ Đào Nha được ưu tiên.")

TEXTOS = {
    "termos": {
        "titulo": "Điều khoản sử dụng",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Dịch vụ này là gì",
             "paragrafos": ["Trình tạo vé số tạo, từ một mẫu PDF, các vé bốc thăm có đánh số sẵn sàng để in. Chỉ có vậy: dịch vụ không bán vé, "
                            "không nhận tiền, không lưu danh sách người tham gia và không tổ chức bốc thăm có giá trị pháp lý.",
                            "{responsavel}"]},
            {"titulo": "Người tổ chức bốc thăm chịu trách nhiệm về việc đó",
             "paragrafos": ["Các cuộc bốc thăm, xổ số từ thiện và rút thăm chịu sự điều chỉnh của quy định pháp luật (ví dụ giấy phép của chính quyền địa phương và quy định dành cho hội nhóm) và khác nhau "
                            "tùy trường hợp. Người tổ chức bốc thăm hoàn toàn chịu trách nhiệm tuân thủ pháp luật, thu tiền và trao giải thưởng. "
                            "Dịch vụ này không đưa ra tư vấn pháp lý."]},
            {"titulo": "Việc sử dụng được phép",
             "paragrafos": ["Dịch vụ miễn phí và dành cho việc sử dụng hợp lý. Không được dùng để làm vé cho hành vi gian lận hoặc để làm quá tải máy chủ: có giới hạn về kích thước tệp, "
                            "về số lượng số mỗi yêu cầu ({max_numeros}) và về số yêu cầu mỗi phút, và chỉ tạo một lượt tại một thời điểm."]},
            {"titulo": "Tệp của bạn",
             "paragrafos": ["Mẫu và các chữ số chỉ được dùng để tạo vé của bạn và bị xóa khỏi máy chủ sau {validade} phút không hoạt động, "
                            "hoặc khi bạn bấm “Xóa tất cả”. Chúng tôi không dùng chúng vào việc gì khác. Chúng vẫn là của bạn: bạn chỉ cần có quyền sử dụng những gì bạn tải lên "
                            "(hình ảnh, phông chữ, logo)."]},
            {"titulo": "Không bảo đảm",
             "paragrafos": ["Dịch vụ được cung cấp “nguyên trạng”, không bảo đảm luôn sẵn sàng hay không có lỗi. Hãy luôn kiểm tra các tệp PDF trước khi in (dịch vụ "
                            "có kiểm tra các số đã tạo, nhưng bước kiểm tra cuối cùng là của bạn). Trong phạm vi pháp luật cho phép, chúng tôi không chịu trách nhiệm về những thiệt hại liên quan đến việc sử dụng dịch vụ."]},
            {"titulo": "Thay đổi",
             "paragrafos": ["Các điều khoản này có thể thay đổi; ngày cập nhật gần nhất là {atualizado}. Nếu một ngày nào đó dịch vụ trở thành có phí, điều này sẽ được nêu rõ trước khi thu phí."]},
            {"titulo": "Liên hệ", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Chính sách quyền riêng tư",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Tóm tắt",
             "paragrafos": ["Không có tài khoản, không có quảng cáo và không có công cụ theo dõi của bên thứ ba. Tệp của bạn bị xóa khỏi máy chủ trong vòng {validade} phút. "
                            "Số liệu thống kê sử dụng chỉ là các con số tổng hợp."]},
            {"titulo": "Chúng tôi xử lý những dữ liệu nào",
             "paragrafos": ["Các tệp bạn tải lên (mẫu và chữ số) chỉ được xử lý để tạo vé, nằm trong một thư mục tạm trên máy chủ và bị xóa "
                            "sau {validade} phút không hoạt động hoặc khi bạn bấm “Xóa tất cả”.",
                            "Để biết dịch vụ được sử dụng như thế nào, chúng tôi ghi lại các số đếm: bao nhiêu lượt truy cập, lượt tạo và lượt tải về, ngôn ngữ và giao diện được chọn, và loại màn hình. "
                            "Chúng tôi cũng ghi lại quốc gia của lượt truy cập (chỉ mã, ví dụ «PT»), do mạng của nhà cung cấp lưu trữ suy ra từ địa chỉ IP; chúng tôi không lưu chính địa chỉ IP. Chúng tôi không bao giờ ghi lại địa chỉ IP, tên tệp, nội dung tệp hay nhận dạng đầy đủ của trình duyệt.",
                            "Địa chỉ IP chỉ được dùng trong bộ nhớ, trong chốc lát, để giới hạn số yêu cầu mỗi phút, và chúng tôi không lưu nó. Nhà cung cấp dịch vụ lưu trữ "
                            "(Render, tại Frankfurt, Liên minh châu Âu) có thể ghi lại địa chỉ IP trong nhật ký kỹ thuật của họ."]},
            {"titulo": "Trong trình duyệt của bạn",
             "paragrafos": ["Chúng tôi lưu tùy chọn của bạn trong trình duyệt (bộ nhớ cục bộ): ngôn ngữ, giao diện, chế độ sáng hoặc tối và các giá trị biểu mẫu gần nhất. Để bạn không phải "
                            "làm lại từ năm này sang năm khác, tệp chữ số cũng có thể được giữ trong trình duyệt của bạn (không bao giờ trên máy chủ của chúng tôi); “Xóa tất cả” sẽ xóa nó. "
                            "Chúng tôi không dùng cookie quảng cáo hay theo dõi."]},
            {"titulo": "Cơ sở pháp lý và thời hạn lưu giữ",
             "paragrafos": ["Chúng tôi xử lý dữ liệu này dựa trên lợi ích hợp pháp của chúng tôi trong việc cung cấp dịch vụ và giữ cho dịch vụ an toàn (GDPR, Điều 6(1)(f)). "
                            "Các tệp chỉ tồn tại vài phút; các số đếm tổng hợp không nhận dạng ai."]},
            {"titulo": "Quyền của bạn",
             "paragrafos": ["Bạn có quyền truy cập, chỉnh sửa, xóa và phản đối, cũng như khiếu nại với cơ quan bảo vệ dữ liệu của bạn (ở Bồ Đào Nha là "
                            "CNPD, cnpd.pt). Vì chúng tôi không giữ dữ liệu nhận dạng bạn, trên thực tế có rất ít thứ để truy cập hay xóa; nếu còn băn khoăn, hãy trao đổi với chúng tôi."]},
            {"titulo": "Ai chịu trách nhiệm", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Cập nhật", "paragrafos": ["Cập nhật lần cuối: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Liên hệ",
        "aviso": "",
        "seccoes": [
            {"titulo": "Hãy liên hệ với chúng tôi",
             "paragrafos": ["{contacto_pagina}",
                            "Nếu bạn gặp lỗi, hãy cho chúng tôi biết bạn đã làm gì và mong đợi điều gì; đừng gửi mẫu của bạn nếu nó chứa dữ liệu cá nhân."]},
        ],
    },
}

ANUNCIOS = {
    "resumo": "Không có tài khoản. Trang web hiển thị quảng cáo của Google (AdSense), có thể dùng cookie; ngoài ra, chúng tôi không dùng công cụ theo dõi của bên thứ ba.",
    "cookies": "Cookie quảng cáo duy nhất là cookie của các quảng cáo (xem “Quảng cáo”).",
    "seccao": {
        "titulo": "Quảng cáo",
        "paragrafos": [
            "Trang web này hiển thị quảng cáo của Google (AdSense) để tự trang trải chi phí. Google và các đối tác có thể dùng cookie và mã nhận dạng để hiển thị quảng cáo, được cá nhân hóa hoặc không, và đo lường kết quả; chúng tôi không nhận dữ liệu đó và không liên kết nó với bất kỳ tệp nào của bạn.",
            "Quảng cáo chỉ xuất hiện sau khi bạn lựa chọn trong thông báo đồng ý mà Google hiển thị khi bạn mở trang web (bắt buộc ở Khu vực Kinh tế châu Âu và Vương quốc Anh); cơ sở pháp lý của cookie quảng cáo là sự đồng ý của bạn (GDPR, Điều 6(1)(a)), và bạn có thể xem lại lựa chọn trong tùy chọn quyền riêng tư của thông báo đó. Quảng cáo không bao giờ xuất hiện trong các tệp đã tạo, trong bảng điều khiển hay trong ứng dụng Windows.",
            "Tìm hiểu cách Google sử dụng dữ liệu tại policies.google.com/technologies/partner-sites và quản lý quảng cáo cá nhân hóa tại adssettings.google.com.",
        ],
    },
}

PARTILHAS = {"titulo": "Thiết kế được chia sẻ", "paragrafos": [
    "Nếu bạn bấm “Chia sẻ bằng liên kết” trong Trình chỉnh sửa mẫu, thiết kế (hình dạng, văn bản và màu sắc, không kèm hình ảnh) được lưu trên máy chủ của chúng tôi, tại một địa chỉ khó đoán, trong 90 ngày kể từ lần truy cập cuối, và bất kỳ ai có liên kết đều có thể mở nó. Chúng tôi không lưu địa chỉ IP của bạn hay dữ liệu khác về người chia sẻ: đừng viết dữ liệu cá nhân hay bí mật vào thiết kế. Thiết kế bạn không chia sẻ chỉ được gửi lên máy chủ để tạo mẫu và bị xóa cùng phiên."]}

OPINIAO = {"titulo": "Bình luận và sự cố được báo cáo", "paragrafos": [
    "Nếu bạn để lại bình luận ở trang «Bình luận», chúng tôi lưu nội dung, ngày và tên bạn chọn hiển thị (không có tên nếu bạn muốn ẩn danh; nếu bạn chọn hiển thị tên nhưng để trống, sẽ hiện «Khách số …»). Bình luận hiển thị cho mọi người, không kèm địa chỉ IP của bạn. Chúng tôi cũng lưu địa chỉ IP của bạn, chỉ người phụ trách trang xem được, duy nhất để chặn lạm dụng: nó bị xóa khỏi bình luận sau 90 ngày. Đừng viết dữ liệu cá nhân vào bình luận; muốn xóa bình luận, hãy viết thư cho chúng tôi (xem Liên hệ).",
    "Nếu bạn báo cáo sự cố, nội dung bạn viết (và, nếu bạn chọn tùy chọn đó, phiên bản ứng dụng, ngôn ngữ, trình duyệt và màn hình) được gửi đến GitHub của dự án, nơi nó được ghi lại và hiển thị cho nhóm. Địa chỉ IP của bạn không được gửi. Đừng viết dữ liệu cá nhân hay mật khẩu.",
]}
