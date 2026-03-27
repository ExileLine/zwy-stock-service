# 库存模型设计

基于文件 `/Users/yangyuexiong/Desktop/测试数据(1).xlsx` 提取的两个工作表建立：

- `产品分类` -> `stock_category`
- `出入库明细表` -> `stock_in_out_record`

## 1. 分类表 `stock_category`

来源表头：

- 产品名称
- 产品品牌
- 产品规格
- PN码
- 物料编码
- 大类
- 序号
- 小码
- 适用设备型号
- 设备类型

字段映射：

- `product_name`：产品名称
- `product_brand`：产品品牌
- `product_spec`：产品规格
- `pn_code`：PN码
- `material_code`：物料编码
- `major_category`：大类编码
- `category_serial_no`：序号
- `category_suffix_code`：小码
- `applicable_device_model`：适用设备型号
- `device_type`：设备类型
- `source_sheet`：来源工作表
- `source_row_no`：来源 Excel 行号
- `remark`：备注

说明：

- 这张表本质上是产品主数据/分类基表，不是单纯的“类目字典”。
- `大类 + 序号 + 小码` 可以拼出一部分内部分类编码。

## 2. 出入库表 `stock_in_out_record`

来源表头：

- 序号
- 类别
- 产品类型
- 产品名称
- 产品品牌
- 产品规格
- 产品描述
- PN码
- 物料编码
- 序列号
- 用于设备类型
- 用于设备品牌
- 用于设备型号
- 大类
- 单号
- 入库数量
- 入库日期
- 入库机房
- 存放位置
- 库存数量
- 领用数量
- 领用日期
- 设备位置
- 原归属用户单位
- 用于机房
- 备注
- 如果用于扩容请备注

字段映射：

- `row_no`：原始序号
- `category_id`：分类 ID，作为与 `stock_category.id` 的逻辑关联字段，不建立外键约束
- `is_outbound`：出入库状态标识，`0` 表示在库，`1` 表示已出库
- `category_name`：类别
- `product_type`：产品类型
- `product_name`：产品名称
- `product_brand`：产品品牌
- `product_spec`：产品规格
- `product_description`：产品描述
- `pn_code`：PN码
- `material_code`：物料编码
- `serial_number`：序列号
- `target_device_type`：用于设备类型
- `target_device_brand`：用于设备品牌
- `target_device_model`：用于设备型号
- `major_category`：大类
- `usage_scene`：用途/设备挂载说明
- `document_no`：单号
- `inbound_qty`：入库数量
- `inbound_date`：入库日期
- `inbound_room`：入库机房
- `storage_location`：存放位置
- `stock_qty`：库存数量
- `outbound_qty`：领用数量
- `outbound_date`：领用日期
- `actual_device_type`：领用后设备类型
- `actual_device_brand`：领用后设备品牌
- `actual_device_model`：领用后设备型号
- `device_position`：设备位置
- `original_owner_org`：原归属用户单位
- `target_room`：用于机房
- `remark`：备注
- `expansion_remark`：扩容备注
- `source_sheet`：来源工作表
- `source_row_no`：来源 Excel 行号

说明：

- Excel 里“用于设备类型/品牌/型号”出现了两组，原始含义不完全稳定。
- `category_id` 用于建立和 `stock_category` 的冗余关联，便于查询与统计，但不使用数据库外键约束。
- `is_outbound` 用于直接标识库存状态，后续统计某个分类库存时可直接按 `category_id + is_outbound=0` 汇总。
- 模型中保留为两组字段：
  - `target_device_*`：产品计划用途或挂载目标
  - `actual_device_*`：产品实际领用后的设备信息
- `usage_scene` 用于保存类似“交换机使用”“上架到名美203机房G列”这类半结构化说明。

## 3. 建模取舍

- 先按 Excel 原始业务含义落两张核心表，保证能直接承接导入。
- 出入库表额外增加 `category_id`，作为逻辑引用字段；历史快照仍然由冗余产品字段保存。
- 没有立即拆成更复杂的主数据、库存台账、出入库流水、设备资产四层模型，避免第一版过度设计。
- 如果后续需要严格库存核算，建议再拆：
  - `stock_product`
  - `stock_lot` / `stock_asset`
  - `stock_transaction`
  - `stock_location`
