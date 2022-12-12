def generate_comment(comment_title, content, issues_found, tool_name):
    if issues_found == 0:
        return (
            '## <p align="center"><b> :white_check_mark:'
            f"{comment_title} - no issues found! :white_check_mark: </b></p>"
        )

    expected_comment_body = (
        f'## <p align="center"><b> :zap: {comment_title} :zap: </b></p> \n\n'
    )
    if tool_name == "clang-tidy":
        expected_comment_body += "\n\n *** \n"

    expected_comment_body += (
        f"<details> <summary> <b> :red_circle: {tool_name} found "
        f"{issues_found} {'issues' if issues_found > 1 else 'issue'}!"
        " Click here to see details. </b> </summary> <br>"
        f"{content} </details>"
    )

    if tool_name == "cppcheck":
        expected_comment_body += "\n\n *** \n"
    else:
        expected_comment_body += "<br>\n"

    return expected_comment_body
