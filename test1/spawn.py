import modal, json, sys
stage, model, fn = sys.argv[1], sys.argv[2], sys.argv[3]
scenes = [{"text":"Every second, billions of neurons in your brain fire tiny electric signals.","prompt":"Extreme close-up of real human neurons with branching dendrites and glowing electrical impulses traveling along axons, blue and cyan bioluminescent light","motion":"electrical signals racing along the axons, slow push in"},
          {"text":"Your brain weighs about one and a half kilograms, yet it uses around twenty percent of your energy.","prompt":"Anatomically accurate human brain floating in darkness, pink-grey cerebral cortex with folds, cerebellum and brainstem visible, subtle golden neural pathways, side view","motion":"slow orbit camera around the brain"}]
f = modal.Function.from_name("neuro-render2", fn)
c = f.spawn(scenes, [0, 1], "test1") if fn == "run_voice" else f.spawn(stage, model, scenes, [0, 1], "test1")
calls = json.load(open("test1/calls.json")) if __import__("os").path.exists("test1/calls.json") else {}
calls[model] = c.object_id; json.dump(calls, open("test1/calls.json", "w")); print(model, "spawned", c.object_id)
