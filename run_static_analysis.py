import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import argparse
from github import Github
import os

# Get file name from user
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help='Output file name', required=True)
graph_file_name = parser.parse_args().output

# Input variables from Github action
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')
REPO_NAME = os.getenv('INPUT_REPO')
WORKFLOW_NAME = os.getenv('INPUT_WORKFLOW')
BRANCH_NAME = os.getenv('INPUT_BRANCH')
REQUESTED_N_LAST_BUILDS = int(os.getenv('INPUT_NUM_LAST_BUILD'))
GRAPH_TITLE = os.getenv('INPUT_TITLE', '')
X_LABEL = os.getenv('INPUT_X_LABEL')
Y_LABEL = os.getenv('INPUT_Y_LABEL')
GRAPH_WIDTH = float(os.getenv('INPUT_GRAPH_WIDTH'))
GRAPH_HEIGHT = float(os.getenv('INPUT_GRAPH_HEIGHT'))

print(f'Repo={REPO_NAME} Workflow={WORKFLOW_NAME}')

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
workflow = repo.get_workflow(id_or_name=WORKFLOW_NAME)

# Data to be plotted
timings = []
run_nums = []
dates = []

workflow_runs = workflow.get_runs(status="success", branch=BRANCH_NAME)

print(f'workflow_runs.totalCount={workflow_runs.totalCount} and requested_last_runs={REQUESTED_N_LAST_BUILDS}')

last_n_runs = min(REQUESTED_N_LAST_BUILDS, workflow_runs.totalCount)

print(f'last_n_runs={last_n_runs}')

for run in workflow_runs[:last_n_runs]:
    run_timing = run.timing()
    print(f"run_number:{run.run_number} created at:{run.created_at} took:{run_timing.run_duration_ms}ms")

    # Convert ms to min
    timings.append(run_timing.run_duration_ms / 60000.0)
    dates.append(run.created_at)
    run_nums.append(run.run_number)

#dates = matplotlib.dates.date2num(run_nums)
#matplotlib.pyplot.plot_date(dates, values)

SMALL_SIZE = 15
MEDIUM_SIZE = 25
BIGGER_SIZE = 35

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)    # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rc('font', family='serif')           # font family

# plot
plt.style.use('seaborn')

fig, (ax1, ax2) = plt.subplots(figsize=(GRAPH_WIDTH, GRAPH_HEIGHT), nrows=2, ncols=1)


#plt.plot_date(dates, timings, color='b')
ax1.plot(dates, timings, color='b')
ax2.plot(run_nums, timings, color='b')
#plt.plot(run_nums, timings, color='b')

#plt.gcf().autofmt_xdate()

plt.title(GRAPH_TITLE)
plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)

plt.savefig(graph_file_name)
