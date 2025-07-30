#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Toolkit 快速開始範例
5 分鐘學會核心功能
"""

from redis_toolkit import RedisToolkit

# 1. 建立工具包實例
print("1️⃣ 建立 RedisToolkit 實例")
toolkit = RedisToolkit()

# 2. 存儲不同類型的資料（自動序列化）
print("\n2️⃣ 存儲各種資料類型")
toolkit.setter("使用者", {"姓名": "小明", "年齡": 25, "VIP": True})
toolkit.setter("分數列表", [95, 87, 92, 88, 90])
toolkit.setter("啟用功能", True)
toolkit.setter("音訊資料", "模擬音訊位元組資料...".encode("utf-8"))

print("✓ 已存儲：字典、列表、布林值、位元組資料")

# 3. 取得資料（自動反序列化）
print("\n3️⃣ 取得資料")
使用者 = toolkit.getter("使用者")
分數 = toolkit.getter("分數列表")
功能 = toolkit.getter("啟用功能")

print(f"使用者資料: {使用者}")
print(f"分數列表: {分數}")
print(f"功能狀態: {功能} (類型: {type(功能).__name__})")

# 4. 批次操作
print("\n4️⃣ 批次操作")
batch_data = {
    "產品_A": {"名稱": "智慧手錶", "價格": 2999},
    "產品_B": {"名稱": "無線耳機", "價格": 1299},
    "產品_C": {"名稱": "充電器", "價格": 299}
}

toolkit.batch_set(batch_data)
products = toolkit.batch_get(["產品_A", "產品_B", "產品_C"])
print(f"批次取得產品: {len(products)} 項")

# 5. 使用原生 Redis 功能
print("\n5️⃣ 使用原生 Redis 功能")
toolkit.client.lpush("購物車", "產品_A", "產品_B")
購物車長度 = toolkit.client.llen("購物車")
print(f"購物車商品數量: {購物車長度}")

# 6. 發布訂閱（簡單示例）
print("\n6️⃣ 發布訊息")
toolkit.publisher("用戶事件", {
    "事件": "購買", 
    "使用者": "小明", 
    "商品": ["產品_A", "產品_B"],
    "總金額": 4298
})
print("✓ 已發布用戶事件訊息")

# 7. 清理
print("\n7️⃣ 清理資源")
toolkit.cleanup()
print("✓ 資源清理完成")

print("\n🎉 快速開始完成！")
print("💡 你已經學會了 Redis Toolkit 的所有核心功能")