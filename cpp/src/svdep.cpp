/*
 * svdep.cpp
 *
 * C API implementation for SVDep
 *
 * Copyright 2024 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 */
#include "svdep.h"
#include "SVDepContext.h"

using namespace svdep;

struct svdep_s {
    SVDepContext ctx;
};

extern "C" {

svdep_t svdep_create(void) {
    return new svdep_s();
}

void svdep_destroy(svdep_t ctx) {
    delete ctx;
}

int svdep_add_incdir(svdep_t ctx, const char *path) {
    if (!ctx || !path) return -1;
    return ctx->ctx.addIncdir(path);
}

int svdep_add_root_file(svdep_t ctx, const char *path) {
    if (!ctx || !path) return -1;
    return ctx->ctx.addRootFile(path);
}

int svdep_build(svdep_t ctx) {
    if (!ctx) return -1;
    return ctx->ctx.build();
}

const char *svdep_get_json(svdep_t ctx) {
    if (!ctx) return nullptr;
    return ctx->ctx.getJson().c_str();
}

int svdep_load_json(svdep_t ctx, const char *json) {
    if (!ctx || !json) return -1;
    return ctx->ctx.loadJson(json);
}

int svdep_check_up_to_date(svdep_t ctx, double last_timestamp) {
    if (!ctx) return -1;
    return ctx->ctx.checkUpToDate(last_timestamp);
}

const char *svdep_get_error(svdep_t ctx) {
    if (!ctx) return nullptr;
    const std::string& err = ctx->ctx.getError();
    return err.empty() ? nullptr : err.c_str();
}

} // extern "C"
