# Settings reference

Open the panel with Center, Enter or Menu. Use Up / Down to select a row and Left / Right to change its value.

All is the default music category. Your selected category is saved.

| Setting | Values | Default |
|---|---|---|
| Auto change | Off, On | On |
| Music category | All, Dance | All |
| Preset duration | 10, 15, 20, 30, 45, 60, 90 s | 30 s |
| Transition | Instant, 1–10 s | 7 s (2 s on low-end devices) |
| Resolution | Auto, or a fixed height up to the panel resolution and the memory limit | Auto |
| Frame rate | The TV's refresh rate, half or a quarter of it, at least 24 fps (e.g. 30 or 60 fps at 60 Hz) | Half the refresh rate: 30 fps at 60 Hz, 25 at 50 Hz |

*Advanced ›* opens a second panel:

| Setting | What it does | Default |
|---|---|---|
| Detail | Mesh detail for preset motion: Minimal, Low, Medium, High, Ultra | Depends on the device |
| Line thickness | How thick waveforms and shape outlines are. *MilkDrop (1024×768)*: 1 px at MilkDrop's original resolution, growing with the picture (1.6 px at 1080p, 3.2 px at 4K), so presets look as their authors made them. *1080p*: 1 px at 1080p, 2 px at 4K (thinner lines, a darker look on some presets) | MilkDrop (1024×768) |
| Transitions | *Auto* blends the two running presets and keeps the frame rate up: when the GPU is the limit, both render at a lower resolution during the blend (75% to start, down to 50%, back up when there is headroom); when the CPU is the limit, the outgoing preset renders every second frame. *Classic* always blends at full resolution. *Lightweight* fades a still image of the old preset for at most 3 s. | Auto |
| Cut on loud beats | Lets projectM cut to the next preset on a loud beat, like MilkDrop, instead of only blending | Off |
| Memory limit | Caps the resolution by installed memory: under 1.6 GB 1080p, under 2.6 GB 1260p, under 3.6 GB 1440p, otherwise no cap | On |
| Skip slow presets | Skips presets that stay below half the target frame rate even at the lowest resolution, or that a lower resolution does not help (limited by the CPU); such a preset is skipped for good on this TV | On |
| Skip blank presets | Moves on from presets that stay black while music plays; skips them for good the second time | On |
| Track titles | *On* when notification access is granted; select it for how to allow it (see [Track titles](getting-started.md#track-titles)) | – |
| Auto-update | Checks GitHub for a new release at every launch and every 6 hours while open, and downloads it; an *Install* row then appears at the top of the settings panel. *Via F-Droid* when the app was installed from F-Droid | Off |
| Skipped presets | Shows how many presets are skipped; select it to reset the list | – |
| Diagnostics | Render size, panel, UI size, frame rate, blend (style and resolution), audio source and level, track titles (access), update status, device tier | – |


![Main settings panel with Music category All](images/setup/main-settings.png)

![Advanced settings panel and Diagnostics](images/setup/advanced-settings.png)

The tables describe version 2.1.3; screenshots use an isolated test installation. See [Dance](dance.md) for collection details and [Troubleshooting](troubleshooting.md) for audio and performance problems.
