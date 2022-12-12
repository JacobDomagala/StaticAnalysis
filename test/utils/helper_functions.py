def generate_comment(comment_title, issues_found, tool_name):
    expected_comment_body = (
        f'## <p align="center"><b> :zap: {comment_title} :zap: </b></p> \n\n'
        f"<details> <summary> <b> :red_circle: {tool_name} found "
        f"{issues_found} {'issues' if issues_found > 1 else 'issue'}!"
        " Click here to see details. </b> </summary> <br>"
        " dummy comment </details>"
    )

    if tool_name == "cppcheck":
        expected_comment_body += "\n\n *** \n"
    else:
        expected_comment_body +="<br>\n"

    return expected_comment_body


