import os, json, argparse
from datasets import load_dataset
from PIL import Image

def build_query_fallback(ex):
    # 兜底：如果 ex 没有 query 字段才用
    qtype = ex.get("question_type")
    atype = ex.get("answer_type")
    precision = ex.get("precision")

    if qtype == "multi_choice":
        inst = "Hint: Answer with the correct option letter (A/B/C/D/...). Put it at the end."
    else:
        if atype == "integer":
            inst = "Hint: Answer with an integer. Put the final value at the end."
        elif atype == "float":
            if precision is None:
                inst = "Hint: Answer with a number. Put the final value at the end."
            else:
                inst = f"Hint: Answer with a number rounded to {int(precision)} decimal place(s). Put the final value at the end."
        elif atype == "list":
            inst = "Hint: Answer with a Python list (e.g., [1, 2, 3]). Put it at the end."
        else:
            inst = "Hint: Put the final answer at the end."

    q = ex["question"]
    choices = ex.get("choices")

    if choices:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        choice_lines = "\n".join([f"({letters[i]}) {c}" for i, c in enumerate(choices)])
        return f"{inst}\nQuestion: {q}\nChoices:\n{choice_lines}"
    return f"{inst}\nQuestion: {q}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="testmini", choices=["testmini","test"])
    ap.add_argument("--max_num", type=int, default=50)
    ap.add_argument("--out_root", default="../tasks/mathvista_testmini")
    args = ap.parse_args()

    ds = load_dataset("AI4Math/MathVista", split=args.split)

    os.makedirs(args.out_root, exist_ok=True)
    n = min(args.max_num, len(ds))

    for i in range(n):
        ex = ds[i]
        pid = str(ex.get("pid", i))
        d = os.path.join(args.out_root, pid)
        os.makedirs(d, exist_ok=True)

        # ✅ 正确拿图：decoded_image 是 PIL Image（官方数据就有这一列）
        img = ex.get("decoded_image", None)
        if isinstance(img, Image.Image):
            img = img.convert("RGB")
        else:
            # 兜底：如果没有 decoded_image（理论上不会），再尝试用 image 路径（通常是相对路径，不一定可用）
            img_path = ex.get("image")
            img = Image.open(img_path).convert("RGB")

        img.save(os.path.join(d, "image.png"))

        # ✅ 官方推荐直接用 query 字段（更一致）
        query = ex.get("query") or build_query_fallback(ex)

        with open(os.path.join(d, "question.txt"), "w", encoding="utf-8") as f:
            f.write(query + "\n")

        meta = {k: ex.get(k) for k in ["pid","question","choices","unit","precision","answer","question_type","answer_type","metadata","image","query"]}
        with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"[{i+1}/{n}] wrote {d}")

if __name__ == "__main__":
    main()
