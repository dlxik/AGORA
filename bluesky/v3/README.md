# AGORA V3 — Dynamic Agent Society

V3 là **Dynamic Agent Society with Argumentation Semantics and Emergent Dynamics**. V3 mở rộng V2 từ agency ở cấp viewpoint-agent sang biến đổi cấu trúc và trạng thái tập thể của xã hội agent. Đây không phải chatbot, mô phỏng dân số thật hay mô hình xã hội học đã được kiểm định.

## 1. V1, V2 và V3

- **V1 — Reactive Viewpoint Agents:** dựng temporal argument graph `G_t`, mapping argument → viewpoint và snapshot diff.
- **V2 — Autonomous Argumentative Agents:** thêm vòng `OBSERVE → REASON → SELECT → INTERACT → REVISE`, internal belief và heuristic score.
- **V3 — Dynamic Agent Society:** giữ nguyên V1/V2, thêm formal semantics baseline, cohesion, structural prevalence, institutional protocol, dynamic-viewpoint candidates và society events.

V3 import và tái sử dụng V1/V2; không sửa canonical CSV, base viewpoint mapping hoặc package cũ.

## 2. Kiến trúc

```text
Canonical data → V1 G_t → V2 agent engines
             → V3 argumentation semantics
             → viewpoint dynamics + structural prevalence
             → society metrics + dynamics events
             → validation/evaluation → V3 trace + HTML
```

Runtime society structure giữ một bản sao bất biến của `base_viewpoint_mapping`. Derived viewpoint chỉ tồn tại trong trace V3.

## 3. Temporal semantics `t`

`t1…t6` là mốc thông tin thật của CTQ. V3 không biến `t` thành vòng debate và không tạo timestamp giả.

## 4. Deliberation semantics `k`

`k` là iteration nội bộ bên trong một `t`. Simulation stop (`NO_OP`, repeated state, max steps) chỉ mô tả việc dừng thuật toán, không đồng nghĩa social consensus.

`SocietyEvent` là record có kiểu, không phải clock thứ ba. Mỗi event ghi `t`, `k`, agent/argument liên quan, metric, threshold, explanation và provenance.

## 5. Argumentation semantics

`WeightedBipolarSemantics` là fixed-point baseline xác định trên support/attack graph:

```text
relational_signal_i = weighted_mean(supporter scores - attacker scores)
s'_i = (1-d) × heuristic_base_i + d × (0.5 + 0.5 × relational_signal_i)
```

Relation weight lấy từ canonical relation confidence. Iteration dừng khi max delta ≤ epsilon. Output giữ input IDs, relation contributions, weights, accepted/rejected/undecided, iteration trace và explanation. Đây không phải ASPIC+, factual truth hay social consensus.

UI cho phép so sánh `heuristic score → semantic score` cho từng belief.

Trước belief revision, V3 tạo score tích hợp:

```text
revision_score = (1 - semantic_revision_blend) × heuristic_score
               + semantic_revision_blend × semantic_score
```

Default blend là `0.35`; cả heuristic lẫn semantic score gốc vẫn được giữ trong trace.

## 6. Viewpoint cohesion

Với mỗi runtime viewpoint:

```text
cohesion = 0.35 × status agreement
         + 0.20 × mean conclusion-token Jaccard
         + 0.20 × internal support density
         + 0.15 × (1 - internal attack density)
         + 0.10 × confidence consistency
```

`internal_conflict`, confidence dispersion và từng component được ghi riêng. Cohesion là proxy cấu trúc của modeled beliefs, không phải group cohesion đo ngoài đời.

## 7. Split/merge

Split score:

```text
0.35 × status disagreement
+ 0.25 × internal attack ratio
+ 0.25 × normalized confidence dispersion
+ 0.15 × conclusion dissimilarity
```

Candidate yêu cầu ít nhất hai belief và score ≥ threshold.

Merge score:

```text
0.40 × status similarity
+ 0.25 × confidence similarity
+ 0.20 × cross-support ratio
+ 0.15 × low cross-conflict
```

Candidate còn yêu cầu có canonical cross-support. Default chỉ phát hiện candidate. `RuntimeSocietyStructure` hỗ trợ derived IDs `VPxx-A/B` và `MERGE(...)`, parent, arguments, trigger event và provenance; auto split/merge mặc định tắt vì CTQ chưa cung cấp căn cứ đủ mạnh để tự động tái cấu trúc.

