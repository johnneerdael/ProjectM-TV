# Settings reference

Open the panel with Center, Enter or Menu. Use Up / Down to select a row and Left / Right to change its value.

All is the default music category. Your selected category is saved.

| Setting | Values | Default |
|---|---|---|
| Auto change | Off, On | On |
| Music category | All, Dance | All |
| Preset duration | 10, 15, 20, 30, 45, 60, 90 s | 30 s |
| Resolution | Auto or numeric fixed heights up to 1330p, within the panel and memory limits; Native uses the detected panel height when it is above 1330p and memory permits | Auto |

The standard APK uses the Native-capable core. **Native** is an explicit opt-in with known picture and resource limits. It uses the TV's detected panel height, such as 2160p on a 4K panel, even if Android's menus run at 1080p. It can show more detail, but can run slower and use more memory. It does not lower resolution for slow presets or memory-pressure reports; use Auto for adaptive performance. Auto transitions can still render a blend at lower resolution. Higher resolution can also change a feedback preset's brightness, colour or pattern, and the compensation does not preserve every preset's look.

Native appears only when the panel height exceeds 1330p and **Memory limit** permits that full height. If a saved Native choice becomes unavailable, the app uses Auto. Older saved numeric 1440p/4K choices remain capped; they do not automatically select Native. Auto remains the default and stops at 1330p even when Memory limit is off.

In the Native-capable core, the feedback correction also applies to eligible presets above their authored reference size in Auto and numeric fixed modes, including 1330p. It can change their patterns even when the resolution setting stays the same.

A build using the **capped core** has no Native choice or feedback diffusion. It keeps internal rendering at or below 1330p even when its host requests a larger surface, and upscales the result for presentation. If that render target is unavailable, the core skips the frame instead of exceeding the cap. The canonical core AAR used by Milkbeat selects this capped policy; the standard ProjectM TV APK uses the Native-capable policy. Core developers can choose the policy in the [build instructions](development.md#core-rendering-policies).

*Track display ›* opens a panel for the playing track:

| Setting | What it does | Default |
|---|---|---|
| Track info | Shows the cover, artist and title of the playing track in the upper left, as Milkbeat does; *Off · Allow* while notification access is missing, select it for how to allow it (see [Track titles](getting-started.md#track-titles)) | On |
| Show for | 10, 20, 30 or 60 s from the start of each track, or *Always* while music plays (it goes when playback stops or pauses) | Always |
| Pill style | Shows the track as one line (*Title — Artist*) in the small pill in the lower left instead | Off |

*Advanced ›* opens a second panel:

| Setting | What it does | Default |
|---|---|---|
| Frame rate | The TV's refresh rate, half or a quarter of it, at least 24 fps (e.g. 30 or 60 fps at 60 Hz) | Half the refresh rate: 30 fps at 60 Hz, 25 at 50 Hz |
| Detail | Mesh detail for preset motion: Minimal, Low, Medium, High, Ultra | Depends on the device |
| Transition | How long the blend from one preset to the next takes: Instant, 1–10 s | 7 s (2 s on low-end devices) |
| Transitions | *Auto* blends the two running presets and keeps the frame rate up: when the GPU is the limit, both render at a lower resolution during the blend (75% to start, down to 50%, back up when there is headroom); when the CPU is the limit, the outgoing preset renders every second frame. *Classic* always blends at full resolution. *Lightweight* fades a still image of the old preset for at most 3 s. | Auto |
| Cut on loud beats | Lets projectM cut to the next preset on a loud beat, like MilkDrop, instead of only blending | Off |
| Memory limit | Caps render height by reported RAM: under 1600 MB 1080p, under 2600 MB 1260p, under 3600 MB 1440p, otherwise no RAM cap. Auto and numeric choices still stop at 1330p. Native appears only if the whole detected panel height fits the limit | On |
| Skip slow presets | Skips presets that stay below half the target frame rate even at the lowest resolution, or that a lower resolution does not help (limited by the CPU); such a preset is skipped for good on this TV | On |
| Skip blank presets | Moves on from presets that stay black while music plays; skips them for good the second time | On |
| Auto-update | Checks GitHub for a new release at every launch and every 6 hours while open, and downloads it; an *Install* row then appears at the top of the settings panel. *Via F-Droid* when the app was installed from F-Droid | Off |
| Skipped presets | Shows how many presets are skipped; select it to reset the list | – |
| Diagnostics | Render size, panel, UI size, frame rate, blend (style and resolution), audio source and level, track display (access, corner or pill, how long), update status, device tier | – |


![Main settings panel with Music category All, next to the track in the upper left](images/setup/main-settings.png)

![Track display panel with Track info On, Show for Always and Pill style Off](images/setup/track-display-settings.png)

![Advanced settings panel and Diagnostics, below the track in the upper left](images/setup/advanced-settings.png)

The tables describe the current source, including the optional Native mode; screenshots use an earlier isolated test installation. See [Dance](dance.md) for collection details and [Troubleshooting](troubleshooting.md) for audio and performance problems.
