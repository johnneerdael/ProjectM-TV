// Stand-in for the header projectM's CMake generates (generate_export_header): the host tests
// compile the engine against projectM's public API headers and fakes, not the library itself.
#pragma once
#define PROJECTM_EXPORT
#define PROJECTM_NO_EXPORT
#define PROJECTM_DEPRECATED
