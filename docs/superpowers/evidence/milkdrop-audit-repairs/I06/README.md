# I06 — Fresh wave-point host inputs

Candidate0021 copies wave-point time/FPS/frame/progress/audio values from the freshly loaded wave-frame context before wave-frame code executes. This follows MilkDrop2 `milkdropfs.cpp:2526–2545,2613–2624`; neither main-equation writes nor later wave-frame writes replace that snapshot. Q/T still copy after wave-frame execution. Main variables remain writable.

The actual EEL/GL regression fails baseline at bass1 overwritten in main to.25. It passes after for all ten host inputs, with main inputs changed to other values, wave-frame bass/time changed to99, and preserved Q/T/replay counts. No extra assignment count, allocation, pass or evaluation is added. All45 normal controls pass.

The one supplied lexical original is Shreyas - Carnival loavthephysyq.milk, SHA da5440792b7f6e1dd987024e72261fa90a3ea455354bd0daf38a1075fcdffeef. Main per_frame_2 scales time by.1; enabled wave point hue equations read time. Candidate restores fresh host time for those wave points while keeping main/per-pixel time policy separate. Actual Native4K impact is not credited until a matched before/expected replay. A finite host-input diagnostic is also required. Final capture/timing/integration remain pending.
