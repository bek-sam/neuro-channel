import modal, json
for m, cid in json.load(open("test1/calls.json")).items():
    try: r = modal.FunctionCall.from_id(cid).get(timeout=0); print(m, "DONE", r)
    except TimeoutError: print(m, "RUNNING")
    except Exception as e: print(m, "FAILED", str(e)[:300])