## 8. Structural prevalence `S_i`

```text
S_i = 0.25 active arguments
    + 0.20 unique sources
    + 0.15 temporal persistence
    + 0.15 incoming support
    + 0.15 outgoing influence
    + 0.10 interaction reach
```

Các component được chuẩn hóa trong society đang active. Trace còn ghi `visibility_proxy`, `persistence`, `source_diversity`, `interaction_reach` và `real_social_prevalence = null`.

> Đây là structural proxy, không phải phép đo mức ủng hộ thật của công chúng.

## 9. Institutional-agent protocol

Agent `contextual` dùng allow-list riêng:

- `PROVIDE_EVIDENCE`
- `CLARIFY_NORM`
- `CLARIFY_AUTHORITY`
- `CHALLENGE_INVALID_GROUNDING`
- `NO_OP`

Action phải ground bằng `official_document` hoặc `authority_statement`, argument/relation/source canonical. Institutional agent không được force belief, set confidence, suppress agent hoặc force convergence. Ảnh hưởng được chuẩn hóa rồi đi qua observation → reasoning → interaction → revision như agent khác.

Personal/organization agent types được kiến trúc hỗ trợ nhưng **không được instantiate trong CTQ vì chưa có dữ liệu thật**.

## 10. Society dynamics

`SocietyDynamicsEngine` phát hiện theo threshold minh bạch:

- structural dominance shift;
- convergence proxy;
- fragmentation proxy, weak components và isolated agents;
- persistent conflict từ attack/challenge lặp qua `k`;
- viewpoint stabilization;
- split/merge candidates.

`polarization_proxy` là mean pairwise distance giữa mean confidence của agents. Không event nào được diễn giải là hiện tượng xã hội học đã được xác nhận.

## 11. Society events

`SocietyEvent` có:

- `event_id`, `timestamp`, `deliberation_step`, `event_type`;
- `involved_agents`, `involved_arguments`;
- `metric_snapshot`, `threshold`, `explanation`;
- provenance tới interaction, action, argument, relation và source IDs khi có.

## 12. Evaluation

`evaluation.py` hỗ trợ:

- sensitivity: semantics damping thấp/cao, thresholds nghiêm hơn, max steps;
- ablation: source quality, relation confidence, observed action effects, institutional policy, viewpoint dynamics;
- deterministic replay bằng cùng input/config;
- outcome comparison cho final beliefs, dominance, candidates, convergence và event types.

Engine không hardcode CTQ ID; CTQ chỉ là demo dataset.

## 13. Provenance và bất biến

`validation_v3.py` kiểm tra semantics/event/protocol IDs cùng V2 action/revision provenance. `demo_v3.py` hash toàn bộ canonical inputs trước và sau run; run bị từ chối nếu dữ liệu thay đổi.

## 14. UI

V3 kế thừa trực tiếp V2 template/design language và thêm:

- tab `Xã hội`: dominance, cohesion, prevalence, convergence, fragmentation và candidates;
- tab `Sự kiện`: event theo `t/k`, click để highlight agents;
- so sánh heuristic ↔ semantics trong inspector;
- dominant badge, cohesion halo, split/persistent-conflict encoding;
- toàn bộ hover/click provenance và playback `t`, `k`, `t+k` của V2.

## 15. Chạy

```bash
python -m bluesky.v3.demo_v3
python -m bluesky.v3.demo_v3 --open
python -m bluesky.v3.demo_v3 --verbose
python -m bluesky.v3.demo_v3 --evaluation
python -m unittest discover -s tests -v
```

Outputs:

- `bluesky/outputs/dynamic_agent_society_v3.html`
- `bluesky/outputs/v3_simulation_trace.json`
- `bluesky/outputs/v3_evaluation_report.json` khi dùng `--evaluation`

## Hạn chế

- Formulas/thresholds là baseline nghiên cứu minh bạch, chưa được hiệu chỉnh thực nghiệm.
- Mapping base là quyết định thủ công; candidate không chứng minh viewpoint xã hội thật đã split/merge.
- Confidence là internal simulation state, không phải factual probability.
- Connected components và dominance chỉ phản ánh graph/modeled interactions.
- Current CTQ demo phát hiện candidate; runtime structural update được scaffold nhưng mặc định tắt.
