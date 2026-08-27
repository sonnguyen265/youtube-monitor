# Theo dõi 10 kênh YouTube — góc nhìn SEO

Công cụ chạy trên máy bạn, không cần cài thư viện, không cần đăng nhập từng kênh.
Mỗi lần chạy sẽ in ra bảng so sánh 10 kênh và tự đối chiếu với lần chạy trước.

---

## 1. Lấy API key (làm 1 lần, ~3 phút, miễn phí)

1. Vào https://console.cloud.google.com/
2. Tạo project mới (nút chọn project ở góc trên trái → **New Project**), đặt tên tuỳ ý
3. Vào **APIs & Services → Library**, tìm **YouTube Data API v3** → bấm **Enable**
4. Vào **APIs & Services → Credentials** → **Create Credentials** → **API key**
5. Copy key vừa hiện ra, dán vào file `api_key.txt` (thay dòng `AIzaSy...` mẫu)

> Key này chỉ đọc dữ liệu công khai — không đụng được vào kênh của bạn, để lộ cũng
> không mất kênh. Nếu muốn chắc chắn, bấm **Restrict key** và giới hạn ở YouTube Data API v3.

## 2. Khai báo 10 kênh

Mở `channels.txt`, xoá các dòng ví dụ, dán mỗi dòng một kênh. Ba dạng đều được:

```
https://www.youtube.com/@tenkenh
@tenkenh
UCxxxxxxxxxxxxxxxxxxxxxx
```

Dạng `UC...` (channel ID) là chính xác nhất. Lấy ở YouTube Studio → **Settings → Channel → Advanced settings**.

## 3. Chạy

Double-click **`run.bat`**, hoặc mở terminal tại thư mục này và gõ:

```
python yt_monitor.py
```

## 4. Hoặc xem bằng trang web

**Double-click [`index.html`](index.html)** là xong. Đây là một file HTML duy nhất,
làm đúng việc như bản Python nhưng có giao diện: thẻ tổng quan, bảng sắp xếp được, cảnh
báo. Không cần Python, không cần terminal, không cần cài gì thêm.

**Lần đầu mở, trang hỏi API key.** Không có key thì chưa làm được gì. Trong màn hình đó có
sẵn hướng dẫn 5 bước lấy key, bấm vào dòng "Chưa có key?" để mở. Key được kiểm tra ngay
khi bấm Lưu — sai key là biết liền, không phải chờ tới lúc thêm kênh.

Key **không nằm trong file**, mà lưu trong `localStorage` của trình duyệt người dùng. Nghĩa
là bạn đưa file này cho ai, hay đăng lên web công khai, thì mỗi người tự dùng key của họ và
quota của bạn không ai đụng tới. Đổi key sau này bằng nút **Đổi API key** ở cuối khung danh
sách kênh.

Trong file có `var DAILY_UNIT_BUDGET = 500;` — trần units trang tự đặt cho mỗi ngày,
thấp hơn hẳn hạn mức 10.000 của Google. Trang đếm từng lượt gọi API và chặn trước khi
gọi nếu vượt trần, nên lỡ bấm nhiều lần cũng không đốt hết quota cả ngày. Số đã dùng hiện
ở dòng chữ nhỏ dưới tiêu đề. Bộ đếm về 0 lúc 0h giờ Thái Bình Dương, đúng lúc Google
reset quota (khoảng 14–15h giờ VN).

> Đây là phanh chống bấm nhầm, không phải khoá bảo mật: ai có file vẫn sửa được con số
> này. Nhưng vì mỗi người dùng key của chính mình, họ chỉ tự đốt quota của họ.

Bấm **Thêm kênh** trên thanh trên cùng để mở khung danh sách kênh. Dán link kênh vào ô rồi
bấm **Thêm** (hoặc gõ Enter). Trang gọi API kiểm tra ngay, hiện tên và ảnh đại diện kênh —
sai link là biết liền, không phải chờ tới lúc chạy. Mỗi kênh có nút **Xoá** riêng.

Khung này mặc định ẩn để trang mở ra là thấy bảng số liệu luôn. Riêng lần đầu, khi chưa có
kênh nào, nó tự mở sẵn.

**Mở trang là tự lấy dữ liệu**, không phải bấm gì, trừ khi hôm nay đã cập nhật rồi. Muốn
lấy lại giữa chừng thì bấm **Cập nhật dữ liệu**.

Danh sách kênh và lịch sử được nhớ trong trình duyệt. Mở bằng Chrome, Edge, Firefox hay
Cốc Cốc đều được — chỉ cần trình duyệt và mạng.

### Dung lượng lưu trong trình duyệt

Trang giữ tối đa 180 ngày lịch sử rồi tự bỏ ngày cũ nhất, nên dung lượng có trần chứ không
phình mãi. Thực đo: mỗi kênh tốn khoảng 0,5 KB một ngày.

| Số kênh | Mỗi ngày | Đầy 180 ngày | So với hạn mức 5 MB |
|---|---|---|---|
| 5 kênh | 2,6 KB | 0,5 MB | 9% |
| 10 kênh | 5,2 KB | 0,9 MB | 18% |
| 20 kênh | 10,4 KB | 1,8 MB | 37% |
| 50 kênh | 26 KB | 4,6 MB | 92% |

