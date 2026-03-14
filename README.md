# 美国本地物流 API 自定义发货平台（示例）

这个仓库提供了一个可扩展的发货平台骨架，满足你提到的核心能力：

- 对接美国本地物流 API（当前用 `CarrierGateway` 抽象，默认模拟 USPS）
- 批量上传表格（CSV）并批量创建运单
- 批量下载 PDF 面单（ZIP 打包下载）

## 快速启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

服务启动后访问：

- Swagger 文档: `http://127.0.0.1:8000/docs`
- 健康检查: `GET /health`

## 接口说明

### 1) 批量上传表格创建运单

`POST /shipments/bulk-upload`

- `multipart/form-data`
- 文件字段名：`file`
- 当前示例支持：`.csv`

CSV 最低字段要求：

- `order_id`
- `recipient_name`
- `address1`
- `city`
- `state`
- `zip_code`
- `weight_lb`

返回包含：成功数量、失败数量、每条订单的 tracking/label 信息。

### 2) 批量下载 PDF 面单

`GET /labels/bulk-download?label_ids=LBL-001&label_ids=LBL-002`

- 入参：`label_ids`（可重复）
- 返回：`application/zip`
- ZIP 中每个 `label_id` 会生成一个 PDF 文件（示例为最小可打开 PDF）

## 生产对接建议

1. 在 `app/services/carriers.py` 中替换 `create_shipment`，接入真实承运商 API：
   - USPS / UPS / FedEx
   - 或 ShipEngine / EasyPost 这类聚合商
2. 增加鉴权（JWT / API Key）和租户隔离。
3. 增加数据库持久化（订单、运单、面单 URL、日志）。
4. 对接对象存储（S3）保存原始 PDF，支持异步任务队列。
5. 增加 Excel（xlsx）解析与模板校验。
