# -*- coding: utf-8 -*-

from translate import Translator

# 由于 translate 库的 Translator 类不接受语言代码作为参数，我们需要移除 'chinese' 和 'english'
trans_all = Translator()

text = "这间客厅空间充满了温暖与宁静的氛围。墙面采用淡雅的米白色，配合简约的灰色沙发，整体色调清新、柔和。窗外的阳光透过宽大的落地窗洒进来，给室内增添了自然的光泽。角落里，一盆绿色植物为空间带来了一抹生气。电视墙上的艺术装饰画简洁却富有层次感，与整体风格完美契合。木质地板温润的色泽与现代感十足的家具相互映衬，给人一种舒适放松的感觉。房间中央，简约的茶几上摆放着几本书和一只精致的花瓶，静谧而雅致。空间布局合理，流线感十足，让人一进入就有种身心放松的感觉。无论是与家人一起聚会，还是独自享受一杯茶的宁静时光，这里都仿佛是一个理想的避风港。"
print(text)
text_to = trans_all.translate(text, src='zh', dest='en')

print(text_to)