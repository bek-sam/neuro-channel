import modal, json, os
os.makedirs("scroll/out", exist_ok=True)
for cid in json.load(open("scroll/calls.json")):
    try: out = modal.FunctionCall.from_id(cid).get(timeout=0)
    except TimeoutError: print(cid, "RUNNING"); continue
    except Exception as e: print(cid, "FAILED", e); continue
    for k, v in out.items(): open(f"scroll/out/{k}", "wb").write(v)
    print(cid, "DONE", out.get("_seconds.txt", b"?").decode(), "s")
print("clips:", len([f for f in os.listdir("scroll/out") if f.startswith("clip_")]))
