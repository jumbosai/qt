# scripts/qt.py —— Orchestrator 骨架（对应课件 P14 状态 / P26 条件路由）
# 作用：读台账 → 看状态 → 决定派给谁 → 更新台账

import json
from pathlib import Path

# 找到 state.json 的位置（不管从哪运行都找得到）
STATE_PATH = Path(__file__).parent.parent / "state" / "state.json"

def load_state():
    """读台账：把 JSON 文件变成 Python 能看懂的字典"""
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

def save_state(state):
    """写台账：把更新后的字典存回 JSON 文件"""
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def main():
    state = load_state()
    print(f"案件：{state['case_id']}  版本：{state['version']}")
    print(f"当前状态：{state['status']}")

    # P26 条件路由：根据状态决定下一步去哪
    if state["status"] == "pending":
        state["status"] = "generator_working"
        save_state(state)
        print("→ 路由决定：分派给 Generator（状态已写入台账）")
    else:
        print("→ 状态机还没写这个分支（期末作业你来扩展）")

if __name__ == "__main__":
    main()