import modal, json
s = json.load(open("scroll/scenes.json"))
f = modal.Function.from_name("neuro-render", "render_scenes")
ids = [f.spawn(s, list(range(0, 22))).object_id, f.spawn(s, list(range(22, len(s)))).object_id]
json.dump(ids, open("scroll/calls.json", "w")); print("spawned", ids)
