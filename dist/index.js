/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 105:
/***/ ((module) => {

module.exports = eval("require")("@actions/core");


/***/ }),

/***/ 82:
/***/ ((module) => {

module.exports = eval("require")("@actions/github");


/***/ }),

/***/ 147:
/***/ ((module) => {

"use strict";
module.exports = require("fs");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat */
/******/ 	
/******/ 	if (typeof __nccwpck_require__ !== 'undefined') __nccwpck_require__.ab = __dirname + "/";
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
const core = __nccwpck_require__(105);
const github = __nccwpck_require__(82);
var fs = __nccwpck_require__(147);

async function main() {
  try {
    await create_or_update_comment(await find_comment_id(), process_compile_output());
  } catch (error) {
    core.setFailed(error.message);
  }
}

main();


function debug_log(log){
  if(core.getInput("debug_output")) {
    console.log(log);
  }
}

// Switch from '\' to '/' so it makes comparing directories universal
function make_dir_universal(line){
  return line.split("\\").join("/");
}

// Returns true if 'line' doesn't start with excluded directory. Return false otherwise
function check_for_exclude_dir(line, exclude_dir) {
  return (exclude_dir.length == 0) || (line.indexOf(exclude_dir) != 0);
}

// Checks whether 'line' is warning/error line
function check_if_valid_line(compiler, line){
  const error_word = compiler != "MSVC" ? "error:" : "error C";
  const warning_word = compiler != "MSVC" ? "warning:" : "warning C";

  return line.indexOf(warning_word) != -1 || line.indexOf(error_word) != -1;
}

// Return type of the issue present in 'line'
function get_issue_type(compiler, line){
  // This function is called after check_if_valid_line, so it's guaranteed that
  // 'line' is warning or error description
  const warning_word = compiler != "MSVC" ? "warning:" : "warning C";

  return line.indexOf(warning_word) != -1 ? "warning" : "error";
}

function get_line_end(file_path, line_start) {
  work_dir = process.env.GITHUB_WORKSPACE;
  file = fs.readFileSync(work_dir + file_path).toString('utf-8');
  num_lines = (file.split(/\r?\n/)).length - 1;

  return Math.min(num_lines, line_start + parseInt(core.getInput("num_lines_to_display"))).toString();
}

function get_line_info(compiler, line) {
  const end_file_char = compiler != "MSVC" ? ":" : "(";
  const file_line_end_char = compiler != "MSVC" ? ":" : ",";

  file_path_end_idx = line.indexOf(end_file_char);
  const file_name_offset = file_path_end_idx + 1;
  file_line_start = line.substring(file_name_offset, file_name_offset + line.substring(file_name_offset).indexOf(file_line_end_char));

  // Special case for MSVC
  if(isNaN(parseInt(file_line_start))){
    if(compiler == "MSVC"){
      file_line_start = line.substring(file_name_offset, file_name_offset + line.substring(file_name_offset).indexOf(")"));
    }
  }

  file_path = line.substring(0, file_path_end_idx);
  file_line_end = get_line_end(file_path, file_line_start);

  return [file_path, file_line_start, file_line_end, get_issue_type(compiler, line)];
}

function process_compile_output() {
  compile_result = fs.readFileSync(core.getInput('compile_result_file')).toString('utf-8');
  const prefix_dir =  make_dir_universal(core.getInput('work_dir'));
  const exclude_dir = make_dir_universal(core.getInput('exclude_dir'));
  const compiler = core.getInput('compiler');
  var num_warnings = 0;
  var num_errors = 0;

  const splitLines = str => str.split(/\r?\n/);
  debug_log(`Initial lines: ${splitLines}`);
  var matchingStrings = [];
  arrayOfLines = [...new Set(splitLines(compile_result))];
  debug_log(`arrayOfLines: ${arrayOfLines}`);
  arrayOfLines.forEach(line => {
    line = make_dir_universal(line);
    var idx = line.indexOf(prefix_dir);

    // Only consider lines that start with 'prefix_dir'
    if (idx == 0 && check_for_exclude_dir(line, exclude_dir) && check_if_valid_line(compiler, line)) {
      debug_log(`Parsing line: ${line}`);
      line = line.replace(prefix_dir, "");

      const [file_path, file_line_start, file_line_end, type] = get_line_info(compiler, line);

      // warning/error description
      const color_mark = type == "error" ? "-" : "!";
      type == "error" ? num_errors++ : num_warnings++;
      description = "\n```diff\n" + `${color_mark}Line: ${file_line_start} ` + line.substring(line.indexOf(" ")) + "\n```\n";

      // Concatinate both modified path to file and the description
      var link_with_description = `\nhttps://github.com/${github.context.issue.owner}/${github.context.issue.repo}` +
        `/blob/${github.context.sha}/${file_path}#L${file_line_start}-L${file_line_end} ${description} </br>\n`;

      matchingStrings.push(link_with_description);
    }
  });

  if (matchingStrings.length == 0) {
    return `<p align="center"><b> :white_check_mark: ${core.getInput("comment_title")} - SUCCESS! :white_check_mark: </b></p>`
  }else{
    return `<details> <summary> <b> ${core.getInput("comment_title")} - \
    :warning: Warnings( ${num_warnings} ) :x: Errors( ${num_errors} ) </b> </summary>\r\n${matchingStrings.join('\n')} </details>`;
  }

}

function findCommentPredicate(comment) {
  return comment.user.login == "github-actions[bot]" && comment.body.includes(core.getInput("comment_title"));
}

async function find_comment_id() {
  const octokit = github.getOctokit(core.getInput("token"));

  const parameters = {
    owner: github.context.issue.owner,
    repo: github.context.issue.repo,
    issue_number: core.getInput("pull_request_number")
  };

  for await (const { data: comments } of octokit.paginate.iterator(
    octokit.issues.listComments,
    parameters
  )) {
    // Search each page for the comment
    const comment = comments.find(comment =>
      findCommentPredicate(comment)
    )
    if (comment) {
      console.log(`Found comment! ID=${comment.id} user-login:${comment.user.login}`);
      return comment.id;
    }
  };

  return -1;
}

async function create_or_update_comment(comment_id, comment_body) {
  const octokit = github.getOctokit(core.getInput("token"));

  // Create comment
  if (comment_id == -1) {
    console.log(`Adding new comment`);
    await octokit.issues.createComment({
      owner: github.context.issue.owner,
      repo: github.context.issue.repo,
      issue_number: core.getInput("pull_request_number"),
      body: comment_body,
    });
  }
  // Update comment
  else {
    console.log(`Updating comment with ID=${comment_id} `);
    await octokit.issues.updateComment({
      owner: github.context.issue.owner,
      repo: github.context.issue.repo,
      comment_id: comment_id,
      body: comment_body,
    });
  }
}

})();

module.exports = __webpack_exports__;
/******/ })()
;