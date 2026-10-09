# AGORA Blue Sky: Temporal Argument Graph and Viewpoint Agents

## Tầm nhìn

Blue Sky mở rộng lõi nghiên cứu AGORA theo chuỗi:

`Arguments -> Temporal Argument Graph -> Viewpoint Clusters -> Viewpoint Agents -> Agentic Public Deliberation`

Mục tiêu của bản proof-of-concept là cho thấy lập luận có provenance có thể tạo thành đồ thị biến đổi theo thông tin sẵn có, rồi được tổng hợp thành các agent quan điểm tập thể. Đây không phải chatbot tranh luận, LLM role-play hay hệ thống tối ưu thuyết phục.

## Quan hệ với lõi AGORA

Lõi AGORA vẫn là lập luận: trích xuất, nguồn, thời gian, trạng thái và quan hệ support/attack. Lớp agent không thay thế dữ liệu này. Mọi node agent và cạnh agent trong demo đều truy ngược được về argument ID, relation ID và source ID.

## Sáu trạng thái CTQ

`t1 ... t6` là các trạng thái thông tin theo thời gian, **không phải các vòng tương tác agent nhân tạo**.

| Mốc | Khoảng ngày | Trọng tâm |
| --- | --- | --- |
| `t1` | 2026-07-01 đến 2026-07-02 | Bất thường điểm và các giải thích cạnh tranh; chưa kết luận sai phạm. |
| `t2` | 2026-07-05 đến 2026-07-07 | Chuyển từ nghi vấn thống kê sang chứng cứ sai phạm coi thi. |
| `t3` | 2026-07-09 | Đề xuất thi lại Toán và các biện pháp cạnh tranh. |
| `t4` | 2026-08-04 đến 2026-08-05 | Hủy kết quả ban đầu và quyết định thi lại tất cả môn. |
| `t5` | 2026-08-19 | Kết quả thi lại và các diễn giải có giới hạn. |
| `t6` | 2026-10-01 | Điều tra mở rộng tới tất cả phòng và tất cả môn. |

Mỗi snapshot tuân theo `G_t = (A_t, E_t, state_t)`. Argument chỉ xuất hiện sau `introduced_at`; sau `active_until`, nó có thể được giữ như node lịch sử nếu cần làm đích của quan hệ thời gian. Node lịch sử hiển thị `status = null`, không dùng status cuối để giả lập status hiện tại. Relation chỉ xuất hiện khi đã được giới thiệu, còn hiệu lực và cả hai đầu đã tồn tại. Status được đọc nguyên trạng từ CSV; loader báo lỗi nếu một argument đang active lại thiếu status.

## Đồ thị lập luận thời gian

Chế độ **Argument Graph** hiển thị:

- node argument với P/R/C, loại `A_K`/`A_D`, nguồn, vai trò thời gian và status;
- màu riêng cho `accepted`, `rejected`, `undecided`;
- viền nổi bật cho argument mới tại mốc đang xem;
- cạnh có hướng `source_arg -> target_arg`, phân biệt support và attack;
- detail panel chứa conflict type, confidence và evidence sources.

Rule null được giữ null và hiển thị rõ; demo không tạo lại các quy tắc ngầm định đã bị loại khỏi canonical data.

## Phân cụm quan điểm và viewpoint agents

Mapping thủ công nằm tại `bluesky/data/viewpoint_mapping.json`. Bảy cụm phủ đúng 27 lập luận, không trùng nhau. Phân nhóm dựa trên kết luận và vai trò thời gian, không thay đổi nội dung hay trạng thái của argument.

Trong **Viewpoint Agent View**, một node là một cụm quan điểm có ít nhất một argument active tại mốc hiện tại. Node hiển thị số argument active và phân bố status. Thành phần nguồn được tính trực tiếp từ source IDs. Không có công thức strength ẩn hoặc hằng số tùy ý; quy mô được mô tả bằng số argument active.

Quan hệ liên cụm được tổng hợp khi relation nền nối hai argument thuộc hai cụm khác nhau. Click cạnh agent sẽ hiện đầy đủ relation ID và cặp argument nền.

Không có institutional agent giả. Nội dung thể chế chỉ xuất hiện qua argument thật có `official_document` hoặc `authority_statement`, được nhận diện bằng viền node và metadata nguồn.

## Điều khiển visualization

- slider sáu vị trí, nút Trước/Sau và Phát/Dừng;
- chuyển giữa Argument Graph và Viewpoint Agent;
- lọc tất cả, `A_K`, `A_D`;
- bật/tắt support, attack, rejected, undecided hoặc chỉ node mới;
- kéo node, kéo nền để pan, cuộn chuột để zoom;
- hover để xem tóm tắt, click để mở provenance chi tiết.

Visualization dùng SVG/JavaScript nhúng, không cần CDN hoặc frontend framework.

## Dữ liệu thật và phần mô hình hóa thủ công

Dữ liệu thật được đọc trực tiếp từ các tệp canonical trong `data/`:

- `data/timelines/ctq_timeline.csv`
- `data/annotations/ctq_selected_arguments.csv`
- `data/annotations/ctq_argument_status.csv`
- `data/annotations/ctq_relations.csv`
- `data/annotations/ctq_arguments.csv`
- `data/sources/ctq_sources.csv`

Phần mô hình hóa thủ công duy nhất là việc gán 27 argument vào bảy viewpoint. Demo không sửa claim, không tạo status, relation, timestamp hay source mới.

## Chạy demo

Từ thư mục gốc repository:

```bash
python -m bluesky.demo
```

Kết quả:

`bluesky/outputs/temporal_agentic_demo.html`

Để yêu cầu Python mở trình duyệt sau khi sinh file:

```bash
python -m bluesky.demo --open
```

## Hạn chế

- Phân cụm viewpoint là quyết định nghiên cứu thủ công, chưa được đánh giá liên mã hóa.
- Layout SVG ưu tiên demo offline và khả năng truy nguyên, chưa phải thuật toán bố trí graph tối ưu.
- Status chỉ có ở những mốc argument được canonical data coi là active; demo không nội suy khoảng trống. Node lịch sử không có status được hiển thị màu xám.
- Aggregation agent chỉ đếm và truy nguyên quan hệ; chưa triển khai belief revision hay solver.
- Một số metadata nguồn còn bất định như đã ghi trong dataset.

## Hướng mở rộng

Ưu tiên tiếp theo là đánh giá độ ổn định của mapping viewpoint, bổ sung snapshot diff, tạo đường dẫn giải thích xuyên thời gian, tích hợp solver lập luận và thử nghiệm protocol tương tác agent nhưng vẫn giữ provenance ở cấp argument.
