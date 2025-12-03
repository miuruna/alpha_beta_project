import random

"""木のノードを表すクラス"""
class Node:
    # 初期かメソッド(Javaでいうコンストラクタ)
    def __init__(self, id, value=None, children=None):
        # ノードの名前
        self.id = id
        # 葉ノードがもつ数字(葉以外はNoneになる)
        self.value = value

        if children is None:
            self.children = []
        else:
            self.children = children
        
    # 自分が「葉(末端)」かどうかを判定するメソッド
    def is_leaf(self):
        return len(self.children) == 0

"""
指定された深さと分岐数で木を自動生成する関数

Args:
    depth(int): 木の深さ
    branching_factor(int): 1つのノードから出る枝の数
    values(list): 葉にセットする値のリスト, Noneならランダム生成
"""
def create_game_tree(depth, branching_factor, values=None):
    # 葉の総数
    num_leaves = branching_factor ** depth

    # 値のリストが指定されていなければランダムにつくる
    if values is None:
        values = [random.randint(1, 99) for _ in range(num_leaves)]
    
    # 値のリストを順番に取り出すための「イテレータ」を用意
    val_iterator = iter(values)

    # 再帰的にノードをつくる内部関数
    def build(current_id, current_depth):
        if current_depth == depth:
            try:
                val = next(val_iterator)
            except StopIteration:
                val = 0
            return Node(current_id, value=val)
        
        # 再帰ステップ: 子ノードを分岐数だけつくる
        children = []
        for i in range(branching_factor):
            child_id = f"{current_id}_{i}"
            children.append(build(child_id, current_depth + 1))
        
        # 子ノードをもつ中間ノードを返す
        return Node(current_id, children=children)
    return build("Root", 0)

