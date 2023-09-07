// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The implementation for script based Filters. */

const fs = require('fs');
const tmp = require('tmp');
const { execSync } = require('child_process');
const { EventHandler } = require('autotransform/event/handler');
const { VerboseEvent } = require('autotransform/event/verbose');
const { BulkFilter, FilterName } = require('autotransform/filter/base');
const { replace_script_args } = require('autotransform/util/functions');

class ScriptFilter extends BulkFilter {
    /* A Filter that uses a script to validate Items. */

    constructor(args, script, timeout, chunk_size = null) {
        super();
        this.args = args;
        this.script = script;
        this.timeout = timeout;
        this.chunk_size = chunk_size;
        this.name = FilterName.SCRIPT;
    }

    _get_valid_keys(items) {
        /* Gets the valid keys from the Items using a script. If a <<RESULT_FILE>> arg is used
        it will be replaced with the path of a temporary file that can be used to store a JSON
        encoded list of keys for valid Items. If no such arg is used, the STDOUT of the script
        will be interpreted as a JSON encoded list of keys for valid Items. Additionally, the
        <<ITEM_FILE>> argument will be replaced with the path to a file containing a JSON
        encoded list of the items to validate. */

        const event_handler = EventHandler.get();

        // Get Command
        let cmd = [this.script].concat(this.args);

        const chunk_size = this.chunk_size || items.length;
        const item_chunks = [];
        for (let i = 0; i < items.length; i += chunk_size) {
            item_chunks.push(items.slice(i, i + chunk_size));
        }

        let valid_keys = new Set();
        for (const chunk of item_chunks) {
            const res_file = tmp.fileSync();
            const item_file = tmp.fileSync();
            fs.writeFileSync(item_file.name, JSON.stringify(chunk.map(item => item.bundle())));
            const arg_replacements = {
                "<<RESULT_FILE>>": [res_file.name],
                "<<ITEM_FILE>>": [item_file.name],
            };
            const uses_result_file = cmd.includes("<<RESULT_FILE>>");
            const replaced_cmd = replace_script_args(cmd, arg_replacements);

            // Run script
            event_handler.handle(new VerboseEvent({"message": `Running command: ${replaced_cmd}`}));
            const proc = execSync(
                replaced_cmd.join(' '),
                { encoding: "utf8", timeout: this.timeout * 1000 },
            );

            const stdout = proc.stdout.trim();
            const stderr = proc.stderr.trim();

            if (stdout && uses_result_file) {
                event_handler.handle(
                    new VerboseEvent({"message": `STDOUT:\n${stdout}`}),
                );
            } else if (uses_result_file) {
                event_handler.handle(new VerboseEvent({"message": "No STDOUT"}));

            if (stderr) {
                event_handler.handle(
                    new VerboseEvent({"message": `STDERR:\n${stderr}`}),
                );
            } else {
                event_handler.handle(new VerboseEvent({"message": "No STDERR"}));
            }

            let key_data;
            if (uses_result_file) {
                key_data = JSON.parse(fs.readFileSync(res_file.name, 'utf8'));
            } else {
                key_data = JSON.parse(stdout);
            }
            valid_keys = new Set([...valid_keys, ...key_data]);
        }
        return valid_keys;
    }
}

module.exports = { ScriptFilter };