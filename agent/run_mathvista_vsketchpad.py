import os, json, argparse
from main import run_agent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task_root", default="../tasks/mathvista_testmini")
    ap.add_argument("--out_root", default="../outputs/mathvista_testmini")
    ap.add_argument("--task_type", default="geo")   # MathVista 都有图，先用 geo（更贴近 geometry pipeline）
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    os.makedirs(args.out_root, exist_ok=True)
    pids = sorted([p for p in os.listdir(args.task_root) if os.path.isdir(os.path.join(args.task_root,p))])

    if args.limit:
        pids = pids[:args.limit]

    for i, pid in enumerate(pids, 1):
        task_dir = os.path.join(args.task_root, pid)
        out_dir  = os.path.join(args.out_root, pid)
        os.makedirs(out_dir, exist_ok=True)
        print(f"[{i}/{len(pids)}] running pid={pid}")
        run_agent(task_dir, out_dir, task_type=args.task_type, task_name="mathvista")

if __name__ == "__main__":
    main()
