# Final Report M1

## Post-merge Verification
- pytest -q school_sim/tests  # 32 passed, 1 warning (pygame pkg_resources deprecation)
- make simulate  # headless run emitted EVENT line at 08:02 (dummy SDL)
- make run  # dummy SDL, observed 10s without exceptions; overlay dismissal pending manual visual check

## Headless Log (Newest, first 30 lines)
```
08:01,Alice,DormA,ClassroomA,25.5,84.6,15.2,69.8
08:01,Becca,DormA,ClassroomA,25.5,84.6,15.2,69.8
08:01,Chloe,DormA,ClassroomA,25.5,84.6,15.2,69.8
EVENT,08:02,welcome_assembly,Welcome assembly in the gym.
08:02,Alice,ClassroomA,ClassroomA,26.0,84.2,16.0,69.6
08:02,Becca,ClassroomA,ClassroomA,26.0,84.2,16.0,69.6
08:02,Chloe,ClassroomA,ClassroomA,26.0,84.2,16.0,69.6
08:03,Alice,ClassroomA,ClassroomA,26.5,83.8,16.8,69.4
08:03,Becca,ClassroomA,ClassroomA,26.5,83.8,16.8,69.4
08:03,Chloe,ClassroomA,ClassroomA,26.5,83.8,16.8,69.4
08:04,Alice,ClassroomA,ClassroomA,27.0,83.4,17.6,69.2
08:04,Becca,ClassroomA,ClassroomA,27.0,83.4,17.6,69.2
08:04,Chloe,ClassroomA,ClassroomA,27.0,83.4,17.6,69.2
08:05,Alice,ClassroomA,ClassroomA,27.5,83.0,18.4,69.0
08:05,Becca,ClassroomA,ClassroomA,27.5,83.0,18.4,69.0
08:05,Chloe,ClassroomA,ClassroomA,27.5,83.0,18.4,69.0
08:06,Alice,ClassroomA,ClassroomA,28.0,82.6,19.2,68.8
08:06,Becca,ClassroomA,ClassroomA,28.0,82.6,19.2,68.8
08:06,Chloe,ClassroomA,ClassroomA,28.0,82.6,19.2,68.8
08:07,Alice,ClassroomA,ClassroomA,28.5,82.2,20.0,68.6
08:07,Becca,ClassroomA,ClassroomA,28.5,82.2,20.0,68.6
08:07,Chloe,ClassroomA,ClassroomA,28.5,82.2,20.0,68.6
08:08,Alice,ClassroomA,ClassroomA,29.0,81.8,20.8,68.4
08:08,Becca,ClassroomA,ClassroomA,29.0,81.8,20.8,68.4
08:08,Chloe,ClassroomA,ClassroomA,29.0,81.8,20.8,68.4
08:09,Alice,ClassroomA,ClassroomA,29.5,81.4,21.6,68.2
08:09,Becca,ClassroomA,ClassroomA,29.5,81.4,21.6,68.2
08:09,Chloe,ClassroomA,ClassroomA,29.5,81.4,21.6,68.2
08:10,Alice,ClassroomA,ClassroomA,30.0,81.0,22.4,68.0
08:10,Becca,ClassroomA,ClassroomA,30.0,81.0,22.4,68.0
```

## Observations
- HUD now reports time/rating/budget; rating defaults to 75.0 until future milestones adjust it.
- Event bus records `welcome_assembly` at 08:02; overlay contract confirmed via tests.
- `/technomancy/deliverables/` contains scripts only post-merge.
