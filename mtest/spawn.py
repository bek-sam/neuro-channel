import modal, json, sys
scenes = [{"text":"t","prompt":"Extreme close-up of real human neurons with branching dendrites and glowing electrical impulses traveling along axons, blue and cyan bioluminescent light","motion":"signals racing along the axons"},
          {"text":"t","prompt":"Anatomically accurate human brain floating in darkness, pink-grey cortex with folds, subtle golden glowing neural pathways, side view","motion":"slow orbit camera"}]
c = modal.Function.from_name("video-gen-render", "render_scenes").spawn(scenes, [0, 1])
open("mtest/call_id.txt", "w").write(c.object_id); print("spawned", c.object_id)
