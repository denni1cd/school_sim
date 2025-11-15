# Final Report M3

## Post-merge Verification
- pytest -q school_sim/tests  # 38 passed, 1 warning (pygame pkg_resources deprecation)
- make simulate  # headless run outputs RATING/EVENT lines
- make run  # dummy SDL, observed 10s; manual UI check pending for save/load overlay

## Headless Log (Newest, first 30 lines)
```
RATING,08:01,75.20,+0.20
08:01,Alice,DormA,ClassroomA,25.5,84.6,15.2,69.8
08:01,Becca,DormA,ClassroomA,25.5,84.6,15.2,69.8
08:01,Chloe,DormA,ClassroomA,25.5,84.6,15.2,69.8
RATING,08:02,75.40,+0.20
EVENT,08:02,welcome_assembly,Welcome assembly in the gym.
08:02,Alice,ClassroomA,ClassroomA,26.0,84.2,16.0,69.6
08:02,Becca,ClassroomA,ClassroomA,26.0,84.2,16.0,69.6
08:02,Chloe,ClassroomA,ClassroomA,26.0,84.2,16.0,69.6
RATING,08:03,75.60,+0.20
08:03,Alice,ClassroomA,ClassroomA,26.5,83.8,16.8,69.4
08:03,Becca,ClassroomA,ClassroomA,26.5,83.8,16.8,69.4
08:03,Chloe,ClassroomA,ClassroomA,26.5,83.8,16.8,69.4
RATING,08:04,75.80,+0.20
08:04,Alice,ClassroomA,ClassroomA,27.0,83.4,17.6,69.2
08:04,Becca,ClassroomA,ClassroomA,27.0,83.4,17.6,69.2
08:04,Chloe,ClassroomA,ClassroomA,27.0,83.4,17.6,69.2
RATING,08:05,76.00,+0.20
08:05,Alice,ClassroomA,ClassroomA,27.5,83.0,18.4,69.0
08:05,Becca,ClassroomA,ClassroomA,27.5,83.0,18.4,69.0
08:05,Chloe,ClassroomA,ClassroomA,27.5,83.0,18.4,69.0
RATING,08:06,76.20,+0.20
08:06,Alice,ClassroomA,ClassroomA,28.0,82.6,19.2,68.8
08:06,Becca,ClassroomA,ClassroomA,28.0,82.6,19.2,68.8
08:06,Chloe,ClassroomA,ClassroomA,28.0,82.6,19.2,68.8
RATING,08:07,76.40,+0.20
08:07,Alice,ClassroomA,ClassroomA,28.5,82.2,20.0,68.6
08:07,Becca,ClassroomA,ClassroomA,28.5,82.2,20.0,68.6
08:07,Chloe,ClassroomA,ClassroomA,28.5,82.2,20.0,68.6
RATING,08:08,76.60,+0.20
```

## Observations
- Console save/load actions exercised in tests; headless run still lacks CLI trigger for save (future enhancement).
- Save snapshots now contain budget/rating/policy/curriculum fields; verified via tests.
- `/technomancy/deliverables/` retains only scripts after merge.
