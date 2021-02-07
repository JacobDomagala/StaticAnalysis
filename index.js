const core = require('@actions/core');
const github = require('@actions/github');

try {
  const result_in = core.getInput('compile_result');
  gitsha = github.context.sha;

  console.log(`GIT SHA = ${gitsha}`);

  const processed_out = process_compile_output(result_in);
  const comment_id = find_comment_id();
  if (comment_id != -1) {
    update_comment(comment_id, processed_out);
  } else {
    create_new_comment(processed_out);
  }
  core.setOutput("time", 0);
} catch (error) {
  core.setFailed(error.message);
}

function process_compile_output(compile_result) {
  const str_begin_len = "/home/runner/work/DGame/".length;
  const splitLines = str => str.split(/\r?\n/);
  var matchingStrings = [];
  arrayOfLines = splitLines(compile_result);
  arrayOfLines.forEach(item => {
    var idx = item.indexOf("/home/runner/work/DGame/");
    if (idx == 0) {
      end_str = item.indexOf(":");
      sub_str = item.substring(str_begin_len, end_str);

      var new_line = `https://github.com/JacobDomagala/DGame/blob/${gitsha}/${sub_str}`;
      matchingStrings.push(new_line);
    }
  });

  matchingStrings.forEach(item => console.log(item));

  return matchingStrings;
}

function find_comment_id() {
  return -1;
}

function create_new_comment(comment_body) {

}

function update_comment(comment_id, comment_body) {

}