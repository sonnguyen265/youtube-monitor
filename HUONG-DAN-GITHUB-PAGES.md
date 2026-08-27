# Đưa trang lên GitHub Pages

Mục tiêu: biến [`index.html`](index.html) thành một địa chỉ web ai cũng mở được, ví dụ
`https://tenban.github.io/yt-seo-monitor/`. Miễn phí, không cần server, không cần thẻ tín dụng.

Làm lần đầu mất khoảng 10 phút. Những lần sau, cập nhật chỉ mất 1 phút.

---

## ⚠️ Đọc phần này trước, đừng bỏ qua

Thư mục dự án đang có file **`api_key.txt` chứa API key thật của bạn**. Đưa file đó lên
GitHub là công khai key cho cả thế giới.

Tệ hơn: Git lưu lại toàn bộ lịch sử. Lỡ đẩy lên rồi thì **xoá file đi cũng không sạch**, key
vẫn nằm trong lịch sử commit và ai cũng đào lại được. Google có quét GitHub công khai để tìm
key bị lộ và thường tự vô hiệu hoá.

Nên nhớ đúng hai điều:

| Đưa lên | Không được đưa lên |
|---|---|
| `index.html` | `api_key.txt` |
| `README.md` | `data/` (snapshot cũ của bạn) |
| `yt_monitor.py`, `run.bat` (nếu muốn) | `__pycache__/` |

Bản thân `index.html` **không chứa key** — mỗi người mở trang tự nhập key của họ, lưu trong
trình duyệt của chính họ. Đó là lý do đưa nó lên web công khai được mà quota của bạn không
ai đụng tới.

> Nếu lỡ đẩy `api_key.txt` lên: vào Google Cloud Console → **APIs & Services → Credentials**
> → xoá key cũ đi và tạo key mới. Đừng chỉ xoá file trên GitHub.

---

## Cách 1 — Dùng giao diện web (khuyên dùng, không cần cài gì)

Không cần cài Git, làm hết trên trình duyệt.

### Bước 1. Tạo tài khoản GitHub

