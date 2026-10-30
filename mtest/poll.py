import modal, os
c = modal.FunctionCall.from_id(open("mtest/call_id.txt").read().strip())
try:
    out = c.get(timeout=150)
except TimeoutError:
    print("RUNNING"); raise SystemExit
os.makedirs("mtest/out", exist_ok=True)
for k, v in out.items(): open(f"mtest/out/{k}", "wb").write(v)
print("DONE", sorted(out), "gpu seconds:", out.get("_seconds.txt", b"?").decode())
