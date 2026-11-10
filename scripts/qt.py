# scripts/qt.py —— Orchestrator 骨架 v2（P14/P26/P15）
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
STATE_PATH = ROOT / "state" / "state.json"

def load_state():
    """读台账：把 JSON 文件变成 Python 能看懂的字典"""
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

def save_state(state):
    """写台账：把更新后的字典存回 JSON 文件"""
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def fingerprint(path):
    """给文件算指纹：内容变一点，指纹全变（P15 审计证据）"""
    data = (ROOT / path).read_bytes()
    return hashlib.sha256(data).hexdigest()[:16]

def seal_artifacts(state):
    """把台账里每个产物的哈希填上"""
    for item in state["artifacts"]:
        item["hash"] = fingerprint(item["path"])
    save_state(state)

def main():
    state = load_state()
    print(f"案件：{state['case_id']}  版本：{state['version']}")
    print(f"当前状态：{state['status']}")

    # P26 条件路由：根据状态决定下一步去哪
    if state["status"] == "pending":
        state["status"] = "generator_working"
        seal_artifacts(state)  # ← 派活前给现有产物盖指纹
        print("→ 路由决定：分派给 Generator（状态+哈希已写入台账）")
    else:
        print("→ 状态机还没写这个分支（期末作业你来扩展）")

if __name__ == "__main__":
    main()