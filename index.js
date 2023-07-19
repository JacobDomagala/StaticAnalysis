const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');

async function main() {
  const eventType = process.env.GITHUB_EVENT_NAME;
  if (eventType === 'pull_request') {
    try {
      await create_or_update_comment(await find_comment_id(), process_compile_output());
    } catch (error) {
      core.setFailed(error.message);
    }
  } else {
    console.log(`This action can only run on 'pull_request' event! Currently running on ${eventType}. Skipping!`);
  }
}

if (require.main === module) {
  main();
}


/**
 * Logs a message to the console if debug output is enabled.
 *
 * @param {string} log - The message to log to the console.
 */
function debug_log(log) {
  // Check if debug output is enabled
  if (core.getInput("debug_output")) {
    // Log the message to the console
    console.log(log);
  }
}

/**
 * Replaces backslashes with forward slashes in a given directory path to make it compatible with all operating systems.
 *
 * @param {string} line - The directory path to convert.
 * @returns {string} - The converted directory path.
 */
function make_dir_universal(line) {
  // Split the directory path by backslashes and rejoin with forward slashes
  return line.split("\\").join("/");
}

/**
 * Checks if a given line contains an excluded directory.
 *
 * @param {string} line - The line to check.
 * @param {string} exclude_dir - The excluded directory to check for.
 * @returns {boolean} - True if the line does not contain the excluded directory, false otherwise.
 */
function check_for_exclude_dir(line, exclude_dir) {
  return exclude_dir.length === 0 || line.indexOf(exclude_dir) !== 0;
}

/**
 * Checks if a given line is a valid error or warning message.
 *
 * @param {string} compiler - The name of the compiler used to generate the message.
 * @param {string} line - The line to check.
 * @returns {boolean} - True if the line contains a valid error or warning message, false otherwise.
 */
function check_if_valid_line(compiler, line) {
  // Determine the error and warning keywords based on the compiler
  const error_word = compiler !== "MSVC" ? "error:" : "error C";
  const warning_word = compiler !== "MSVC" ? "warning:" : "warning C";

  // Check if the line contains an error or warning keyword
  const has_warning = line.indexOf(warning_word) !== -1;
  const has_error = line.indexOf(error_word) !== -1;

  // Return true if the line contains an error or warning keyword, false otherwise
  return has_warning || has_error;
}

/**
 * Determines the type of issue (error or warning) based on the compiler and message content.
 *
 * @param {string} compiler - The name of the compiler used to generate the message.
 * @param {string} line - The line containing the error or warning message.
 * @returns {string} - The type of issue, either "error" or "warning".
 */
function get_issue_type(compiler, line) {
  // Determine the warning keyword based on the compiler
  const warning_word = compiler !== "MSVC" ? "warning:" : "warning C";

  // Check if the line contains the warning keyword
  const is_warning = line.indexOf(warning_word) !== -1;

  // Return "warning" if the line contains the warning keyword, "error" otherwise
  return is_warning ? "warning" : "error";
}

/**
 * Returns the ending line number for a given file and starting line number.
 *
 * @param {string} file_path - The path to the file.
 * @param {string} line_start - The starting line number.
 * @returns {string} - The ending line number.
 */
function get_line_end(file_path, line_start) {
  // Get the current working directory where the file is located
  const work_dir = process.env.GITHUB_WORKSPACE;

  // Read the file and convert it to a string
  const file = fs.readFileSync(work_dir + file_path).toString('utf-8');

  // Count the number of lines in the file
  const num_lines = file.split(/\r?\n/).length - 1;

  // Calculate the ending line number based on the starting line number and the number of lines to display
  const num_lines_to_display = parseInt(core.getInput("num_lines_to_display"));
  const line_end = Math.min(num_lines, parseInt(line_start) + num_lines_to_display).toString();

  // Return the ending line number as a string
  return line_end;
}

/**
 * Extracts information about a line of code from a compiler error message.
 *
 * @param {string} compiler - The name of the compiler that produced the error message.
 * @param {string} line - The line of code in the error message.
 * @returns {Array} - An array containing the file path, starting line number, ending line number, and issue type.
 */
