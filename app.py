import streamlit as st
import graphviz
import math
import random

from models import create_game_tree
from algorithms import alphabeta

# ==========================================
# 1. ページ設定とセッション管理
# ==========================================
st.set_page_config(layout="wide", page_title="Alpha-Beta Visualizer")
st.title(":material/account_tree: Alpha-Beta Pruning: 相互再帰")

# サイドバー設定
st.sidebar.header(":material/park: 木の設定")
depth = st.sidebar.slider("木の深さ", 2, 4, 3)
branching = st.sidebar.slider("分岐数", 2, 3, 2)
seed = st.sidebar.number_input("乱数シード", value=42)

# リセットボタン
if st.sidebar.button("木を再生成"):
    seed = random.randint(0, 1000)

random.seed(seed)

# ==========================================
# 2. ロジック実行
# ==========================================
# 木を作成
root = create_game_tree(depth, branching)

# ログを記録するリストを用意
log = []

# アルゴリズム実行
# 結果は log リストに書き込まれる
alphabeta(root, 0, -math.inf, math.inf, True, log)

# ==========================================
# 3. タイムライン制御
# ==========================================
total_steps = len(log)
if "step" not in st.session_state:
    st.session_state.step = 0

# コールバック関数（ボタンが押されたときに動く関数）
def prev_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

def next_step():
    if st.session_state.step < total_steps - 1:
        st.session_state.step += 1

# レイアウト作成（左ボタン、スライダー、右ボタン）
t_col1, t_col2, t_col3 = st.columns([1, 8, 1])

with t_col1:
    # 前へボタン (on_clickで関数を呼び出す)
    st.button("◀", on_click=prev_step, use_container_width=True)

with t_col3:
    # 次へボタン
    st.button("▶", on_click=next_step, use_container_width=True)

with t_col2:
    # スライダー (key="step" とすることで、session_state.stepと自動連動します)
    st.slider(
        "ステップ操作", 
        0, total_steps - 1, 
        key="step", 
        label_visibility="collapsed" # ラベルを隠してスッキリさせる
    )

# 現在のステップの情報を取得
state = log[st.session_state.step]

# ==========================================
# 4. 画面描画 (左: 木, 右: コード)
# ==========================================
col_left, col_right = st.columns([1.5, 1])

# --- 左側: 木の可視化 ---
with col_left:
    st.subheader(":material/search: 探索木の様子")

    graph = graphviz.Digraph()
    graph.attr(rankdir='TB')

    # 現在のハイライト対象を決める
    active_id = state['node_id']
    finish_mode = False
    
    if state['event'] == 'finish':
        finish_mode = True # 終了モードフラグ

    # 再帰的にグラフを描く関数
    def draw_tree(node, active_node_id, pruned_info):
        fillcolor = 'white'
        style = 'filled'
        penwidth = '1'
        fontcolor = 'black'

        if finish_mode and node.id == "Root":
            fillcolor = '#90EE90' # LightGreen
            penwidth = '3'
            label_extra = "\n(決定!)"
        elif node.id == active_node_id:
            fillcolor = '#FDD835' # 黄色
            penwidth = '3'
            label_extra = ""
        elif node.id in pruned_info:
            fillcolor = '#FFCDD2' 
            style = 'filled,dashed'
            fontcolor = 'gray'
            label_extra = ""
        else:
            label_extra = ""
        
        # ラベル
        label = f"{node.id}"
        if node.is_leaf():
            label += f"\n({node.value})"
        elif node.id == "Root":
            label += "\n(MAX)"
        
        graph.node(
            node.id,
            label,
            style=style,
            fillcolor=fillcolor,
            color='black',
            penwidth=penwidth,
            fontcolor=fontcolor
        )

        # 子ノードへの線
        for child in node.children:
            edge_style = 'solid'
            if child.id in pruned_info:
                edge_style = 'dashed' # 枝刈りされた枝は点線
            
            graph.edge(node.id, child.id, style=edge_style)
            draw_tree(child, active_node_id, pruned_info)
    
    # 枝刈り情報の抽出 (現在のステップでpruneアクションがあればその対象を取得)
    pruned_nodes = set()
    
    # 最初(0)から現在(st.session_state.step)までのログを振り返る
    for i in range(st.session_state.step + 1):
        past_state = log[i]
        if past_state['event'] == 'prune':
            p_list = past_state.get('pruned_children', [])
            for p_id in p_list:
                pruned_nodes.add(p_id)
    
    pruned_list = list(pruned_nodes)

    draw_tree(root, state['node_id'], pruned_list)
    st.graphviz_chart(graph, use_container_width=True)

# --- 右側: コードと変数の可視化 ---
with col_right:
    st.subheader(":material/terminal: 実行中のコード")

    # 1. 変数パネル
    c1, c2, c3 = st.columns(3)
    
    a_str = "-∞" if state['alpha'] == -math.inf else str(round(state['alpha'], 2))
    b_str = "+∞" if state['beta'] == math.inf else str(round(state['beta'], 2))
    
    v_val = state.get('value', None)
    if v_val == math.inf: v_str = "+∞"
    elif v_val == -math.inf: v_str = "-∞"
    else: v_str = str(v_val)

    c1.metric("Alpha (Max)", a_str)
    c2.metric("Beta (Min)", b_str)
    c3.metric("Value", v_str)

    st.info(f"**解説**: {state['description']}")

    # 2. コードハイライト表示
    # ★ここを変更: if文を使って条件を明示したコードにする
    code_text = """def max_level(node, alpha, beta):
    # [MAX] 自分のターン
    if node.is_leaf(): return node.value

    value = -∞
    for child in children:
        ret = min_level(child, ...)
        
        # もし戻り値(ret)が暫定値より大きければ
        if ret > value:
            value = ret       # Value更新
            
        # もし暫定値がAlpha(最低保証)より大きければ
        if value > alpha:
            alpha = value     # Alpha更新
        
        # 枝刈りチェック
        if beta <= alpha:
            break # Pruning!
    return value

# -----------------------------------

def min_level(node, alpha, beta):
    # [MIN] 相手のターン
    if node.is_leaf(): return node.value

    value = +∞
    for child in children:
        ret = max_level(child, ...)
        
        # もし戻り値(ret)が暫定値より小さければ
        if ret < value:
            value = ret       # Value更新

        # もし暫定値がBeta(許容上限)より小さければ
        if value < beta:
            beta = value      # Beta更新
        
        # 枝刈りチェック
        if beta <= alpha:
            break # Pruning!
    return value"""

    # ★ここを変更: コードが長くなったので行番号(0始まり)を再マッピング
    line_map = {
        # --- MAX関数 ---
        ("visit", True): 0,          # def max_level
        ("leaf", True): 2,           # if node.is_leaf
        ("update_val", True): 10,    # value = ret (ifの中)
        ("update_alpha", True): 14,  # alpha = value (ifの中)
        ("prune", True): 18,         # break
        
        # --- MIN関数 ---
        # 空行などを考慮してカウント
        ("visit", False): 23,        # def min_level
        ("leaf", False): 25,         # if node.is_leaf
        ("update_val", False): 33,   # value = ret (ifの中)
        ("update_beta", False): 37,  # beta = value (ifの中)
        ("prune", False): 41,        # break
        ("finish", True): 20,
    }

    key = (state['event'], state['is_max'])
    target_line = line_map.get(key, -1)

    lines = code_text.split('\n')
    if 0 <= target_line < len(lines):
        # 矢印を追加
        lines[target_line] += "  # <--- 🟢 今ココ！"

    st.code("\n".join(lines), language="python")

    with st.expander("詳細ログデータを見る"):
        st.write(state)