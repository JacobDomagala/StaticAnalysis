const core = require('@actions/core');
const github = require('@actions/github');
var fs = require("fs");

async function main() {
  try {
    //const result_in = core.getInput('compile_result');
    await create_or_update_comment(await find_comment_id(), process_compile_output());
  } catch (error) {
    core.setFailed(error.message);
  }
}

main();

function check_for_exclude_dir(line, prefix, exclude_dir) {
   if(exclude_dir.length == 0) {
     return true;
   }

   // substring(1) is here to skip file delimiter it can be either / or \
   return line.replace(prefix, "").substring(1).indexOf(exclude_dir) != 0;
}

function check_if_valid_line(compiler, line){
  var error_word = "error:";
  var warning_word = "warning:";

  if(compiler == "MSVC"){
    error_word = "error C";
    warning_word = "warning C"
  }

  return line.indexOf(warning_word) != -1 || line.indexOf(error_word) != -1;
}

function get_line_info(compiler, line) {
  var end_file_char = ":";
  var file_line_end_char = ":";

  if(compiler == "MSVC"){
    end_file_char = "(";
    file_line_end_char = ",";
  }

  file_path_end_idx = line.indexOf(end_file_char);
  const file_name_offset = file_path_end_idx + 1;
  file_line_start = line.substring(file_name_offset, file_name_offset + line.substring(file_name_offset).indexOf(file_line_end_char));
  file_line_end = (parseInt(file_line_start) + parseInt(core.getInput("num_lines_to_display"))).toString();
  file_path = line.substring(0, file_path_end_idx).split("\\").join("/");

  return [file_path, file_line_start, file_line_end];
}

function process_compile_output() {
  compile_result = fs.readFileSync(core.getInput('compile_result_file')).toString('utf-8');
  console.log(`compile result = ${compile_result}`);
  const prefix =  core.getInput('work_dir');
  const exclude_dir = core.getInput('exclude_dir');
  const compiler = core.getInput('compiler');

  const splitLines = str => str.split(/\r?\n/);
  var matchingStrings = [];
  arrayOfLines = splitLines(compile_result);
  arrayOfLines.forEach(line => {
    var idx = line.indexOf(prefix);

    // Only consider lines that start with 'prefix'
    if (idx == 0 && check_for_exclude_dir(line, prefix, exclude_dir) && check_if_valid_line(compiler, line)) {
      str = line.replace(prefix, "");

      const [file_path, file_line_start, file_line_end] = get_line_info(compiler, str);

      // warning/error description
      description = "\n```diff\n" + `-Line: ${file_line_start} ` + str.substring(str.indexOf(" ")) + "\n```\n";

      // Concatinate both modified path to file and the description
      var link_with_description = `\nhttps://github.com/${github.context.issue.owner}/${github.context.issue.repo}` +
        `/blob/${github.context.sha}/${file_path}#L${file_line_start}-L${file_line_end} ${description} </br>\n`;

      matchingStrings.push(link_with_description);
    }
  });

  if (matchingStrings.length == 0) {
    return `<b> ${core.getInput("comment_title")} - SUCCESS! </b>`
  }else{
    return `<details> <summary> <b> ${core.getInput("comment_title")} </b> </summary>\r\n${matchingStrings.join('\n')} </details>`;
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
