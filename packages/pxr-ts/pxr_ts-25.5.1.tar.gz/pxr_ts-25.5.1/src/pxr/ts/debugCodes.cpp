// Copyright 2024 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./debugCodes.h"
#include <pxr/tf/registryManager.h>

namespace pxr {


TF_REGISTRY_FUNCTION(pxr::TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(
        TS_DEBUG_LOOPS,
        "Diagnostic output for looping splines");
    TF_DEBUG_ENVIRONMENT_SYMBOL(
        TS_DEBUG_SAMPLE,
        "Diagnostic output for sampling splines");
}


}  // namespace pxr