function get_line_info(compiler, line) {
  // Determine the characters used to separate the file path and line number in the error message
  const end_file_char = compiler !== "MSVC" ? ":" : "(";
  const file_line_end_char = compiler !== "MSVC" ? ":" : ",";

  // Find the index of the character that separates the file path and line number
  const file_path_end_idx = line.indexOf(end_file_char);

  // Extract the file path from the error message
  const file_path = line.substring(0, file_path_end_idx);

  // Extract the starting line number from the error message
  const file_name_offset = file_path_end_idx + 1;
  let file_line_start = line.substring(file_name_offset, file_name_offset + line.substring(file_name_offset).indexOf(file_line_end_char));

  // Special case for MSVC: if the starting line number is not a valid integer, extract it differently
  if (compiler === "MSVC" && isNaN(parseInt(file_line_start))) {
    file_line_start = line.substring(file_name_offset, file_name_offset + line.substring(file_name_offset).indexOf(")"));
  }

  // Use the starting line number to determine the ending line number
  const file_line_end = get_line_end(file_path, file_line_start);

  // Determine the type of issue indicated by the error message
  const issue_type = get_issue_type(compiler, line);

  // Return an array containing the extracted information
  return [file_path, file_line_start, file_line_end, issue_type];
}

/**
 * Parses the compile result file and generates a comment body with links to the files and
 * lines that caused warnings and errors.
 *
 * @returns {string} The comment body.
 */
function process_compile_output() {
  compile_result = fs.readFileSync(core.getInput('compile_result_file')).toString('utf-8');
  const prefix_dir = make_dir_universal(core.getInput('work_dir'));
  const exclude_dir = make_dir_universal(core.getInput('exclude_dir'));
  const compiler = core.getInput('compiler');
  var num_warnings = 0;
  var num_errors = 0;

  const splitLines = str => str.split(/\r?\n/);
  inistialList = splitLines(compile_result)
  inistialList.forEach(function (part, index) {
    this[index] = this[index].split("\\").join("/");
  }, inistialList);

  var matchingStrings = [];
  uniqueLines = [...new Set(inistialList)];
  debug_log(`Original string:\n ${compile_result} \n\n inistialList:\n ${splitLines(compile_result)} \n\n uniqueLines:\n ${uniqueLines}\n\n`);

  uniqueLines.forEach(line => {
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
      var link_with_description = `\n` + core.getInput('server_url') + `/${github.context.issue.owner}/${github.context.issue.repo}` +
        `/blob/${github.context.sha}/${file_path}#L${file_line_start}-L${file_line_end} ${description} </br>\n`;

      matchingStrings.push(link_with_description);
    }
  });

  if (matchingStrings.length == 0) {
    return `<p align="center"><b> :white_check_mark: ${core.getInput("comment_title")} - SUCCESS! :white_check_mark: </b></p>`
  } else {
    return `<details> <summary> <b> ${core.getInput("comment_title")} - \
    :warning: Warnings( ${num_warnings} ) :x: Errors( ${num_errors} ) </b> </summary>\r\n${matchingStrings.join('\n')} </details>`;
  }

}

/**
 * Returns a predicate function to find a specific comment on a GitHub pull request.
 *
 * @param {Object} comment - The comment object to check against.
 * @returns {boolean} - Whether the comment was created by the GitHub Actions bot and contains the specified title.
 */
function findCommentPredicate(comment) {
  // Check if the comment was created by the GitHub Actions bot
  const is_actions_bot = comment.user.login === "github-actions[bot]";

  // Check if the comment body contains the specified title
  const has_title = comment.body.includes(core.getInput("comment_title"));

  // Return true if both conditions are met, false otherwise
  return is_actions_bot && has_title;
}

/**
 * Searches for a specific comment associated with the current pull request.
 * @returns {Promise<number>} - The ID of the comment if it exists, otherwise -1.
 */
async function find_comment_id() {
  const octokit = github.getOctokit(core.getInput("token"));

  // Define the parameters for the request to list comments
  const parameters = {
    owner: github.context.issue.owner,
    repo: github.context.issue.repo,
    issue_number: core.getInput("pull_request_number")
  };

  // Iterate through all pages of comments until the desired comment is found
  for await (const { data: comments } of octokit.paginate.iterator(
    octokit.issues.listComments,
    parameters
  )) {
    // Search each page of comments for the desired comment
    const comment = comments.find(comment =>
      findCommentPredicate(comment)
    )
    if (comment) {
      console.log(`Found comment! ID=${comment.id} user-login:${comment.user.login}`);
      return comment.id;
    }
  };

  // If the comment was not found, return -1
  return -1;
}

/**
  Creates or updates a comment on a pull request.
  @async
  @param {number} comment_id - The ID of the comment to update, or -1 to create a new comment.
  @param {string} comment_body - The body of the comment.
  @returns {Promise<void>} - A promise that resolves when the comment has been created or updated.
*/
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
    console.log(`Updating comment with ID=${comment_id}`);
    await octokit.issues.updateComment({
      owner: github.context.issue.owner,
      repo: github.context.issue.repo,
      comment_id: comment_id,
      body: comment_body,
    });
  }
}


module.exports = {
  make_dir_universal,
  check_for_exclude_dir,
  check_if_valid_line,
  get_issue_type,
  get_line_end,
  get_line_info,
  process_compile_output,
};
