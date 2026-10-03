// Forced into the host build of projectM by tools/projectm-host-tests.sh. Apple's OpenGL 4.1 has no
// glInvalidateFramebuffer (used by patch 0009); a no-op stands in, as in preset-lab's worker.
#pragma once
#ifdef __APPLE__
#define glInvalidateFramebuffer(target, count, attachments) ((void)0)
#endif