Dưới 20 kênh thì không bao giờ phải lo. Từ 50 kênh trở lên mới nên hạ `MAX_SNAPSHOTS`
trong file xuống, ví dụ 90 ngày.

Cuối khung **Danh sách kênh** có dòng báo đang chiếm bao nhiêu, kèm hai nút dọn:

- **Xoá lịch sử** — bỏ số liệu các ngày, giữ lại danh sách kênh và API key.
- **Xoá sạch mọi thứ** — xoá cả key lẫn kênh lẫn lịch sử, về như lần đầu mở.

**Trên điện thoại**, bảng 11 cột không thể nhét vừa màn hình nên mỗi kênh tự đổi thành
một thẻ dọc — xem đủ mọi cột mà không phải vuốt ngang. Vì thẻ không còn tiêu đề cột để
bấm, có thêm ô **Sắp theo** ngay trên bảng làm thay việc sắp xếp. Muốn dùng trên điện
thoại thì chép file `index.html` vào máy rồi mở bằng trình duyệt, hoặc để file trong
thư mục đồng bộ (Google Drive, OneDrive) và mở từ đó.

Trang không xuất/nhập CSV. Cần file CSV thì chạy bản Python, nó vẫn ghi vào
`data/snapshot_*.csv` như cũ.

## 5. Chia sẻ cho người khác dùng

Vì key không nằm trong file, bạn đưa trang lên web công khai được mà quota của mình không ai
đụng tới — mỗi người tự nhập key của họ.

Xem [HUONG-DAN-GITHUB-PAGES.md](HUONG-DAN-GITHUB-PAGES.md) để có địa chỉ dạng
`https://tenban.github.io/yt-seo-monitor/`, miễn phí.

> File `.gitignore` trong thư mục này đã chặn sẵn `api_key.txt` và `data/`. Đừng xoá nó —
> đó là thứ giữ cho key thật của bạn không bị đẩy lên GitHub.

---

## Đọc kết quả

### Bảng chính

| Cột | Ý nghĩa |
|---|---|
| **SUBS** | Số sub hiện tại (YouTube làm tròn ở mức nghìn) |
| **SUB +/-** | Tăng/giảm so với lần chạy trước |
| **MEDIAN 10** | View trung vị của 10 video dài gần nhất |
| **XU HƯỚNG** | Median 10 video mới so với 10 video liền trước |
| **VIEW/NGÀY** | Tốc độ kéo view trung bình của video mới |
| **IM LẶNG** | Số ngày kể từ video gần nhất |

**Cột quan trọng nhất với SEO là XU HƯỚNG và VIEW/NGÀY.**

- **XU HƯỚNG** trả lời: kênh này đang khá lên hay đang xuống? Dùng median chứ không dùng
  trung bình, nên một video viral bất thường không làm sai lệch bức tranh.
- **VIEW/NGÀY** trả lời: video mới có được YouTube đẩy đi không? Video sống nhờ search/suggest
  sẽ giữ được view/ngày ổn định lâu dài; video chỉ sống nhờ cú đẩy lúc mới đăng sẽ tụt rất nhanh.

Bảng được sắp theo VIEW/NGÀY giảm dần — kênh đáng đầu tư nhất nằm trên cùng.

### Mục "CẦN CHÚ Ý"

Tự cảnh báo khi kênh tụt trên 30%, ngừng đăng quá 21 ngày, hoặc quá nửa số video mới
bị lỗi metadata (thiếu tag, mô tả dưới 200 ký tự, title dài quá 70 ký tự nên bị cắt
trên kết quả tìm kiếm).

### File CSV

Mỗi lần chạy lưu một snapshot vào `data/snapshot_YYYY-MM-DD.csv`, mở bằng Excel được
(đã encode UTF-8 nên tiếng Việt không lỗi font). File này có thêm các cột không hiện
trên terminal: tổng view, tổng video, nhịp đăng bài, số Shorts, video top và view của nó.

Càng chạy đều thì dữ liệu càng có giá trị — nên chạy cố định mỗi tuần một lần.

---

## Lưu ý

- **Shorts được tách riêng.** Các chỉ số median/xu hướng chỉ tính video dài, vì trộn
  Shorts vào sẽ làm sai lệch hoàn toàn. Số Shorts nằm ở cột `so_shorts_trong_20` trong CSV.
- **Kênh mới hoặc kênh chủ yếu đăng Shorts** có thể hiện `n/a` ở cột xu hướng do chưa đủ
  20 video dài để so sánh.
- **Quota:** mỗi lần chạy 10 kênh tốn khoảng 30–40 units, hạn mức 10.000 units/ngày.
  Chạy thoải mái.

## Cái này chưa làm được

Dữ liệu công khai không có: **CTR thumbnail, thời lượng xem trung bình (AVD), tỷ lệ
traffic đến từ YouTube Search, và từ khoá người xem gõ để tìm ra video**. Muốn có bốn
thứ đó — đặc biệt là danh sách từ khoá, thứ giá trị nhất với người làm SEO — cần
YouTube Analytics API + OAuth, phải authorize một lần cho mỗi kênh.
