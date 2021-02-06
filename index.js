const core = require('@actions/core');
const github = require('@actions/github');
//const FileReader = require('filereader');

try {
  // `who-to-greet` input defined in action metadata file
  const result_in = core.getInput('compile_result');
  // const repo = core.getInput('repo');
  // const run_id = core.getInput('run_id');
  console.log(`Going with ${result_in}!`);

  	// Do something with your data
  // 	console.log(data);
  // });
  //reader.readAsText(files[0]);
  //const time = (new Date()).toTimeString();
  // GET https://api.github.com/repos/<org>/<repo>/check-suites/<check_suite_id>/check-runs
  // Get workflow_id
  // https://api.github.com/repos/JacobDomagala/DGame/actions/workflows
  // Get all run_id for given workflow
  // https://api.github.com/repos/JacobDomagala/DGame/actions/workflows/2745476/runs
  // const result = await request('GET /repos/{owner}/{repo}/actions/runs/{run_id}/runs', {
  //   owner: owner,
  //   repo: repo,
  //   run_id: run_id
  // })
  //console.log(`Run duration=${result.data.run_duration_ms}`)
  core.setOutput("time", 0);
} catch (error) {
  core.setFailed(error.message);
}