Vào [github.com](https://github.com) → **Sign up**. Nếu đã có tài khoản thì đăng nhập.

Tên tài khoản sẽ nằm trong địa chỉ trang web sau này, nên chọn tên gọn gàng.

### Bước 2. Tạo repository

1. Bấm dấu **+** góc trên bên phải → **New repository**
2. **Repository name**: `yt-seo-monitor` (hoặc tên khác, không dấu, không khoảng trắng)
3. Chọn **Public** — bắt buộc, vì gói miễn phí chỉ cho Pages trên repo công khai
4. Tick **Add a README file**
5. Bấm **Create repository**

### Bước 3. Upload

1. Trong repo vừa tạo, bấm **Add file** → **Upload files**
2. Kéo thả `index.html` vào
3. Ô **Commit changes** ở dưới, gõ mô tả ngắn: `them trang theo doi kenh`
4. Bấm **Commit changes**

**Chỉ upload đúng file này.** Đừng kéo cả thư mục dự án vào — `api_key.txt` sẽ đi theo.

### Bước 4. Bật GitHub Pages

1. Trong repo, vào tab **Settings** (bánh răng, hàng trên cùng)
2. Cột trái, mục **Code and automation**, bấm **Pages**
3. Phần **Build and deployment** → **Source**: chọn **Deploy from a branch**
4. **Branch**: chọn `main`, thư mục để `/ (root)`
5. Bấm **Save**

### Bước 5. Đợi rồi mở thử

Lần đầu mất khoảng 1–2 phút. Tải lại trang Settings → Pages, khi nào hiện dòng
**"Your site is live at ..."** kèm địa chỉ là xong.

Địa chỉ có dạng:

```
https://<tên-tài-khoản>.github.io/<tên-repo>/
```

Mở thử bằng **cửa sổ ẩn danh** (Ctrl+Shift+N). Phải thấy màn hình *"Nhập API key để bắt
đầu"* — đúng như người lạ nhìn thấy. Nếu mở bằng cửa sổ thường, trình duyệt còn nhớ key cũ
của bạn nên sẽ vào thẳng bảng, không kiểm tra được.

---

## Cách 2 — Dùng Git dòng lệnh

Chọn cách này nếu bạn muốn đẩy cả `yt_monitor.py` lên và cập nhật thường xuyên.

### Bước 1. Chặn file nhạy cảm trước khi làm bất cứ điều gì khác

Mở terminal tại `d:\SourceUser\yt-seo-monitor` và tạo file `.gitignore`:

```bash
printf 'api_key.txt\ndata/\n__pycache__/\n' > .gitignore
```

Kiểm tra lại — lệnh dưới đây **không được** hiện `api_key.txt`:

```bash
git init
git add -A
git status --short
```

Nếu vẫn thấy `api_key.txt` trong danh sách thì dừng lại, `.gitignore` chưa ăn.

### Bước 2. Commit và đẩy lên

Tạo repo rỗng trên GitHub trước (Bước 2 của Cách 1, **bỏ tick** "Add a README file"), rồi:

```bash
git add -A
git commit -m "trang theo doi SEO kenh YouTube"
git branch -M main
git remote add origin https://github.com/<tên-tài-khoản>/<tên-repo>.git
git push -u origin main
```

GitHub sẽ hỏi đăng nhập. Mật khẩu tài khoản **không dùng được** — cần Personal Access Token:
vào [github.com/settings/tokens](https://github.com/settings/tokens) → **Generate new token
(classic)** → tick quyền `repo` → copy chuỗi hiện ra và dán vào chỗ hỏi mật khẩu.

### Bước 3. Bật Pages

Giống Bước 4 của Cách 1.

---

## Cập nhật trang sau này

**Qua web:** vào repo → bấm vào `index.html` → biểu tượng bút chì → sửa → **Commit changes**.

**Qua Git:**

```bash
git add -A
git commit -m "sua giao dien"
git push
```

Cả hai cách đều tự triển khai lại sau khoảng 30–60 giây. Không phải bật lại Pages.

---

## Sự cố thường gặp

| Hiện tượng | Nguyên nhân và cách xử lý |
|---|---|
| Vào địa chỉ ra lỗi **404** | Pages chưa build xong — đợi thêm 1 phút. Hoặc file trong repo không tên đúng `index.html`. |
| Trang trắng trơn, không hiện gì | Bấm **F12** → tab **Console** xem lỗi. Thường do tên file sai chữ hoa/thường: GitHub phân biệt `Index.html` với `index.html`, Windows thì không. |
| Sửa xong mà trang vẫn cũ | Trình duyệt lưu cache. Nhấn **Ctrl+F5**. |
| Mục **Pages** không có trong Settings | Repo đang để Private. Gói miễn phí chỉ hỗ trợ repo Public. Đổi trong **Settings → General → Danger Zone → Change visibility**. |
| Vào trang thấy luôn bảng, không hỏi key | Trình duyệt bạn còn nhớ key cũ. Mở bằng cửa sổ ẩn danh để xem đúng cảnh người lạ thấy. |
| Người dùng báo lỗi hết quota | Quota tính theo key của từng người, không dùng chung. Bảo họ đợi sang ngày hôm sau (reset lúc 0h giờ Thái Bình Dương, khoảng 14–15h giờ VN). |

---

## Vài điều nên biết thêm

**Repo phải Public.** Gói GitHub Free chỉ cho Pages trên repo công khai. Muốn để repo riêng
tư mà vẫn có Pages thì cần GitHub Pro (trả phí). Lưu ý thêm: kể cả repo Private, trang web
xuất bản ra **vẫn công khai** — đó là hai thiết lập tách rời nhau.

**Trang chạy qua `https://` nên khác bản mở bằng file.** Điểm khác duy nhất đáng kể: giờ
trình duyệt có gửi header `Referer`, nên nếu muốn bạn có thể vào Google Cloud Console giới
hạn **key của riêng bạn** theo HTTP referrer trỏ về đúng địa chỉ Pages này. Không bắt buộc,
vì người khác dùng key của họ chứ không đụng tới key của bạn.

**Mỗi người một kho dữ liệu riêng.** Key, danh sách kênh và lịch sử đều nằm trong
`localStorage` của từng trình duyệt. Hai người vào cùng một địa chỉ vẫn thấy hai bảng khác
nhau, không ai nhìn thấy dữ liệu của ai.

**Muốn tên miền riêng** (kiểu `theodoi.com`): mua tên miền, rồi vào **Settings → Pages →
Custom domain**. GitHub có hướng dẫn cấu hình DNS chi tiết ở đó.
