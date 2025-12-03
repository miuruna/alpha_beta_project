import math

def alphabeta(node, depth, alpha, beta, is_maximizing, log):
    result = max_level(node, depth, alpha, beta, log)
    log.append({
        "event": "finish", 
        "node_id": node.id, # Rootに戻ってきました
        "value": result,    # 最終的なスコア
        "alpha": alpha,     # ここは初期値のままですが今回は表示用なのでOK
        "beta": beta,
        "is_max": True,
        "description": f":material/sports_score: 探索終了！ ルートが選んだ最終スコアは 【{result}】 です"
    })
    return result

# =================================================
# 1. MAX_LEVEL (自分のターン)
# =================================================
def max_level(node, depth, alpha, beta, log):
    # 訪問ログ
    log.append({
        "event": "visit",
        "node_id": node.id,
        "alpha": alpha,
        "beta": beta,
        "is_max": True,
        "description": f"[MAX]ノード {node.id}に到着"
    })

    # 葉ノードチェック
    if node.is_leaf():
        log.append({
            "event": "leaf",
            "node_id": node.id,
            "value": node.value,
            "alpha": alpha,
            "beta": beta,
            "is_max": True,
            "description": f"葉 {node.id} の値 {node.value} を確認"
        })
        return node.value
    
    value = -math.inf

    for i, child in enumerate(node.children):
        child_val = min_level(child, depth + 1, alpha, beta, log)

        # 値の更新
        old_value = value
        value = max(value, child_val)
        
        if value > old_value:
            log.append({
                "event": "update_val",
                "node_id": node.id,
                "value": value,
                "alpha": alpha,
                "beta": beta,
                "is_max": True, 
                "description": f":material/star_shine: 子の値({child_val}) が 今の暫定値({old_value}) より大きいので更新"
            })
        
        # Alphaの更新
        old_alpha = alpha
        alpha = max(alpha, value)

        if alpha > old_alpha:
            log.append({
                "event": "update_alpha",
                "node_id": node.id,
                "value": value,
                "alpha": alpha,
                "beta": beta,
                "is_max": True,
                "description": f":material/star_shine: 値が元のαよりも大きいため更新 {old_alpha} -> {alpha} に上がりました"
            })
        
        # 枝刈り (Beta Cutoff)
        if beta <= alpha:
            remaining_children = node.children[i+1:]
            pruned_ids = [c.id for c in remaining_children]

            log.append({
                "event": "prune",
                "node_id": node.id,
                "value": value,
                "alpha": alpha,
                "beta": beta,
                "is_max": True,
                "pruned_children": pruned_ids,
                "description": f":material/content_cut:  Beta枝刈り! ({beta} <= {alpha})"
            })
            break
    return value

# =================================================
# 2. MIN_LEVEL (相手のターン)
# =================================================
def min_level(node, depth, alpha, beta, log):
    # 訪問ログ
    log.append({
        "event": "visit",
        "node_id": node.id,
        "alpha": alpha,
        "beta": beta,
        "is_max": False,
        "description": f"[MIN]ノード {node.id} に到着"
    })

    # 葉ノードチェック
    if node.is_leaf():
        log.append({
            "event": "leaf",
            "node_id": node.id,
            "value": node.value,
            "alpha": alpha,
            "beta": beta,
            "is_max": False,
            "description": f"葉 {node.id} の値 {node.value} を確認"
        })
        return node.value
    
    value = math.inf

    for i, child in enumerate(node.children):
        child_val = max_level(child, depth + 1, alpha, beta, log)

        # 値の更新
        old_value = value
        value = min(value, child_val)

        if value < old_value:
            log.append({
                "event": "update_val",
                "node_id": node.id,
                "value": value,
                "alpha": alpha,
                "beta": beta,
                "is_max": False,
                "description": f":material/star_shine: 子の値({child_val}) が 今の暫定値({old_value}) より小さいので更新"
            })
        
        # Betaの更新
        old_beta = beta
        beta = min(beta, value)

        if beta < old_beta:
            log.append({
                "event": "update_beta",
                "node_id": node.id,
                "value": value,
                "alpha": alpha,
                "beta": beta,
                "is_max": False,
                "description": f":material/star_shine: 値が元のβより小さいので更新  {old_beta} -> {beta} に更新"
            })
        
        # 枝刈り (Alpha Cutoff)
        if beta <= alpha:
            remaining_children = node.children[i+1:]
            pruned_ids = [c.id for c in remaining_children]
            log.append({
                "event": "prune",
                "node_id": node.id,
                "value": value,
                "alpha": alpha,
                "beta": beta,
                "is_max": False,
                "pruned_children": pruned_ids,
                "description": f":material/content_cut:  Alpha枝刈り! ({beta} <= {alpha})"
            })
            break
    
    return value