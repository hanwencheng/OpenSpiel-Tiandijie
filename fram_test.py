ATTRIBUTE_NAMES = ['力量', '敏捷', '智力']
growth_coefficient_tuple = (1.2, 1.1, 1.3)
added_attributes_tuple = (5, 3, 4)

# 假设我们有一个字典来存储结果
attributes = {name: 0 for name in ATTRIBUTE_NAMES}

# 迭代zip后的序列
for attr_name, growth_coefficient, added_value in zip(
        ATTRIBUTE_NAMES, growth_coefficient_tuple, added_attributes_tuple):
    # 示例操作：更新attributes字典
    attributes[attr_name] += growth_coefficient * added_value

# 打印更新后的attributes
print(3.0*1.1)